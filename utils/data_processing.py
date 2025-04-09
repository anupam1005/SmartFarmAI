import pandas as pd
import numpy as np
import cv2
from datetime import datetime, timedelta
import random

def normalize_data(data, min_val=0, max_val=1):
    """
    Normalize a numeric array to a specified range
    
    Args:
        data: Numeric array or list
        min_val: Minimum value in normalized range
        max_val: Maximum value in normalized range
        
    Returns:
        Normalized array
    """
    if isinstance(data, list):
        data = np.array(data)
    
    data_min = np.min(data)
    data_max = np.max(data)
    
    # Avoid division by zero
    if data_max == data_min:
        return np.ones_like(data) * min_val
    
    # Normalize to [0, 1] then scale to [min_val, max_val]
    normalized = (data - data_min) / (data_max - data_min)
    scaled = normalized * (max_val - min_val) + min_val
    
    return scaled

def smooth_data(data, window_size=3):
    """
    Apply moving average smoothing to a data series
    
    Args:
        data: Data to smooth (list or numpy array)
        window_size: Size of the smoothing window
        
    Returns:
        Smoothed data
    """
    if isinstance(data, list):
        data = np.array(data)
    
    if len(data) < window_size:
        return data
    
    # Compute moving average
    weights = np.ones(window_size) / window_size
    smoothed = np.convolve(data, weights, mode='valid')
    
    # Pad the beginning to maintain the same length
    padding = np.full(window_size - 1, smoothed[0])
    return np.concatenate([padding, smoothed])

def detect_outliers(data, threshold=2.0):
    """
    Identify outliers in a dataset using the Z-score method
    
    Args:
        data: Numeric data (list or numpy array)
        threshold: Z-score threshold for outlier detection
        
    Returns:
        Indices of outliers
    """
    if isinstance(data, list):
        data = np.array(data)
    
    mean = np.mean(data)
    std = np.std(data)
    
    # Avoid division by zero
    if std == 0:
        return []
    
    # Calculate Z-scores
    z_scores = np.abs((data - mean) / std)
    
    # Find indices where Z-score exceeds threshold
    return np.where(z_scores > threshold)[0]

def filter_outliers(data, threshold=2.0, replace_with='mean'):
    """
    Filter outliers from a dataset
    
    Args:
        data: Numeric data (list or numpy array)
        threshold: Z-score threshold for outlier detection
        replace_with: Method to replace outliers ('mean', 'median', 'nearest', or None to remove)
        
    Returns:
        Data with outliers filtered
    """
    if isinstance(data, list):
        data = np.array(data)
    
    # Make a copy of the data
    filtered_data = data.copy()
    
    # Get outlier indices
    outlier_indices = detect_outliers(data, threshold)
    
    if len(outlier_indices) == 0:
        return filtered_data
    
    if replace_with is None:
        # Remove outliers
        return np.delete(filtered_data, outlier_indices)
    
    # Calculate replacement value
    if replace_with == 'mean':
        replacement = np.mean(np.delete(data, outlier_indices))
    elif replace_with == 'median':
        replacement = np.median(np.delete(data, outlier_indices))
    elif replace_with == 'nearest':
        # For each outlier, replace with the nearest non-outlier value
        for idx in outlier_indices:
            # Find non-outlier indices
            non_outlier_indices = np.setdiff1d(np.arange(len(data)), outlier_indices)
            
            # Find nearest non-outlier index
            nearest_idx = non_outlier_indices[np.argmin(np.abs(non_outlier_indices - idx))]
            
            # Replace with value at nearest index
            filtered_data[idx] = data[nearest_idx]
        
        return filtered_data
    else:
        raise ValueError("replace_with must be 'mean', 'median', 'nearest', or None")
    
    # Replace outliers with the calculated value
    filtered_data[outlier_indices] = replacement
    
    return filtered_data

def generate_time_series(days=30, base_value=100, volatility=20, trend=1):
    """
    Generate a synthetic time series dataset
    
    Args:
        days: Number of days in the time series
        base_value: Starting value for the series
        volatility: Volatility of the random fluctuations
        trend: Daily trend direction and magnitude
        
    Returns:
        DataFrame with date and value columns
    """
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Generate values with random walk and trend
    values = [base_value]
    for i in range(1, days):
        # Random change with specified volatility
        random_change = np.random.normal(0, volatility)
        
        # Apply trend and bound to non-negative values
        new_value = max(0, values[-1] + random_change + trend)
        values.append(new_value)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'value': values
    })
    
    return df

def extract_features_from_image(image):
    """
    Extract basic features from an image for analysis
    
    Args:
        image: Input image array
        
    Returns:
        Dictionary with extracted features
    """
    if image is None:
        return None
    
    # Convert to RGB if the image is in BGR format (OpenCV default)
    if len(image.shape) == 3 and image.shape[2] == 3:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image
    
    # Convert to HSV for color analysis
    image_hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
    
    # Calculate average color
    avg_color_rgb = np.mean(image_rgb, axis=(0, 1))
    avg_color_hsv = np.mean(image_hsv, axis=(0, 1))
    
    # Calculate color histograms
    hist_h = cv2.calcHist([image_hsv], [0], None, [18], [0, 180])
    hist_s = cv2.calcHist([image_hsv], [1], None, [10], [0, 256])
    hist_v = cv2.calcHist([image_hsv], [2], None, [10], [0, 256])
    
    # Normalize histograms
    hist_h = cv2.normalize(hist_h, hist_h).flatten()
    hist_s = cv2.normalize(hist_s, hist_s).flatten()
    hist_v = cv2.normalize(hist_v, hist_v).flatten()
    
    # Calculate texture features (using grayscale image)
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    
    # Texture using GLCM (Gray-Level Co-occurrence Matrix) would be done here in a full implementation
    # For a simplified version, let's use basic statistical measures
    texture_mean = np.mean(gray)
    texture_std = np.std(gray)
    texture_entropy = -np.sum(gray * np.log2(gray + 1e-10)) / (gray.shape[0] * gray.shape[1])
    
    # Compile features
    features = {
        "avg_color_rgb": avg_color_rgb.tolist(),
        "avg_color_hsv": avg_color_hsv.tolist(),
        "histogram_hue": hist_h.tolist(),
        "histogram_saturation": hist_s.tolist(),
        "histogram_value": hist_v.tolist(),
        "texture_mean": float(texture_mean),
        "texture_std": float(texture_std),
        "texture_entropy": float(texture_entropy),
        "image_width": image.shape[1],
        "image_height": image.shape[0]
    }
    
    return features

def calculate_vegetation_indices(image):
    """
    Calculate vegetation indices from an RGB image
    
    Args:
        image: Input RGB image array
        
    Returns:
        Dictionary with vegetation indices
    """
    if image is None:
        return None
    
    # Ensure image is in RGB format
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Convert BGR to RGB if necessary (OpenCV loads images in BGR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image
    
    # Extract the RGB channels and normalize to 0-1
    r = image_rgb[:, :, 0].astype(float) / 255.0
    g = image_rgb[:, :, 1].astype(float) / 255.0
    b = image_rgb[:, :, 2].astype(float) / 255.0
    
    # Avoid division by zero
    epsilon = 1e-10
    
    # Calculate Visible Atmospherically Resistant Index (VARI)
    # VARI = (Green - Red) / (Green + Red - Blue)
    vari_numerator = g - r
    vari_denominator = g + r - b + epsilon
    vari = vari_numerator / vari_denominator
    
    # Calculate Green Leaf Index (GLI)
    # GLI = (2*Green - Red - Blue) / (2*Green + Red + Blue)
    gli_numerator = 2 * g - r - b
    gli_denominator = 2 * g + r + b + epsilon
    gli = gli_numerator / gli_denominator
    
    # Calculate Excess Green Index (ExG)
    # ExG = 2*g - r - b
    exg = 2 * g - r - b
    
    # Calculate Normalized Green Red Difference Index (NGRDI)
    # NGRDI = (g - r) / (g + r)
    ngrdi_numerator = g - r
    ngrdi_denominator = g + r + epsilon
    ngrdi = ngrdi_numerator / ngrdi_denominator
    
    # Calculate average values for each index
    vari_avg = float(np.mean(vari))
    gli_avg = float(np.mean(gli))
    exg_avg = float(np.mean(exg))
    ngrdi_avg = float(np.mean(ngrdi))
    
    # Return the indices
    indices = {
        "vari": vari_avg,
        "gli": gli_avg,
        "exg": exg_avg,
        "ngrdi": ngrdi_avg
    }
    
    return indices