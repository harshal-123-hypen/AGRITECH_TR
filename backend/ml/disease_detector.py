import cv2
import numpy as np
from PIL import Image
import io
import base64
import logging

logger = logging.getLogger(__name__)

DISEASE_PATTERNS = {
    "leaf_spot": {
        "color_range": [(35, 40, 40), (85, 255, 255)],
        "description": "Bacterial/Fungal Leaf Spot",
        "confidence_boost": 1.0
    },
    "rust": {
        "color_range": [(0, 100, 100), (20, 255, 255)],
        "description": "Crop Rust Disease",
        "confidence_boost": 0.85
    },
    "powdery_mildew": {
        "color_range": [(0, 0, 200), (255, 30, 255)],
        "description": "Powdery Mildew",
        "confidence_boost": 0.9
    },
    "blight": {
        "color_range": [(80, 50, 50), (100, 200, 200)],
        "description": "Late Blight/Early Blight",
        "confidence_boost": 0.95
    },
    "healthy": {
        "color_range": [(35, 40, 40), (90, 255, 255)],
        "description": "Healthy Crop",
        "confidence_boost": 1.0
    }
}

TREATMENT_RECOMMENDATIONS = {
    "leaf_spot": "Apply copper-based fungicides. Improve air circulation. Remove infected leaves.",
    "rust": "Use sulfur-based fungicides. Ensure proper spacing between plants. Remove infected debris.",
    "powdery_mildew": "Apply baking soda spray (1 tbsp per gallon). Use sulfur fungicides. Increase air circulation.",
    "blight": "Remove infected plants immediately. Apply systematic fungicides. Improve drainage.",
    "healthy": "Continue regular maintenance. Monitor for signs of disease. Apply preventive sprays if needed."
}

class DiseaseDetector:
    def __init__(self):
        self.disease_patterns = DISEASE_PATTERNS
        self.treatments = TREATMENT_RECOMMENDATIONS
    
    def preprocess_image(self, image_base64: str) -> np.ndarray:
        """Preprocess base64 image for analysis"""
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            resized = cv2.resize(image_cv, (256, 256))
            
            return resized
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise ValueError("Invalid image data")
    
    def detect_disease(self, image_array: np.ndarray) -> dict:
        """Detect disease using image analysis"""
        hsv = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
        
        disease_scores = {}
        
        for disease_name, pattern in self.disease_patterns.items():
            lower = np.array(pattern["color_range"][0])
            upper = np.array(pattern["color_range"][1])
            
            mask = cv2.inRange(hsv, lower, upper)
            affected_pixels = np.count_nonzero(mask)
            total_pixels = hsv.shape[0] * hsv.shape[1]
            affected_percentage = (affected_pixels / total_pixels) * 100
            
            confidence = min(affected_percentage / 100, 1.0) * pattern["confidence_boost"]
            disease_scores[disease_name] = {
                "confidence": confidence,
                "affected_percentage": affected_percentage
            }
        
        detected_disease = max(disease_scores, key=lambda x: disease_scores[x]["confidence"])
        confidence_score = disease_scores[detected_disease]["confidence"]
        
        if confidence_score < 0.2:
            detected_disease = "healthy"
            confidence_score = 0.95
        
        return {
            "disease": detected_disease,
            "confidence": float(confidence_score),
            "description": self.disease_patterns[detected_disease]["description"],
            "all_scores": disease_scores
        }
    
    def get_severity_level(self, confidence: float, affected_percentage: float) -> str:
        """Determine severity level of disease"""
        if confidence < 0.3:
            return "healthy"
        elif confidence < 0.5:
            return "minor"
        elif confidence < 0.75:
            return "moderate"
        else:
            return "severe"
    
    def predict(self, image_base64: str) -> dict:
        """Full prediction pipeline"""
        image_array = self.preprocess_image(image_base64)
        detection = self.detect_disease(image_array)
        
        disease_name = detection["disease"]
        confidence = detection["confidence"]
        affected_percentage = detection["all_scores"][disease_name]["affected_percentage"]
        
        severity = self.get_severity_level(confidence, affected_percentage)
        treatment = self.treatments.get(disease_name, "Consult local agricultural expert")
        
        return {
            "disease": disease_name,
            "description": detection["description"],
            "confidence": confidence,
            "severity": severity,
            "affected_percentage": affected_percentage,
            "treatment": treatment,
            "recommendations": self._get_recommendations(disease_name, severity)
        }
    
    def _get_recommendations(self, disease: str, severity: str) -> list:
        """Get specific recommendations based on disease and severity"""
        base_recommendations = {
            "leaf_spot": [
                "Isolate affected plants to prevent spread",
                "Apply fungicide every 7-10 days",
                "Ensure proper plant spacing for air circulation",
                "Remove infected leaves and dispose safely",
                "Water at soil level, avoid wetting leaves"
            ],
            "rust": [
                "Remove alternate hosts nearby",
                "Apply sulfur or copper fungicides",
                "Improve drainage and air circulation",
                "Monitor weather for high humidity",
                "Use resistant varieties for next season"
            ],
            "powdery_mildew": [
                "Apply baking soda spray",
                "Increase air circulation in field",
                "Remove heavily infected leaves",
                "Apply neem oil spray",
                "Monitor regularly for recurrence"
            ],
            "blight": [
                "URGENT: Remove and destroy affected plants",
                "Apply systematic fungicides immediately",
                "Quarantine affected area",
                "Improve drainage",
                "Avoid overhead irrigation"
            ],
            "healthy": [
                "Continue regular monitoring",
                "Maintain proper irrigation schedule",
                "Apply preventive fungicides periodically",
                "Ensure good soil nutrition",
                "Rotate crops next season"
            ]
        }
        
        recommendations = base_recommendations.get(disease, [])
        
        if severity == "severe":
            recommendations = [f"PRIORITY: {r}" for r in recommendations[:3]] + recommendations[3:]
        
        return recommendations
