"""
Machine Learning Model for Vital Risk Assessment
Uses LightGBM for risk prediction from vital signs trends
"""
import logging
import os
import pickle
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import LightGBM (optional dependency)
try:
    import lightgbm as lgb
    import numpy as np
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("LightGBM not available. ML model features will be disabled.")


class VitalRiskMLModel:
    """LightGBM model for vital risk prediction"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.model_path = Path(__file__).parent / "models" / "vital_risk_model.pkl"
    
    def load_model(self) -> bool:
        """Load the trained LightGBM model"""
        if not LIGHTGBM_AVAILABLE:
            logger.warning("LightGBM not available. Cannot load ML model.")
            return False
        
        # Check if model file exists
        if not self.model_path.exists():
            logger.warning(f"Model file not found: {self.model_path}. Using rule-based only.")
            return False
        
        try:
            logger.info(f"Loading ML model from {self.model_path}")
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.model_loaded = True
            logger.info("ML model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading ML model: {str(e)}")
            self.model_loaded = False
            return False
    
    def predict_risk(
        self,
        vitals_data: list,
        patient_age: Optional[int] = None,
        patient_sex: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Predict risk score from vital signs data
        
        Args:
            vitals_data: List of vital readings
            patient_age: Patient age
            patient_sex: Patient sex
            
        Returns:
            Risk prediction dict with score, level, and explanation
        """
        if not self.model_loaded:
            if not self.load_model():
                return None  # Return None if model can't be loaded
        
        try:
            # Extract features from vitals
            features = self._extract_features(vitals_data, patient_age, patient_sex)
            
            # Predict risk score
            risk_score = self.model.predict([features])[0]
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Generate explanation
            explanation = self._generate_explanation(features, risk_score, risk_level)
            
            return {
                "score": float(risk_score),
                "risk_level": risk_level,
                "explanation": explanation,
                "source": "ml_model"
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {str(e)}")
            return None
    
    def _extract_features(self, vitals_data: list, age: Optional[int], sex: Optional[str]) -> list:
        """Extract features from vital signs for model input"""
        if not vitals_data:
            return [0.0] * 20  # Return zero features if no data
        
        # Sort by timestamp (most recent first)
        sorted_vitals = sorted(vitals_data, key=lambda v: v.get('timestamp', ''), reverse=True)
        latest = sorted_vitals[0] if sorted_vitals else {}
        
        # Calculate trends (if multiple readings)
        if len(sorted_vitals) > 1:
            # Trend over last 3 readings
            recent = sorted_vitals[:3]
            hr_trend = (recent[0].get('hr', 0) - recent[-1].get('hr', 0)) / len(recent) if len(recent) > 1 else 0
            bp_trend = (recent[0].get('bp_sys', 0) - recent[-1].get('bp_sys', 0)) / len(recent) if len(recent) > 1 else 0
        else:
            hr_trend = 0
            bp_trend = 0
        
        # Extract features (adjust based on your trained model)
        features = [
            latest.get('hr', 0) or 0,
            latest.get('bp_sys', 0) or 0,
            latest.get('bp_dia', 0) or 0,
            latest.get('spo2', 0) or 0,
            latest.get('rr', 0) or 0,
            latest.get('temp', 0) or 0,
            latest.get('pain', 0) or 0,
            hr_trend,
            bp_trend,
            age or 0,
            1.0 if sex == 'M' else 0.0,  # Binary encoding
            # Add more features as needed
        ]
        
        # Pad to expected feature count (adjust based on your model)
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]  # Ensure exactly 20 features
    
    def _generate_explanation(self, features: list, score: float, level: str) -> str:
        """Generate explanation for ML model prediction"""
        explanations = []
        
        hr = features[0] if len(features) > 0 else 0
        bp_sys = features[1] if len(features) > 1 else 0
        spo2 = features[3] if len(features) > 3 else 0
        
        if hr > 100:
            explanations.append(f"elevated heart rate ({hr:.0f} bpm)")
        if bp_sys > 140:
            explanations.append(f"elevated blood pressure ({bp_sys:.0f} mmHg)")
        if spo2 < 95:
            explanations.append(f"low oxygen saturation ({spo2:.1f}%)")
        
        if explanations:
            return f"ML model identified: {', '.join(explanations)}. Risk score: {score:.2f}."
        else:
            return f"ML model risk assessment: {level} risk (score: {score:.2f})."


# Global instance (lazy loaded)
_ml_model_instance: Optional[VitalRiskMLModel] = None


def get_ml_model() -> Optional[VitalRiskMLModel]:
    """Get or create the ML model instance"""
    global _ml_model_instance
    
    if _ml_model_instance is None:
        _ml_model_instance = VitalRiskMLModel()
    
    return _ml_model_instance


def predict_ml_risk(
    vitals_data: list,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Predict risk using ML model (wrapper function)"""
    ml_model = get_ml_model()
    if ml_model:
        return ml_model.predict_risk(vitals_data, patient_age, patient_sex)
    return None

