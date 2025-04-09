import numpy as np
import cv2
import os

# Conditionally import TensorFlow
# This allows the application to run even if TensorFlow isn't working correctly
tf = None
try:
    import tensorflow as tf
    print("TensorFlow imported successfully")
except (ImportError, TypeError, AttributeError) as e:
    print(f"TensorFlow import failed: {e}. Using fallback methods instead.")

# Simulated pest detection functionality since we don't have an actual model
# In production, this would be a real ML model for pest and disease detection

def preprocess_image(image):
    """
    Preprocess image for the pest detection model
    
    Args:
        image: Input image array
        
    Returns:
        Preprocessed image ready for the model
    """
    # Resize the image to a standard size
    resized_img = cv2.resize(image, (224, 224))
    
    # Convert to RGB if grayscale
    if len(resized_img.shape) == 2:
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_GRAY2RGB)
    elif resized_img.shape[2] == 4:  # If RGBA, convert to RGB
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_RGBA2RGB)
    
    # Normalize pixel values to [0, 1]
    normalized_img = resized_img / 255.0
    
    # Expand dimensions to match model input shape
    return np.expand_dims(normalized_img, axis=0)

def get_disease_info(disease_class):
    """
    Get detailed information about a specific crop disease
    
    Args:
        disease_class: The identified disease class
        
    Returns:
        Dictionary with disease information
    """
    disease_database = {
        "Healthy": {
            "description": "No disease detected. Plant appears healthy.",
            "treatment": "Continue with regular maintenance and monitoring.",
            "severity": "None"
        },
        "Tomato_Late_Blight": {
            "description": "Late blight is a destructive disease affecting tomatoes, causing dark, water-soaked lesions on leaves, stems, and fruits.",
            "treatment": "Apply fungicides containing chlorothalonil or copper compounds. Remove infected plants to prevent spread. Avoid overhead watering and ensure good air circulation.",
            "severity": "High"
        },
        "Maize_Common_Rust": {
            "description": "Common rust appears as small, circular to elongate, cinnamon-brown pustules on both leaf surfaces, often in bands across the leaf.",
            "treatment": "Apply fungicides containing azoxystrobin, pyraclostrobin, or propiconazole. Plant resistant varieties for future crops.",
            "severity": "Medium"
        },
        "Bean_Anthracnose": {
            "description": "Anthracnose causes dark, sunken lesions on pods, leaves, and stems, often with pink spore masses in the center.",
            "treatment": "Apply copper-based fungicides or chlorothalonil. Use certified disease-free seeds. Rotate crops and avoid handling plants when wet.",
            "severity": "Medium"
        },
        "Tomato_Early_Blight": {
            "description": "Early blight causes dark, concentric rings on leaves, often starting from the bottom of the plant and moving upward.",
            "treatment": "Apply fungicides containing chlorothalonil, copper, or mancozeb. Remove lower infected leaves. Mulch around plants to prevent soil splashing.",
            "severity": "Medium"
        },
        "Cassava_Mosaic_Disease": {
            "description": "Cassava mosaic disease causes mottling and distortion of leaves, stunted growth, and reduced root yield.",
            "treatment": "No chemical treatment is effective. Use disease-free cuttings for planting. Remove and destroy infected plants. Plant resistant varieties.",
            "severity": "High"
        },
        "Aphid_Infestation": {
            "description": "Aphids are small sap-sucking insects that cause yellowing, curling of leaves, and stunted growth. They also transmit viral diseases.",
            "treatment": "Apply insecticidal soap, neem oil, or pyrethrin. Introduce natural predators like ladybugs. Use strong water spray to knock aphids off plants.",
            "severity": "Medium"
        },
        "Whitefly_Infestation": {
            "description": "Whiteflies are tiny, white insects that feed on plant sap, causing yellowing and wilting. They also excrete honeydew, leading to sooty mold.",
            "treatment": "Apply insecticidal soap, neem oil, or synthetic insecticides. Use yellow sticky traps. Remove heavily infested leaves.",
            "severity": "Medium"
        }
    }
    
    return disease_database.get(disease_class, {
        "description": "Information not available for this condition.",
        "treatment": "Consult with a local agricultural expert.",
        "severity": "Unknown"
    })

def detect_pests(image):
    """
    Detect pests and diseases in the provided image
    
    Args:
        image: Input image array
        
    Returns:
        Dictionary containing detection results
    """
    # In a real implementation, we would:
    # 1. Load a trained pest/disease detection model
    # 2. Preprocess the image
    # 3. Make predictions with the model
    # 4. Process the predictions to provide useful insights
    
    # Since we don't have a real model, we'll simulate the detection
    # This is just for demonstration purposes
    
    # Preprocess the image
    preprocessed_img = preprocess_image(image)
    
    # Simple image analysis for demonstration
    # In production, this would be replaced with actual model prediction
    hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Analyze color distribution
    green_mask = cv2.inRange(hsv_img, (36, 25, 25), (70, 255, 255))
    yellow_mask = cv2.inRange(hsv_img, (15, 25, 25), (35, 255, 255))
    brown_mask = cv2.inRange(hsv_img, (5, 25, 25), (14, 255, 255))
    
    green_pixels = cv2.countNonZero(green_mask)
    yellow_pixels = cv2.countNonZero(yellow_mask)
    brown_pixels = cv2.countNonZero(brown_mask)
    total_pixels = image.shape[0] * image.shape[1]
    
    yellow_ratio = yellow_pixels / total_pixels
    brown_ratio = brown_pixels / total_pixels
    green_ratio = green_pixels / total_pixels
    
    # Simulated disease detection based on color distribution
    # In production, this would come from a trained model's predictions
    detected_class = "Healthy"
    confidence = 85.0
    severity = "None"
    
    if yellow_ratio > 0.2 and green_ratio < 0.5:
        detected_class = "Tomato_Early_Blight"
        confidence = 78.5
        severity = "Medium"
    elif brown_ratio > 0.15:
        detected_class = "Tomato_Late_Blight"
        confidence = 82.3
        severity = "High"
    elif yellow_ratio > 0.1 and brown_ratio > 0.05:
        detected_class = "Maize_Common_Rust"
        confidence = 75.8
        severity = "Medium"
    
    # Get additional information about the detected disease
    disease_info = get_disease_info(detected_class)
    
    # Create a highlighted image showing affected areas
    highlighted_image = image.copy()
    
    if detected_class != "Healthy":
        # Create a mask for affected areas based on color analysis
        if "Blight" in detected_class:
            affected_mask = cv2.bitwise_or(brown_mask, yellow_mask)
        elif "Rust" in detected_class:
            affected_mask = brown_mask
        else:
            affected_mask = yellow_mask
        
        # Dilate the mask to make it more visible
        kernel = np.ones((5, 5), np.uint8)
        affected_mask = cv2.dilate(affected_mask, kernel, iterations=1)
        
        # Highlight affected areas in red
        highlighted_image[affected_mask > 0] = [255, 0, 0]
    else:
        # No highlighting for healthy plants
        highlighted_image = None
    
    # Compile detection results
    detection_result = {
        "detected_class": detected_class,
        "confidence": confidence,
        "severity": severity,
        "description": disease_info.get("description", ""),
        "treatment_recommendation": disease_info.get("treatment", ""),
        "highlighted_image": highlighted_image
    }
    
    return detection_result

def load_model():
    """
    Load the pre-trained pest detection model
    
    Returns:
        Loaded TensorFlow model
    """
    # In a real implementation, we would load a saved model
    # For example:
    # model_path = os.getenv("PEST_MODEL_PATH", "models/pest_detection_model.h5")
    # model = tf.keras.models.load_model(model_path)
    # return model
    
    # For now, we'll just indicate that we would load a model here
    print("Note: In production, a pre-trained pest detection model would be loaded here.")
    return None
