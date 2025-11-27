"""
Logging utilities for structured logging and PHI validation
"""
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StructuredLogger:
    """Utility for structured logging with PHI validation"""
    
    # Common PHI patterns (simplified - in production use proper PHI detection)
    PHI_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Date of birth
        r'\b\d{3}-\d{3}-\d{4}\b',  # Phone number
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
    ]
    
    @staticmethod
    def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize data to remove potential PHI before logging.
        Returns a sanitized copy of the data.
        """
        sanitized = {}
        for key, value in data.items():
            # Skip certain keys that might contain PHI
            if key.lower() in ['name', 'patient_name', 'email', 'address', 'phone', 'ssn', 'dob']:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str):
                # Check for PHI patterns in strings
                sanitized_value = value
                for pattern in StructuredLogger.PHI_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        sanitized_value = re.sub(pattern, "[REDACTED]", sanitized_value)
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = StructuredLogger.sanitize_for_logging(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    StructuredLogger.sanitize_for_logging(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def log_user_action(
        action_type: str,
        user_id: str,
        patient_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        level: str = "INFO"
    ):
        """
        Log a user action with structured format.
        Automatically sanitizes metadata to prevent PHI leakage.
        """
        log_data = {
            "event_type": "user_action",
            "action_type": action_type,
            "user_id": user_id,
            "patient_id": patient_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": StructuredLogger.sanitize_for_logging(metadata or {}),
        }
        
        log_message = f"User action: {action_type} by user {user_id}"
        if patient_id:
            log_message += f" for patient {patient_id}"
        
        if level.upper() == "INFO":
            logger.info(log_message, extra={"structured_data": log_data})
        elif level.upper() == "WARNING":
            logger.warning(log_message, extra={"structured_data": log_data})
        elif level.upper() == "ERROR":
            logger.error(log_message, extra={"structured_data": log_data})
        else:
            logger.debug(log_message, extra={"structured_data": log_data})
    
    @staticmethod
    def log_ai_suggestion(
        suggestion_id: str,
        patient_id: str,
        suggestion_type: str,
        source: str,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log AI suggestion creation with structured format.
        """
        log_data = {
            "event_type": "ai_suggestion",
            "suggestion_id": suggestion_id,
            "patient_id": patient_id,
            "suggestion_type": suggestion_type,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": StructuredLogger.sanitize_for_logging(metadata or {}),
        }
        
        log_message = f"AI suggestion created: {suggestion_type} from {source} for patient {patient_id}"
        if confidence is not None:
            log_message += f" (confidence: {confidence:.2f})"
        
        logger.info(log_message, extra={"structured_data": log_data})
    
    @staticmethod
    def log_adaptation(
        adaptation_id: str,
        user_id: str,
        patient_id: Optional[str] = None,
        plan_type: str = "ui_layout",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log system adaptation with structured format.
        """
        log_data = {
            "event_type": "system_adaptation",
            "adaptation_id": adaptation_id,
            "user_id": user_id,
            "patient_id": patient_id,
            "plan_type": plan_type,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": StructuredLogger.sanitize_for_logging(metadata or {}),
        }
        
        log_message = f"System adaptation: {plan_type} for user {user_id}"
        if patient_id:
            log_message += f" (patient: {patient_id})"
        
        logger.info(log_message, extra={"structured_data": log_data})
    
    @staticmethod
    def log_model_output(
        model_type: str,
        model_version: str,
        patient_id: Optional[str] = None,
        output_summary: Optional[Dict[str, Any]] = None,
    ):
        """
        Log AI model output with structured format.
        Only logs summary, not full output to avoid PHI.
        """
        log_data = {
            "event_type": "model_output",
            "model_type": model_type,
            "model_version": model_version,
            "patient_id": patient_id,
            "timestamp": datetime.utcnow().isoformat(),
            "output_summary": StructuredLogger.sanitize_for_logging(output_summary or {}),
        }
        
        log_message = f"Model output: {model_type} v{model_version}"
        if patient_id:
            log_message += f" for patient {patient_id}"
        
        logger.info(log_message, extra={"structured_data": log_data})

