"""
CNN Model for Medical Image Analysis
Uses CheXNet (DenseNet-121) for chest X-ray analysis
"""
import logging
import os
from typing import Tuple, Optional
from pathlib import Path
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Try to import torch (required for CNN)
try:
    import torch
    import torchvision
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. CNN model features will be disabled.")


class CheXNetModel:
    """CheXNet model for chest X-ray analysis"""
    
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self) -> bool:
        """Load CheXNet model (DenseNet-121)"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available. Cannot load CNN model.")
            return False
        
        try:
            logger.info("Loading CheXNet model...")
            
            # Load DenseNet-121 (base for CheXNet)
            self.model = models.densenet121(pretrained=False)
            num_ftrs = self.model.classifier.in_features
            self.model.classifier = nn.Linear(num_ftrs, 14)  # 14 classes for ChestX-ray14
            
            # Try to load pretrained weights (if available)
            model_path = Path(__file__).parent / "models" / "chexnet.pth"
            if model_path.exists():
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info("Loaded pretrained CheXNet weights")
            else:
                logger.warning("Pretrained weights not found. Using randomly initialized model.")
            
            self.model = self.model.to(self.device)
            self.model.eval()
            self.model_loaded = True
            
            logger.info(f"CheXNet model loaded on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CheXNet model: {str(e)}")
            self.model_loaded = False
            return False
    
    def analyze_image(
        self,
        image_data: bytes,
        image_type: str
    ) -> Optional[Tuple[float, str, Optional[str], str]]:
        """
        Analyze medical image using CNN
        
        Args:
            image_data: Image bytes
            image_type: Type of image (X-ray, MRI, CT)
            
        Returns:
            Tuple of (abnormality_score, classification, heatmap_url, explanation)
        """
        if not self.model_loaded:
            if not self.load_model():
                return None
        
        # Only analyze chest X-rays for now
        if image_type.lower() not in ["chest_xray", "x-ray", "xray", "chest x-ray"]:
            logger.info(f"CNN model only supports chest X-rays, not {image_type}")
            return None
        
        try:
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.sigmoid(outputs).cpu().numpy()[0]
            
            # Get top abnormality
            abnormality_classes = [
                "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
                "Mass", "Nodule", "Pneumonia", "Pneumothorax", "Consolidation",
                "Edema", "Emphysema", "Fibrosis", "Pleural_Thickening", "Hernia"
            ]
            
            max_prob = float(probabilities.max())
            max_idx = int(probabilities.argmax())
            classification = abnormality_classes[max_idx] if max_idx < len(abnormality_classes) else "Normal"
            
            # Generate explanation
            explanation = f"CNN model (CheXNet) detected {classification} with {max_prob:.1%} confidence. This is an experimental AI analysis."
            
            return (max_prob, classification, None, explanation)
            
        except Exception as e:
            logger.error(f"Error in CNN image analysis: {str(e)}")
            return None


# Global instance (lazy loaded)
_cnn_model_instance: Optional[CheXNetModel] = None


def get_cnn_model() -> Optional[CheXNetModel]:
    """Get or create the CNN model instance"""
    global _cnn_model_instance
    
    if _cnn_model_instance is None:
        _cnn_model_instance = CheXNetModel()
    
    return _cnn_model_instance


def analyze_image_cnn(
    image_data: bytes,
    image_type: str
) -> Optional[Tuple[float, str, Optional[str], str]]:
    """Analyze image using CNN (wrapper function)"""
    cnn_model = get_cnn_model()
    if cnn_model:
        return cnn_model.analyze_image(image_data, image_type)
    return None

