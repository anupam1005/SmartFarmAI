import numpy as np
import cv2
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CropHealthModel:
    """
    A simplified crop health analysis model that uses computer vision techniques
    to assess crop health from images.
    
    Note: This is a demonstration model that uses basic image processing instead of
    deep learning to avoid TensorFlow and GPU dependencies.
    """
    
    def __init__(self):
        """Initialize the crop health analysis model"""
        logger.info("Initializing Crop Health Analysis Model")
        self.initialized = True
    
    def analyze_image(self, image):
        """
        Analyze crop health from an image
        
        Args:
            image: Image as a numpy array (BGR format)
            
        Returns:
            Dictionary with health analysis results
        """
        if image is None:
            return {
                "success": False,
                "error": "No image provided"
            }
        
        try:
            # Convert BGR to HSV color space
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for healthy (green), stressed (yellow), and unhealthy (brown) vegetation
            # HSV ranges: (hue, saturation, value)
            green_lower = np.array([35, 40, 40])
            green_upper = np.array([90, 255, 255])
            
            yellow_lower = np.array([20, 40, 40])
            yellow_upper = np.array([35, 255, 255])
            
            brown_lower = np.array([0, 20, 20])
            brown_upper = np.array([20, 100, 100])
            
            # Create masks for each color range
            green_mask = cv2.inRange(hsv_image, green_lower, green_upper)
            yellow_mask = cv2.inRange(hsv_image, yellow_lower, yellow_upper)
            brown_mask = cv2.inRange(hsv_image, brown_lower, brown_upper)
            
            # Count pixels in each category
            green_pixels = np.sum(green_mask > 0)
            yellow_pixels = np.sum(yellow_mask > 0)
            brown_pixels = np.sum(brown_mask > 0)
            total_pixels = image.shape[0] * image.shape[1]
            
            # Calculate percentage of each category
            total_vegetation_pixels = green_pixels + yellow_pixels + brown_pixels
            
            # Avoid division by zero
            if total_vegetation_pixels == 0:
                return {
                    "success": False,
                    "error": "No vegetation detected in image"
                }
            
            green_percentage = (green_pixels / total_vegetation_pixels) * 100
            yellow_percentage = (yellow_pixels / total_vegetation_pixels) * 100
            brown_percentage = (brown_pixels / total_vegetation_pixels) * 100
            
            # Calculate vegetation coverage
            vegetation_coverage = (total_vegetation_pixels / total_pixels) * 100
            
            # Calculate a health score (weighted sum)
            health_score = (green_percentage * 1.0 + 
                           yellow_percentage * 0.5 + 
                           brown_percentage * 0.0)
            
            # Determine health status
            if health_score >= 80:
                health_status = "Healthy"
            elif health_score >= 60:
                health_status = "Moderate Stress"
            elif health_score >= 40:
                health_status = "Significant Stress"
            else:
                health_status = "Severe Stress"
            
            # Simple nutrient status estimation
            # In a real model, this would use more sophisticated analysis or additional sensors
            nutrient_status = self._estimate_nutrient_status(green_percentage, yellow_percentage, brown_percentage)
            
            # Generate analysis result
            result = {
                "success": True,
                "health_score": round(health_score, 1),
                "health_status": health_status,
                "vegetation_coverage": round(vegetation_coverage, 1),
                "green_percentage": round(green_percentage, 1),
                "yellow_percentage": round(yellow_percentage, 1),
                "brown_percentage": round(brown_percentage, 1),
                "nutrient_status": nutrient_status
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing crop health image: {e}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _estimate_nutrient_status(self, green_pct, yellow_pct, brown_pct):
        """
        Estimate nutrient status based on color percentages
        
        Args:
            green_pct: Percentage of green pixels
            yellow_pct: Percentage of yellow pixels
            brown_pct: Percentage of brown pixels
            
        Returns:
            Dictionary with nutrient status estimates
        """
        # In a real model, this would be based on more sophisticated analysis
        # For this demo, we'll use simplified rules
        
        # Nitrogen status based on overall greenness
        if green_pct >= 70:
            nitrogen = "Adequate"
        elif green_pct >= 50:
            nitrogen = "Slight Deficiency"
        else:
            nitrogen = "Deficient"
        
        # Phosphorus status based on purple/reddish coloration (simplified here)
        # In this simplified version, we'll randomize but with a bias based on health
        phosphorus_options = ["Adequate", "Slight Deficiency", "Deficient"]
        phosphorus_weights = [0.7, 0.2, 0.1] if green_pct > 60 else [0.3, 0.4, 0.3]
        phosphorus = random.choices(phosphorus_options, weights=phosphorus_weights)[0]
        
        # Potassium status based on yellowing of older leaves (simplified)
        if yellow_pct <= 15:
            potassium = "Adequate"
        elif yellow_pct <= 30:
            potassium = "Slight Deficiency"
        else:
            potassium = "Deficient"
        
        return {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium
        }
    
    def generate_recommendations(self, analysis_result):
        """
        Generate recommendations based on the crop health analysis
        
        Args:
            analysis_result: Analysis result from analyze_image method
            
        Returns:
            List of recommendation strings
        """
        if not analysis_result.get("success", False):
            return ["Unable to generate recommendations due to analysis failure."]
        
        recommendations = []
        
        # Health score based recommendations
        health_score = analysis_result.get("health_score", 0)
        
        if health_score < 50:
            recommendations.append("Immediate action recommended: Crop showing significant stress.")
        elif health_score < 70:
            recommendations.append("Monitor crop closely: Moderate stress detected.")
        
        # Nutrient recommendations
        nutrient_status = analysis_result.get("nutrient_status", {})
        
        if nutrient_status.get("nitrogen") == "Deficient":
            recommendations.append("Apply nitrogen fertilizer. Signs of nitrogen deficiency detected.")
        elif nutrient_status.get("nitrogen") == "Slight Deficiency":
            recommendations.append("Consider nitrogen application during next scheduled fertilization.")
        
        if nutrient_status.get("phosphorus") == "Deficient":
            recommendations.append("Apply phosphorus fertilizer. Phosphorus deficiency indicated.")
        elif nutrient_status.get("phosphorus") == "Slight Deficiency":
            recommendations.append("Monitor for phosphorus deficiency symptoms. Consider soil testing.")
        
        if nutrient_status.get("potassium") == "Deficient":
            recommendations.append("Apply potassium fertilizer. Signs of potassium deficiency detected.")
        elif nutrient_status.get("potassium") == "Slight Deficiency":
            recommendations.append("Consider potassium application during next scheduled fertilization.")
        
        # Color distribution recommendations
        yellow_pct = analysis_result.get("yellow_percentage", 0)
        brown_pct = analysis_result.get("brown_percentage", 0)
        
        if yellow_pct > 30:
            recommendations.append("High yellowing detected. Check for water stress or nutrient imbalances.")
        
        if brown_pct > 20:
            recommendations.append("Significant brown/dead tissue detected. Check for disease, pest damage, or extreme stress.")
        
        # Add general recommendations if limited specific ones
        if len(recommendations) < 2:
            if health_score >= 80:
                recommendations.append("Crop appears healthy. Maintain current management practices.")
            else:
                recommendations.append("Consider soil testing for more precise nutrient management recommendations.")
                recommendations.append("Monitor water management to ensure optimal moisture levels.")
        
        return recommendations