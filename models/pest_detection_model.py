import numpy as np
import cv2
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PestDetectionModel:
    """
    A simplified pest detection model that uses basic computer vision techniques
    to detect potential pest issues in crop images.
    
    Note: This is a demonstration model that uses basic image processing instead of
    deep learning to avoid TensorFlow and GPU dependencies.
    """
    
    def __init__(self):
        """Initialize the pest detection model"""
        logger.info("Initializing Pest Detection Model")
        self.initialized = True
        
        # Define common agricultural pest classes
        self.pest_classes = [
            "Aphids",
            "Spider Mites",
            "Thrips",
            "Whiteflies",
            "Leaf Miners",
            "Caterpillars",
            "Beetle Damage",
            "Grasshoppers",
            "Fungal Infection",
            "Bacterial Infection",
            "Viral Infection",
            "Nutrient Deficiency"  # Not a pest but often confused with pest damage
        ]
    
    def detect_pests(self, image):
        """
        Detect potential pest issues in an image
        
        Args:
            image: Image as a numpy array (BGR format)
            
        Returns:
            Dictionary with detection results
        """
        if image is None:
            return {
                "success": False,
                "error": "No image provided"
            }
        
        try:
            # This is a simplified demo version that simulates pest detection
            # In a real application, this would use an actual detection model
            
            # Convert to HSV color space
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Extract features that might indicate pest presence
            # For this demo, we'll analyze color distributions and look for irregular patterns
            features = self._extract_features(image, hsv_image)
            
            # Analyze features for pest indicators
            # In a real model, this would involve a trained classifier
            detections = self._analyze_features(features)
            
            # Return results
            return {
                "success": True,
                "detections": detections
            }
            
        except Exception as e:
            logger.error(f"Error detecting pests: {e}")
            return {
                "success": False,
                "error": f"Detection failed: {str(e)}"
            }
    
    def _extract_features(self, image, hsv_image):
        """
        Extract features from image that might indicate pest presence
        
        Args:
            image: Original BGR image
            hsv_image: HSV converted image
            
        Returns:
            Dictionary of extracted features
        """
        # Calculate color histograms
        h_hist = cv2.calcHist([hsv_image], [0], None, [30], [0, 180])
        s_hist = cv2.calcHist([hsv_image], [1], None, [32], [0, 256])
        v_hist = cv2.calcHist([hsv_image], [2], None, [32], [0, 256])
        
        # Normalize histograms
        h_hist = cv2.normalize(h_hist, h_hist).flatten()
        s_hist = cv2.normalize(s_hist, s_hist).flatten()
        v_hist = cv2.normalize(v_hist, v_hist).flatten()
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect edges (can indicate irregular patterns caused by pests)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Detect potential spots/lesions using simple blob detection
        # In a real app, this would use more sophisticated techniques
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contours
        small_spots_count = 0
        medium_spots_count = 0
        large_spots_count = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 10 <= area < 50:
                small_spots_count += 1
            elif 50 <= area < 200:
                medium_spots_count += 1
            elif area >= 200:
                large_spots_count += 1
        
        # Analyze color variations which might indicate stress or damage
        std_hue = np.std(hsv_image[:, :, 0])
        std_saturation = np.std(hsv_image[:, :, 1])
        std_value = np.std(hsv_image[:, :, 2])
        
        # Compile features
        features = {
            "h_hist": h_hist,
            "s_hist": s_hist,
            "v_hist": v_hist,
            "edge_density": edge_density,
            "small_spots": small_spots_count,
            "medium_spots": medium_spots_count,
            "large_spots": large_spots_count,
            "std_hue": std_hue,
            "std_saturation": std_saturation,
            "std_value": std_value
        }
        
        return features
    
    def _analyze_features(self, features):
        """
        Analyze extracted features to identify potential pest issues
        
        Args:
            features: Dictionary of image features
            
        Returns:
            List of detection results
        """
        # For this demo, we'll use a simplified rule-based approach
        # In a real application, this would use a trained model
        
        detections = []
        
        # Example rules (simplified)
        # These thresholds would normally be learned or carefully calibrated
        
        # Check for small clusters that might indicate small pests
        if features['small_spots'] > 30:
            confidence = min(0.95, 0.5 + (features['small_spots'] - 30) / 100)
            detections.append(self._create_detection("Aphids", confidence))
        elif features['small_spots'] > 20:
            confidence = min(0.85, 0.4 + (features['small_spots'] - 20) / 100)
            detections.append(self._create_detection("Spider Mites", confidence))
        
        # Check for irregular edges that might indicate leaf damage
        if features['edge_density'] > 0.15:
            confidence = min(0.9, 0.5 + features['edge_density'])
            if features['medium_spots'] > 10:
                detections.append(self._create_detection("Caterpillars", confidence))
            else:
                detections.append(self._create_detection("Leaf Miners", confidence))
        
        # Check for color variations that might indicate disease
        if features['std_saturation'] > 50 and features['large_spots'] > 5:
            confidence = min(0.85, 0.5 + features['std_saturation'] / 100)
            detections.append(self._create_detection("Fungal Infection", confidence))
        
        # If no specific patterns detected but some anomalies exist
        if not detections and (features['edge_density'] > 0.1 or 
                              features['small_spots'] > 10 or 
                              features['medium_spots'] > 5):
            # Generate a random detection for demonstration
            random_class = random.choice(self.pest_classes)
            detections.append(self._create_detection(random_class, 0.6))
        
        # If really nothing found, indicate so
        if not detections:
            detections.append({
                "class": "No Pests Detected",
                "confidence": 0.8,
                "severity": "None",
                "description": "No significant pest issues detected in the image.",
                "treatment": "Continue regular monitoring and preventive measures."
            })
        
        return detections
    
    def _create_detection(self, pest_class, confidence):
        """
        Create a formatted detection result
        
        Args:
            pest_class: Detected pest class
            confidence: Detection confidence score
            
        Returns:
            Dictionary with detection details
        """
        # Determine severity based on confidence
        if confidence > 0.8:
            severity = "High"
        elif confidence > 0.6:
            severity = "Medium"
        else:
            severity = "Low"
        
        # Get description and treatment for the pest
        description, treatment = self._get_pest_info(pest_class)
        
        return {
            "class": pest_class,
            "confidence": round(float(confidence), 2),
            "severity": severity,
            "description": description,
            "treatment": treatment
        }
    
    def _get_pest_info(self, pest_class):
        """
        Get description and treatment information for a pest class
        
        Args:
            pest_class: Name of pest class
            
        Returns:
            Tuple of (description, treatment) strings
        """
        pest_info = {
            "Aphids": (
                "Small sap-sucking insects that cluster on new growth and undersides of leaves, causing distortion and stunting.",
                "Apply insecticidal soap or neem oil. For severe infestations, consider systemic insecticides. Encourage beneficial insects like ladybugs."
            ),
            "Spider Mites": (
                "Tiny arachnids that cause stippling on leaves and fine webbing. Thrive in hot, dry conditions.",
                "Increase humidity and water pressure spray to reduce populations. Apply miticides if severe. Predatory mites can provide biological control."
            ),
            "Thrips": (
                "Slender insects that rasp plant surfaces and suck sap, causing silvery scarring and distorted growth.",
                "Use blue sticky traps for monitoring. Apply insecticidal soap or spinosad. Remove weeds that may host thrips."
            ),
            "Whiteflies": (
                "Small white flying insects that cluster on leaf undersides. They excrete honeydew that leads to sooty mold.",
                "Use yellow sticky traps. Apply insecticidal soap or neem oil. Consider parasitic wasps for biological control."
            ),
            "Leaf Miners": (
                "Larvae that tunnel between leaf surfaces, creating distinctive winding trails or blotches.",
                "Remove and destroy affected leaves. Use yellow sticky traps for adult flies. Apply spinosad or neem oil as a preventive measure."
            ),
            "Caterpillars": (
                "Larvae of butterflies and moths that chew on leaves, causing irregular holes and substantial defoliation.",
                "Handpick if infestation is small. Apply Bacillus thuringiensis (Bt) for biological control. Use pheromone traps for monitoring."
            ),
            "Beetle Damage": (
                "Various beetles chew leaves, stems, or roots, often leaving characteristic feeding patterns.",
                "Rotate crops to break pest cycles. Use row covers for protection. Apply appropriate insecticides if damage is severe."
            ),
            "Grasshoppers": (
                "Large insects that consume large amounts of plant material, leaving irregular edges on leaves.",
                "Use row covers for protection. Apply neem oil as a repellent. For severe infestations, consider insecticides or biological controls like Nosema locustae."
            ),
            "Fungal Infection": (
                "Fungal pathogens causing spots, blotches, powdery or downy mildew, or rot on plant tissues.",
                "Improve air circulation. Avoid overhead watering. Apply appropriate fungicides. Remove and destroy infected plant material."
            ),
            "Bacterial Infection": (
                "Bacterial pathogens causing spots, blights, or wilts, often with water-soaked appearance and yellow halos.",
                "Remove infected plants to prevent spread. Use copper-based bactericides preventively. Avoid working with plants when wet."
            ),
            "Viral Infection": (
                "Viral pathogens causing mottling, distortion, stunting, or unusual coloration patterns.",
                "Remove and destroy infected plants as there is no cure. Control insect vectors like aphids. Use virus-resistant varieties when available."
            ),
            "Nutrient Deficiency": (
                "Symptoms resembling pest damage but caused by lack of essential nutrients, often showing specific patterns on leaves.",
                "Conduct soil tests to confirm. Apply appropriate fertilizers to address specific deficiencies. Consider foliar feeding for quick results."
            )
        }
        
        # Return information for the pest class, or generic information if not found
        default_info = (
            "Unspecified plant health issue that may affect crop production.",
            "Conduct further analysis to identify specific issue. Monitor affected plants closely."
        )
        
        return pest_info.get(pest_class, default_info)