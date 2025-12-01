"""
Federated Learning Service
Implements FedAvg and coordination for privacy-preserving multi-site learning
"""
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime
import logging
import hashlib
import json

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from models.federated_learning import (
    FLRound,
    FLClientUpdate,
    FLGlobalModel,
    FLClient,
)

logger = logging.getLogger(__name__)


class FederatedLearningService:
    """
    Core federated learning coordinator service.
    
    Implements FedAvg (Federated Averaging) algorithm:
    1. Distribute global model to clients
    2. Clients train locally on their data
    3. Clients send weight updates (not raw data)
    4. Coordinator aggregates updates (weighted average)
    5. Update global model
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def start_round(
        self,
        model_type: str,
        global_model_version: str,
        aggregation_method: str = "fedavg",
    ) -> FLRound:
        """
        Start a new federated learning round.
        
        Args:
            model_type: Type of model ('vital_risk', 'adaptation_policy', etc.)
            global_model_version: Version identifier for this round
            aggregation_method: Aggregation algorithm ('fedavg', 'dual_aggregated', etc.)
        
        Returns:
            FLRound instance
        """
        # Get next round number
        last_round = self.db.query(func.max(FLRound.round_number)).filter(
            FLRound.model_type == model_type
        ).scalar()
        
        round_number = (last_round or 0) + 1
        
        # Create round
        fl_round = FLRound(
            round_number=round_number,
            model_type=model_type,
            global_model_version=global_model_version,
            aggregation_method=aggregation_method,
            status="in_progress",
        )
        
        self.db.add(fl_round)
        self.db.commit()
        self.db.refresh(fl_round)
        
        logger.info(f"Started FL round {round_number} for {model_type}")
        
        return fl_round
    
    def submit_client_update(
        self,
        round_id: UUID,
        client_id: str,
        weight_updates: Dict[str, Any],
        sample_count: int,
        training_loss: Optional[float] = None,
        validation_loss: Optional[float] = None,
        signature: Optional[str] = None,
    ) -> FLClientUpdate:
        """
        Submit weight updates from a client.
        
        Args:
            round_id: FL round ID
            client_id: Client identifier
            weight_updates: Model weight deltas (not raw data)
            sample_count: Number of samples used in training
            training_loss: Local training loss
            validation_loss: Local validation loss
            signature: Digital signature for verification
        
        Returns:
            FLClientUpdate instance
        """
        # Verify round exists and is active
        fl_round = self.db.query(FLRound).filter(FLRound.id == round_id).first()
        if not fl_round:
            raise ValueError(f"FL round {round_id} not found")
        
        if fl_round.status != "in_progress":
            raise ValueError(f"FL round {round_id} is not in progress")
        
        # Hash weight updates for verification
        weights_json = json.dumps(weight_updates, sort_keys=True)
        weights_hash = hashlib.sha256(weights_json.encode()).hexdigest()
        
        # Get or create client
        client = self.db.query(FLClient).filter(FLClient.client_id == client_id).first()
        if not client:
            client = FLClient(
                client_id=client_id,
                client_type="site",  # Default
            )
            self.db.add(client)
        
        # Create update
        update = FLClientUpdate(
            round_id=round_id,
            client_id=client_id,
            client_type=client.client_type,
            model_weights_hash=weights_hash,
            sample_count=sample_count,
            training_loss=training_loss,
            validation_loss=validation_loss,
            weight_updates=weight_updates,
            signature=signature,
            status="pending",
        )
        
        self.db.add(update)
        
        # Update client participation
        client.last_participation = datetime.utcnow()
        client.participation_count += 1
        
        # Update round statistics
        fl_round.participant_count += 1
        fl_round.total_samples += sample_count
        
        self.db.commit()
        self.db.refresh(update)
        
        logger.info(
            f"Received update from {client_id} for round {fl_round.round_number}: "
            f"{sample_count} samples"
        )
        
        return update
    
    def aggregate_updates(
        self,
        round_id: UUID,
        min_participants: int = 3,
    ) -> Dict[str, Any]:
        """
        Aggregate client updates using FedAvg (Federated Averaging).
        
        Args:
            round_id: FL round ID
            min_participants: Minimum number of participants required
        
        Returns:
            Aggregated model weights
        """
        # Get round
        fl_round = self.db.query(FLRound).filter(FLRound.id == round_id).first()
        if not fl_round:
            raise ValueError(f"FL round {round_id} not found")
        
        # Get all pending updates
        updates = self.db.query(FLClientUpdate).filter(
            and_(
                FLClientUpdate.round_id == round_id,
                FLClientUpdate.status == "pending",
            )
        ).all()
        
        if len(updates) < min_participants:
            raise ValueError(
                f"Not enough participants: {len(updates)} < {min_participants}"
            )
        
        # Calculate total samples
        total_samples = sum(update.sample_count for update in updates)
        
        if total_samples == 0:
            raise ValueError("Total samples is zero")
        
        # Aggregate using weighted average (FedAvg)
        aggregated_weights = self._federated_average(updates, total_samples)
        
        # Mark updates as aggregated
        for update in updates:
            update.status = "aggregated"
        
        # Complete round
        fl_round.status = "completed"
        fl_round.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(
            f"Aggregated {len(updates)} updates for round {fl_round.round_number}, "
            f"total samples: {total_samples}"
        )
        
        return {
            "aggregated_weights": aggregated_weights,
            "participant_count": len(updates),
            "total_samples": total_samples,
            "round_number": fl_round.round_number,
        }
    
    def _federated_average(
        self,
        updates: List[FLClientUpdate],
        total_samples: int,
    ) -> Dict[str, Any]:
        """
        Federated Averaging: Weighted average of client updates.
        
        Formula: w_global = Σ(n_i / n_total * w_i)
        where n_i is samples from client i, n_total is total samples
        """
        aggregated = {}
        
        for update in updates:
            weight = update.sample_count / total_samples
            
            if not update.weight_updates:
                logger.warning(f"Update {update.id} has no weight_updates")
                continue
            
            for key, value in update.weight_updates.items():
                if key not in aggregated:
                    # Initialize with zero structure matching value
                    if isinstance(value, dict):
                        aggregated[key] = {k: 0.0 for k in value.keys()}
                    elif isinstance(value, (list, tuple)):
                        aggregated[key] = [0.0] * len(value)
                    else:
                        aggregated[key] = 0.0
                
                # Weighted sum
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        aggregated[key][sub_key] = aggregated[key].get(sub_key, 0.0) + weight * sub_value
                elif isinstance(value, (list, tuple)):
                    for i, sub_value in enumerate(value):
                        aggregated[key][i] = aggregated[key][i] + weight * sub_value
                else:
                    aggregated[key] = aggregated[key] + weight * value
        
        return aggregated
    
    def save_global_model(
        self,
        round_id: UUID,
        model_weights: Dict[str, Any],
        performance_metrics: Optional[Dict[str, float]] = None,
    ) -> FLGlobalModel:
        """
        Save aggregated model as new global model version.
        
        Args:
            round_id: FL round ID
            model_weights: Aggregated model weights
            performance_metrics: Optional performance metrics
        
        Returns:
            FLGlobalModel instance
        """
        # Get round
        fl_round = self.db.query(FLRound).filter(FLRound.id == round_id).first()
        if not fl_round:
            raise ValueError(f"FL round {round_id} not found")
        
        # Hash weights
        weights_json = json.dumps(model_weights, sort_keys=True)
        weights_hash = hashlib.sha256(weights_json.encode()).hexdigest()
        
        # Generate version
        version = f"{fl_round.model_type}_v{fl_round.round_number}_{weights_hash[:8]}"
        
        # Deactivate previous active model
        previous_active = self.db.query(FLGlobalModel).filter(
            and_(
                FLGlobalModel.model_type == fl_round.model_type,
                FLGlobalModel.is_active == "true",
            )
        ).all()
        
        for model in previous_active:
            model.is_active = "false"
        
        # Create new global model
        global_model = FLGlobalModel(
            round_id=round_id,
            model_type=fl_round.model_type,
            version=version,
            model_weights=model_weights,
            model_weights_hash=weights_hash,
            global_accuracy=performance_metrics.get("accuracy") if performance_metrics else None,
            global_loss=performance_metrics.get("loss") if performance_metrics else None,
            test_accuracy=performance_metrics.get("test_accuracy") if performance_metrics else None,
            aggregation_method=fl_round.aggregation_method,
            participant_count=fl_round.participant_count,
            total_samples=fl_round.total_samples,
            is_active="true",
        )
        
        self.db.add(global_model)
        self.db.commit()
        self.db.refresh(global_model)
        
        logger.info(f"Saved global model {version} for {fl_round.model_type}")
        
        return global_model
    
    def get_latest_global_model(
        self,
        model_type: str,
    ) -> Optional[FLGlobalModel]:
        """
        Get the latest active global model for a model type.
        
        Args:
            model_type: Type of model
        
        Returns:
            FLGlobalModel instance or None
        """
        model = self.db.query(FLGlobalModel).filter(
            and_(
                FLGlobalModel.model_type == model_type,
                FLGlobalModel.is_active == "true",
            )
        ).order_by(FLGlobalModel.created_at.desc()).first()
        
        return model
    
    def register_client(
        self,
        client_id: str,
        client_name: Optional[str] = None,
        client_type: str = "site",
        public_key: Optional[str] = None,
    ) -> FLClient:
        """
        Register a new FL client (site/department).
        
        Args:
            client_id: Unique client identifier
            client_name: Human-readable name
            client_type: Type of client ('site', 'department', 'user_group')
            public_key: Public key for signature verification
        
        Returns:
            FLClient instance
        """
        # Check if client exists
        existing = self.db.query(FLClient).filter(FLClient.client_id == client_id).first()
        if existing:
            # Update existing
            if client_name:
                existing.client_name = client_name
            if public_key:
                existing.public_key = public_key
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # Create new client
        client = FLClient(
            client_id=client_id,
            client_name=client_name or client_id,
            client_type=client_type,
            public_key=public_key,
        )
        
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        
        logger.info(f"Registered FL client: {client_id}")
        
        return client
    
    def get_round_status(
        self,
        round_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get status of an FL round.
        
        Returns:
            Dictionary with round status and statistics
        """
        round_obj = self.db.query(FLRound).filter(FLRound.id == round_id).first()
        if not round_obj:
            raise ValueError(f"FL round {round_id} not found")
        
        # Get updates
        updates = self.db.query(FLClientUpdate).filter(
            FLClientUpdate.round_id == round_id
        ).all()
        
        return {
            "round_id": str(round_id),
            "round_number": round_obj.round_number,
            "model_type": round_obj.model_type,
            "status": round_obj.status,
            "participant_count": round_obj.participant_count,
            "total_samples": round_obj.total_samples,
            "updates": [
                {
                    "client_id": u.client_id,
                    "sample_count": u.sample_count,
                    "status": u.status,
                    "sent_at": u.sent_at.isoformat() if u.sent_at else None,
                }
                for u in updates
            ],
            "started_at": round_obj.started_at.isoformat() if round_obj.started_at else None,
            "completed_at": round_obj.completed_at.isoformat() if round_obj.completed_at else None,
        }


def get_fl_service(db: Session) -> FederatedLearningService:
    """Factory function to get FederatedLearningService instance"""
    return FederatedLearningService(db)

