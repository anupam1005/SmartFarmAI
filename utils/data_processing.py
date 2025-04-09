import pandas as pd
import numpy as np
import cv2
from datetime import datetime, timedelta

def clean_weather_data(data):
    """
    Clean and process weather data
    
    Args:
        data: Raw weather data
        
    Returns:
        Cleaned and processed weather data
    """
    # Handle missing values
    if isinstance(data, pd.DataFrame):
        # Fill missing numeric values with column means
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())
        
        # Fill missing categorical values with 'Unknown'
        categorical_cols = data.select_dtypes(exclude=[np.number]).columns
        data[categorical_cols] = data[categorical_cols].fillna('Unknown')
    
    return data

def process_image(image, resize_dim=None):
    """
    Process image for analysis
    
    Args:
        image: Input image
        resize_dim: Tuple of (width, height) for resizing, or None to keep original size
        
    Returns:
        Processed image
    """
    # Convert to numpy array if it's not already
    if not isinstance(image, np.ndarray):
        import io
        from PIL import Image as PILImage
        
        if isinstance(image, bytes):
            image = PILImage.open(io.BytesIO(image))
        
        image = np.array(image)
    
    # Resize if dimensions are provided
    if resize_dim is not None:
        image = cv2.resize(image, resize_dim)
    
    # Ensure image is in RGB format
    if len(image.shape) == 2:  # Grayscale
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:  # RGBA
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    
    return image

def generate_time_series(days=30, base_value=100, volatility=10, trend=0):
    """
    Generate synthetic time series data for demonstration
    
    Args:
        days: Number of days in the time series
        base_value: Starting value
        volatility: Volatility of the series
        trend: Overall trend direction (positive or negative)
        
    Returns:
        DataFrame with date and value columns
    """
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days, 0, -1)]
    
    # Generate values with some randomness, volatility and trend
    values = [base_value]
    for i in range(1, days):
        change = np.random.normal(trend, volatility)
        new_value = max(0, values[-1] + change)  # Ensure non-negative values
        values.append(new_value)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'value': values
    })
    
    return df

def normalize_soil_values(soil_data):
    """
    Normalize soil nutrient values to a 0-100 scale
    
    Args:
        soil_data: Dictionary with soil nutrient values
        
    Returns:
        Dictionary with normalized values
    """
    # Define typical min/max ranges for normalization
    ranges = {
        'nitrogen': (0, 150),
        'phosphorus': (0, 150),
        'potassium': (0, 200),
        'ph': (4, 9),
        'organic_matter': (0, 10)
    }
    
    normalized_data = {}
    
    for key, value in soil_data.items():
        if key in ranges:
            min_val, max_val = ranges[key]
            normalized_value = ((value - min_val) / (max_val - min_val)) * 100
            normalized_data[key] = max(0, min(100, normalized_value))  # Clamp to 0-100
        else:
            normalized_data[key] = value  # Keep non-numeric values as is
    
    return normalized_data

def extract_image_features(image):
    """
    Extract basic features from an image for analysis
    
    Args:
        image: Input image array
        
    Returns:
        Dictionary with extracted features
    """
    # Convert to HSV color space for better color analysis
    hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Calculate color histograms
    h_hist = cv2.calcHist([hsv_img], [0], None, [180], [0, 180])
    s_hist = cv2.calcHist([hsv_img], [1], None, [256], [0, 256])
    v_hist = cv2.calcHist([hsv_img], [2], None, [256], [0, 256])
    
    # Normalize histograms
    h_hist = cv2.normalize(h_hist, h_hist, 0, 1, cv2.NORM_MINMAX)
    s_hist = cv2.normalize(s_hist, s_hist, 0, 1, cv2.NORM_MINMAX)
    v_hist = cv2.normalize(v_hist, v_hist, 0, 1, cv2.NORM_MINMAX)
    
    # Extract color masks for common plant health indicators
    green_mask = cv2.inRange(hsv_img, (36, 25, 25), (70, 255, 255))
    yellow_mask = cv2.inRange(hsv_img, (15, 25, 25), (35, 255, 255))
    brown_mask = cv2.inRange(hsv_img, (5, 25, 25), (14, 255, 255))
    
    # Calculate percentages of each color
    total_pixels = image.shape[0] * image.shape[1]
    green_percent = cv2.countNonZero(green_mask) / total_pixels * 100
    yellow_percent = cv2.countNonZero(yellow_mask) / total_pixels * 100
    brown_percent = cv2.countNonZero(brown_mask) / total_pixels * 100
    
    # Extract edge features to detect leaf patterns
    gray_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray_img, 100, 200)
    edge_percent = cv2.countNonZero(edges) / total_pixels * 100
    
    # Compile features
    features = {
        'green_percent': green_percent,
        'yellow_percent': yellow_percent,
        'brown_percent': brown_percent,
        'edge_density': edge_percent,
        'h_hist': h_hist.flatten().tolist(),
        's_hist': s_hist.flatten().tolist(),
        'v_hist': v_hist.flatten().tolist()
    }
    
    return features
