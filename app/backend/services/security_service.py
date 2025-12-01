"""
Security Service - Threat Detection & Mitigation

Implements security mechanisms for FL and adaptation systems:
- Anomaly detection on client updates (FL poisoning)
- Gradient clipping (prevent model inversion)
- Continuous monitoring
- Alert system

Part of Phase 7: Privacy, Security & Governance
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import logging
import math
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)

# Security thresholds
GRADIENT_MAX_NORM = 1.0  # Maximum L2 norm for gradients
ANOMALY_Z_SCORE_THRESHOLD = 3.0  # Z-score threshold for anomaly detection
MIN_SAMPLES_FOR_BASELINE = 10  # Minimum samples needed for baseline
POISONING_VOTE_THRESHOLD = 0.3  # Fraction of updates flagged = poisoning attack
RATE_LIMIT_WINDOW_MINUTES = 5
RATE_LIMIT_MAX_REQUESTS = 100


class SecurityService:
    """
    Security service for detecting and mitigating threats.
    
    Key Capabilities:
    1. FL Poisoning Detection - Identify malicious client updates
    2. Gradient Clipping - Prevent model inversion attacks
    3. Rate Limiting - Prevent DoS attacks
    4. Anomaly Detection - Identify unusual patterns
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._baseline_stats: Dict[str, Dict] = {}  # Cache for baseline statistics
    
    # =========================================================================
    # FL Poisoning Detection
    # =========================================================================
    
    def detect_poisoning(
        self,
        client_updates: List[Dict[str, Any]],
        global_model: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Detect potential FL poisoning attacks.
        
        Checks for:
        1. Gradient magnitude anomalies
        2. Direction divergence from consensus
        3. Statistical outliers
        4. Sudden distribution shifts
        
        Args:
            client_updates: List of client update dictionaries
            global_model: Current global model for comparison
        
        Returns:
            Detection results with flagged clients
        """
        if len(client_updates) < 3:
            return {
                "poisoning_detected": False,
                "reason": "Insufficient updates for analysis",
                "flagged_clients": [],
                "confidence": 0.0
            }
        
        flagged_clients = []
        detection_scores = []
        
        # Extract gradients/weights from updates
        gradients = []
        client_ids = []
        
        for update in client_updates:
            client_id = update.get("client_id", "unknown")
            weights = update.get("weight_updates", {})
            
            if not weights:
                continue
            
            # Flatten weights to vector
            flat_weights = self._flatten_weights(weights)
            gradients.append(flat_weights)
            client_ids.append(client_id)
        
        if len(gradients) < 3:
            return {
                "poisoning_detected": False,
                "reason": "Insufficient valid gradients",
                "flagged_clients": [],
                "confidence": 0.0
            }
        
        # Calculate baseline (median for robustness)
        baseline = self._calculate_robust_baseline(gradients)
        
        # Check each client's update
        for i, (gradient, client_id) in enumerate(zip(gradients, client_ids)):
            # 1. Magnitude check
            magnitude = self._vector_norm(gradient)
            magnitude_score = self._check_magnitude_anomaly(magnitude, gradients)
            
            # 2. Direction check (cosine similarity with consensus)
            direction_score = self._check_direction_anomaly(gradient, baseline)
            
            # 3. Statistical outlier check
            outlier_score = self._check_statistical_outlier(gradient, gradients)
            
            # Combine scores
            combined_score = (
                0.4 * magnitude_score +
                0.4 * direction_score +
                0.2 * outlier_score
            )
            
            detection_scores.append(combined_score)
            
            if combined_score > 0.7:
                flagged_clients.append({
                    "client_id": client_id,
                    "score": round(combined_score, 3),
                    "magnitude_score": round(magnitude_score, 3),
                    "direction_score": round(direction_score, 3),
                    "outlier_score": round(outlier_score, 3),
                    "reason": self._get_flag_reason(magnitude_score, direction_score, outlier_score)
                })
        
        # Determine if attack is happening
        flagged_fraction = len(flagged_clients) / len(client_ids)
        poisoning_detected = flagged_fraction > 0 and flagged_fraction < POISONING_VOTE_THRESHOLD
        
        # If too many are flagged, might be a coordinated attack or false positive
        if flagged_fraction >= POISONING_VOTE_THRESHOLD:
            logger.warning(
                f"High fraction of clients flagged ({flagged_fraction:.1%}). "
                "Possible coordinated attack or baseline drift."
            )
        
        return {
            "poisoning_detected": poisoning_detected,
            "flagged_clients": flagged_clients,
            "flagged_fraction": round(flagged_fraction, 3),
            "total_clients": len(client_ids),
            "confidence": round(1 - min(0.5, abs(flagged_fraction - POISONING_VOTE_THRESHOLD)), 3),
            "recommendation": self._get_poisoning_recommendation(flagged_clients, flagged_fraction)
        }
    
    def _flatten_weights(self, weights: Dict[str, Any]) -> List[float]:
        """Flatten nested weight dictionary to vector."""
        flat = []
        
        def _flatten(obj):
            if isinstance(obj, (int, float)):
                flat.append(float(obj))
            elif isinstance(obj, list):
                for item in obj:
                    _flatten(item)
            elif isinstance(obj, dict):
                for value in obj.values():
                    _flatten(value)
        
        _flatten(weights)
        return flat if flat else [0.0]
    
    def _vector_norm(self, vector: List[float]) -> float:
        """Calculate L2 norm of vector."""
        return math.sqrt(sum(x * x for x in vector))
    
    def _calculate_robust_baseline(self, gradients: List[List[float]]) -> List[float]:
        """Calculate robust baseline using coordinate-wise median."""
        if not gradients:
            return []
        
        # Pad to same length
        max_len = max(len(g) for g in gradients)
        padded = [g + [0.0] * (max_len - len(g)) for g in gradients]
        
        # Calculate coordinate-wise median
        baseline = []
        for i in range(max_len):
            values = sorted([g[i] for g in padded])
            mid = len(values) // 2
            if len(values) % 2 == 0:
                median = (values[mid - 1] + values[mid]) / 2
            else:
                median = values[mid]
            baseline.append(median)
        
        return baseline
    
    def _check_magnitude_anomaly(
        self,
        magnitude: float,
        all_gradients: List[List[float]]
    ) -> float:
        """Check if gradient magnitude is anomalous."""
        magnitudes = [self._vector_norm(g) for g in all_gradients]
        
        mean_mag = sum(magnitudes) / len(magnitudes)
        std_mag = math.sqrt(sum((m - mean_mag) ** 2 for m in magnitudes) / len(magnitudes))
        
        if std_mag < 1e-10:
            return 0.0
        
        z_score = abs(magnitude - mean_mag) / std_mag
        
        # Normalize to 0-1 score
        return min(1.0, z_score / ANOMALY_Z_SCORE_THRESHOLD)
    
    def _check_direction_anomaly(
        self,
        gradient: List[float],
        baseline: List[float]
    ) -> float:
        """Check if gradient direction diverges from baseline."""
        if not gradient or not baseline:
            return 0.0
        
        # Pad to same length
        max_len = max(len(gradient), len(baseline))
        g = gradient + [0.0] * (max_len - len(gradient))
        b = baseline + [0.0] * (max_len - len(baseline))
        
        # Cosine similarity
        dot_product = sum(g[i] * b[i] for i in range(max_len))
        norm_g = self._vector_norm(g)
        norm_b = self._vector_norm(b)
        
        if norm_g < 1e-10 or norm_b < 1e-10:
            return 0.0
        
        cosine_sim = dot_product / (norm_g * norm_b)
        
        # Convert to anomaly score (lower similarity = higher anomaly)
        return max(0.0, (1 - cosine_sim) / 2)
    
    def _check_statistical_outlier(
        self,
        gradient: List[float],
        all_gradients: List[List[float]]
    ) -> float:
        """Check if gradient is a statistical outlier."""
        if len(all_gradients) < 3:
            return 0.0
        
        # Use sum of absolute values as simple statistic
        stats = [sum(abs(x) for x in g) for g in all_gradients]
        current_stat = sum(abs(x) for x in gradient)
        
        mean_stat = sum(stats) / len(stats)
        std_stat = math.sqrt(sum((s - mean_stat) ** 2 for s in stats) / len(stats))
        
        if std_stat < 1e-10:
            return 0.0
        
        z_score = abs(current_stat - mean_stat) / std_stat
        
        return min(1.0, z_score / ANOMALY_Z_SCORE_THRESHOLD)
    
    def _get_flag_reason(
        self,
        magnitude_score: float,
        direction_score: float,
        outlier_score: float
    ) -> str:
        """Generate human-readable reason for flagging."""
        reasons = []
        
        if magnitude_score > 0.7:
            reasons.append("abnormal gradient magnitude")
        if direction_score > 0.7:
            reasons.append("divergent update direction")
        if outlier_score > 0.7:
            reasons.append("statistical outlier")
        
        return ", ".join(reasons) if reasons else "combined anomaly score exceeded threshold"
    
    def _get_poisoning_recommendation(
        self,
        flagged_clients: List[Dict],
        flagged_fraction: float
    ) -> str:
        """Generate recommendation based on detection results."""
        if not flagged_clients:
            return "No action needed - all updates appear legitimate"
        
        if flagged_fraction < 0.1:
            return "Exclude flagged client(s) from aggregation"
        elif flagged_fraction < POISONING_VOTE_THRESHOLD:
            return "Review flagged clients and consider temporary exclusion"
        else:
            return "High anomaly rate - consider postponing aggregation and investigating"
    
    # =========================================================================
    # Gradient Clipping
    # =========================================================================
    
    def clip_gradients(
        self,
        gradients: Dict[str, Any],
        max_norm: float = GRADIENT_MAX_NORM
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Clip gradients to prevent model inversion attacks.
        
        Args:
            gradients: Gradient dictionary
            max_norm: Maximum L2 norm
        
        Returns:
            Tuple of (clipped gradients, was_clipped flag)
        """
        flat_gradients = self._flatten_weights(gradients)
        current_norm = self._vector_norm(flat_gradients)
        
        if current_norm <= max_norm:
            return gradients, False
        
        # Scale factor
        scale = max_norm / current_norm
        
        # Apply scaling to all values
        clipped = self._scale_gradients(gradients, scale)
        
        logger.info(
            f"Clipped gradients: norm {current_norm:.4f} -> {max_norm:.4f} "
            f"(scale: {scale:.4f})"
        )
        
        return clipped, True
    
    def _scale_gradients(self, obj: Any, scale: float) -> Any:
        """Recursively scale gradient values."""
        if isinstance(obj, (int, float)):
            return obj * scale
        elif isinstance(obj, list):
            return [self._scale_gradients(item, scale) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._scale_gradients(value, scale) for key, value in obj.items()}
        else:
            return obj
    
    def clip_and_add_noise(
        self,
        gradients: Dict[str, Any],
        max_norm: float = GRADIENT_MAX_NORM,
        noise_multiplier: float = 0.1
    ) -> Dict[str, Any]:
        """
        Clip gradients and add Gaussian noise for differential privacy.
        
        This implements DP-SGD (Differentially Private SGD).
        
        Args:
            gradients: Gradient dictionary
            max_norm: Maximum L2 norm for clipping
            noise_multiplier: Noise scale relative to max_norm
        
        Returns:
            Clipped and noised gradients
        """
        import random
        
        # First clip
        clipped, _ = self.clip_gradients(gradients, max_norm)
        
        # Then add noise
        noise_scale = max_norm * noise_multiplier
        
        def add_noise(obj):
            if isinstance(obj, (int, float)):
                return obj + random.gauss(0, noise_scale)
            elif isinstance(obj, list):
                return [add_noise(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: add_noise(value) for key, value in obj.items()}
            else:
                return obj
        
        noised = add_noise(clipped)
        
        return noised
    
    # =========================================================================
    # Rate Limiting
    # =========================================================================
    
    def check_rate_limit(
        self,
        client_id: str,
        action: str,
        window_minutes: int = RATE_LIMIT_WINDOW_MINUTES,
        max_requests: int = RATE_LIMIT_MAX_REQUESTS
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Client identifier
            action: Action being rate limited
            window_minutes: Time window for counting
            max_requests: Maximum requests allowed
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        try:
            from sqlalchemy import text
            
            window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
            
            # Count recent requests
            query = text("""
                SELECT COUNT(*) FROM rate_limit_log
                WHERE client_id = :client_id
                  AND action = :action
                  AND timestamp > :window_start
            """)
            
            count = self.db.execute(query, {
                "client_id": client_id,
                "action": action,
                "window_start": window_start
            }).scalar() or 0
            
            is_allowed = count < max_requests
            
            # Log this request if allowed
            if is_allowed:
                log_query = text("""
                    INSERT INTO rate_limit_log (client_id, action, timestamp)
                    VALUES (:client_id, :action, :timestamp)
                """)
                self.db.execute(log_query, {
                    "client_id": client_id,
                    "action": action,
                    "timestamp": datetime.utcnow()
                })
                self.db.commit()
            
            return is_allowed, {
                "client_id": client_id,
                "action": action,
                "requests_in_window": count,
                "max_requests": max_requests,
                "window_minutes": window_minutes,
                "is_allowed": is_allowed,
                "retry_after_seconds": 0 if is_allowed else window_minutes * 60
            }
            
        except Exception as e:
            logger.warning(f"Rate limit check failed (allowing request): {e}")
            return True, {"error": str(e), "is_allowed": True}
    
    # =========================================================================
    # Anomaly Detection
    # =========================================================================
    
    def detect_behavioral_anomaly(
        self,
        user_id: UUID,
        current_behavior: Dict[str, float],
        behavior_type: str = "usage"
    ) -> Dict[str, Any]:
        """
        Detect anomalous user behavior.
        
        Args:
            user_id: User to analyze
            current_behavior: Current behavior metrics
            behavior_type: Type of behavior being analyzed
        
        Returns:
            Anomaly detection results
        """
        # Get baseline for user
        baseline = self._get_user_baseline(user_id, behavior_type)
        
        if not baseline:
            # No baseline yet, establish one
            self._update_user_baseline(user_id, behavior_type, current_behavior)
            return {
                "anomaly_detected": False,
                "reason": "No baseline established yet",
                "baseline_updated": True
            }
        
        # Check each metric
        anomalies = []
        for metric, value in current_behavior.items():
            if metric in baseline:
                baseline_mean = baseline[metric].get("mean", value)
                baseline_std = baseline[metric].get("std", 1.0)
                
                if baseline_std > 0:
                    z_score = abs(value - baseline_mean) / baseline_std
                    
                    if z_score > ANOMALY_Z_SCORE_THRESHOLD:
                        anomalies.append({
                            "metric": metric,
                            "value": value,
                            "expected": baseline_mean,
                            "z_score": round(z_score, 2)
                        })
        
        # Update baseline with current behavior (exponential moving average)
        self._update_user_baseline(user_id, behavior_type, current_behavior)
        
        return {
            "anomaly_detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "metrics_checked": len(current_behavior),
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def _get_user_baseline(
        self,
        user_id: UUID,
        behavior_type: str
    ) -> Optional[Dict[str, Dict]]:
        """Get stored baseline for user."""
        cache_key = f"{user_id}:{behavior_type}"
        
        if cache_key in self._baseline_stats:
            return self._baseline_stats[cache_key]
        
        # Try to load from database
        try:
            from sqlalchemy import text
            
            query = text("""
                SELECT baseline_data FROM user_baselines
                WHERE user_id = :user_id AND behavior_type = :behavior_type
            """)
            
            result = self.db.execute(query, {
                "user_id": user_id,
                "behavior_type": behavior_type
            }).fetchone()
            
            if result:
                import json
                baseline = json.loads(result[0]) if isinstance(result[0], str) else result[0]
                self._baseline_stats[cache_key] = baseline
                return baseline
                
        except Exception as e:
            logger.warning(f"Error loading user baseline: {e}")
        
        return None
    
    def _update_user_baseline(
        self,
        user_id: UUID,
        behavior_type: str,
        current_behavior: Dict[str, float],
        alpha: float = 0.1  # EMA smoothing factor
    ) -> None:
        """Update user baseline using exponential moving average."""
        cache_key = f"{user_id}:{behavior_type}"
        baseline = self._baseline_stats.get(cache_key, {})
        
        for metric, value in current_behavior.items():
            if metric not in baseline:
                baseline[metric] = {"mean": value, "std": 1.0, "count": 1}
            else:
                old_mean = baseline[metric]["mean"]
                old_std = baseline[metric]["std"]
                count = baseline[metric]["count"]
                
                # Update mean with EMA
                new_mean = alpha * value + (1 - alpha) * old_mean
                
                # Update std (simplified)
                diff = abs(value - new_mean)
                new_std = alpha * diff + (1 - alpha) * old_std
                
                baseline[metric] = {
                    "mean": new_mean,
                    "std": max(0.1, new_std),  # Minimum std to avoid division by zero
                    "count": count + 1
                }
        
        self._baseline_stats[cache_key] = baseline
        
        # Persist to database periodically
        if baseline.get(list(current_behavior.keys())[0], {}).get("count", 0) % 10 == 0:
            self._persist_baseline(user_id, behavior_type, baseline)
    
    def _persist_baseline(
        self,
        user_id: UUID,
        behavior_type: str,
        baseline: Dict
    ) -> None:
        """Persist baseline to database."""
        try:
            import json
            from sqlalchemy import text
            
            query = text("""
                INSERT INTO user_baselines (user_id, behavior_type, baseline_data, updated_at)
                VALUES (:user_id, :behavior_type, :baseline_data, :updated_at)
                ON CONFLICT (user_id, behavior_type)
                DO UPDATE SET baseline_data = :baseline_data, updated_at = :updated_at
            """)
            
            self.db.execute(query, {
                "user_id": user_id,
                "behavior_type": behavior_type,
                "baseline_data": json.dumps(baseline),
                "updated_at": datetime.utcnow()
            })
            self.db.commit()
            
        except Exception as e:
            logger.warning(f"Error persisting baseline: {e}")
            self.db.rollback()
    
    # =========================================================================
    # Security Alerts
    # =========================================================================
    
    def create_security_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        details: Dict[str, Any] = None,
        affected_entity: str = None
    ) -> Dict[str, Any]:
        """
        Create a security alert.
        
        Args:
            alert_type: Type of alert (poisoning, anomaly, rate_limit, etc.)
            severity: Alert severity (low, medium, high, critical)
            description: Human-readable description
            details: Additional details
            affected_entity: Entity affected (client_id, user_id, etc.)
        
        Returns:
            Created alert
        """
        try:
            import json
            from sqlalchemy import text
            
            alert_id = str(UUID(int=int(datetime.utcnow().timestamp() * 1000000)))
            
            query = text("""
                INSERT INTO security_alerts 
                (id, alert_type, severity, description, details, affected_entity, created_at, status)
                VALUES (:id, :alert_type, :severity, :description, :details, :affected_entity, :created_at, 'open')
            """)
            
            self.db.execute(query, {
                "id": alert_id,
                "alert_type": alert_type,
                "severity": severity,
                "description": description,
                "details": json.dumps(details or {}),
                "affected_entity": affected_entity,
                "created_at": datetime.utcnow()
            })
            self.db.commit()
            
            alert = {
                "id": alert_id,
                "alert_type": alert_type,
                "severity": severity,
                "description": description,
                "details": details,
                "affected_entity": affected_entity,
                "created_at": datetime.utcnow().isoformat(),
                "status": "open"
            }
            
            # Log high-severity alerts
            if severity in ("high", "critical"):
                logger.warning(f"SECURITY ALERT [{severity.upper()}]: {alert_type} - {description}")
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating security alert: {e}")
            return {"error": str(e)}
    
    def get_open_alerts(
        self,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get open security alerts."""
        try:
            from sqlalchemy import text
            
            if severity:
                query = text("""
                    SELECT * FROM security_alerts
                    WHERE status = 'open' AND severity = :severity
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                result = self.db.execute(query, {"severity": severity, "limit": limit})
            else:
                query = text("""
                    SELECT * FROM security_alerts
                    WHERE status = 'open'
                    ORDER BY 
                        CASE severity 
                            WHEN 'critical' THEN 1 
                            WHEN 'high' THEN 2 
                            WHEN 'medium' THEN 3 
                            ELSE 4 
                        END,
                        created_at DESC
                    LIMIT :limit
                """)
                result = self.db.execute(query, {"limit": limit})
            
            alerts = []
            for row in result:
                alerts.append(dict(row._mapping))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []


def get_security_service(db: Session) -> SecurityService:
    """Get security service instance."""
    return SecurityService(db)

