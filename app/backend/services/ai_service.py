"""
AI Service Client
Routes requests to appropriate AI model services and handles responses
"""
import httpx
import logging
from typing import Optional, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)

# Timeout for AI service calls (in seconds)
# Increased to 120 seconds to allow for AI model loading (first request can take 30-60 seconds)
AI_SERVICE_TIMEOUT = 120.0


class AIServiceClient:
    """Client for communicating with AI model services"""
    
    def __init__(self):
        self.vital_risk_url = settings.VITAL_RISK_SERVICE_URL
        self.image_analysis_url = settings.IMAGE_ANALYSIS_SERVICE_URL
        self.diagnosis_helper_url = settings.DIAGNOSIS_HELPER_SERVICE_URL
    
    async def predict_vital_risk(
        self,
        patient_id: str,
        vitals: list
    ) -> Optional[Dict[str, Any]]:
        """
        Route request to vital risk model service
        
        Args:
            patient_id: Patient ID
            vitals: List of vital readings
            
        Returns:
            Response from vital risk service or None if error
        """
        try:
            async with httpx.AsyncClient(timeout=AI_SERVICE_TIMEOUT) as client:
                response = await client.post(
                    f"{self.vital_risk_url}/predict",
                    json={
                        "patient_id": patient_id,
                        "vitals": vitals
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling vital risk service for patient {patient_id}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling vital risk service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error calling vital risk service: {str(e)}", exc_info=True)
            return None
    
    async def analyze_image(
        self,
        image_id: str,
        image_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Route request to image analysis model service
        
        Args:
            image_id: Image ID
            image_type: Type of image (X-ray, MRI, CT)
            
        Returns:
            Response from image analysis service or None if error
        """
        try:
            async with httpx.AsyncClient(timeout=AI_SERVICE_TIMEOUT) as client:
                response = await client.post(
                    f"{self.image_analysis_url}/analyze",
                    json={
                        "image_id": image_id,
                        "image_type": image_type
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling image analysis service for image {image_id}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling image analysis service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error calling image analysis service: {str(e)}", exc_info=True)
            return None
    
    async def suggest_diagnosis(
        self,
        patient_id: str,
        patient_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Route request to diagnosis helper service
        
        Args:
            patient_id: Patient ID
            patient_data: Patient data including vitals, labs, diagnoses
            
        Returns:
            Response from diagnosis helper service or None if error
        """
        try:
            async with httpx.AsyncClient(timeout=AI_SERVICE_TIMEOUT) as client:
                response = await client.post(
                    f"{self.diagnosis_helper_url}/suggest",
                    json={
                        "patient_id": patient_id,
                        **patient_data
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling diagnosis helper service for patient {patient_id}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling diagnosis helper service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error calling diagnosis helper service: {str(e)}", exc_info=True)
            return None


# Global instance
ai_service_client = AIServiceClient()

