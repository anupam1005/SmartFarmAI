import streamlit as st
import cv2
import numpy as np
import time
import io
from PIL import Image
from datetime import datetime

from models.pest_detection_model import PestDetectionModel
from db_utils import (
    get_all_farms,
    get_fields_by_farm,
    save_pest_detection,
    get_pest_detections_by_field,
    get_detection_history
)

# Initialize the pest detection model
pest_model = PestDetectionModel()

def show():
    st.markdown("<h1 class='main-header'>Pest Detection</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Detect and identify crop pests and diseases using AI</p>", unsafe_allow_html=True)
    
    # Layout with sidebar for options
    with st.sidebar:
        st.header("Detection Options")
        
        # Get farms
        farms = get_all_farms()
        if not farms:
            st.warning("No farms found. Please create a farm first.")
            return
        
        # Farm selector
        farm_names = [farm.name for farm in farms]
        selected_farm_name = st.selectbox("Select Farm", farm_names)
        
        # Get selected farm
        selected_farm = next((farm for farm in farms if farm.name == selected_farm_name), None)
        if not selected_farm:
            st.error("Selected farm not found.")
            return
        
        # Field selector
        fields = get_fields_by_farm(selected_farm.id)
        if not fields:
            st.warning("No fields found for this farm. Please add a field first.")
            return
        
        field_names = [field.name for field in fields]
        selected_field_name = st.selectbox("Select Field", field_names)
        
        # Get selected field
        selected_field = next((field for field in fields if field.name == selected_field_name), None)
        if not selected_field:
            st.error("Selected field not found.")
            return
        
        # Detection parameters
        st.subheader("Detection Parameters")
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
        
        # Detection History tab
        st.subheader("Detection History")
        show_history = st.checkbox("Show Detection History", value=False)
    
    # Main content area - Tabs for Upload and History
    if show_history:
        show_detection_history(selected_field)
    else:
        show_detection_interface(selected_field, confidence_threshold)

def show_detection_interface(field, confidence_threshold):
    """Show the pest detection upload and analysis interface"""
    st.header(f"Pest Detection for {field.name}")
    
    if field.current_crop:
        st.info(f"Current crop: {field.current_crop}")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an image of your crop for pest detection", 
                                     type=["jpg", "jpeg", "png"])
    
    use_camera = st.checkbox("Or use camera to take a photo")
    
    image = None
    
    if use_camera:
        camera_image = st.camera_input("Take a photo of your crop")
        if camera_image is not None:
            # Convert the file to an opencv image.
            bytes_data = camera_image.getvalue()
            image = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            st.success("Photo captured successfully!")
    
    elif uploaded_file is not None:
        # Convert the file to an opencv image.
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.success("Image uploaded successfully!")
    
    # Process the image if available
    if image is not None:
        # Display the uploaded image
        st.subheader("Uploaded Image")
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Uploaded Image", use_column_width=True)
        
        # Add a button to run the detection
        if st.button("Run Pest Detection"):
            with st.spinner("Analyzing image for pests and diseases..."):
                # Artificial delay to simulate processing
                time.sleep(1.5)
                
                # Run detection
                detection_results = pest_model.detect_pests(image)
                
                if detection_results["success"]:
                    # Filter results by confidence threshold
                    filtered_detections = [
                        d for d in detection_results["detections"] 
                        if d["confidence"] >= confidence_threshold or d["class"] == "No Pests Detected"
                    ]
                    
                    if not filtered_detections or (len(filtered_detections) == 1 and filtered_detections[0]["class"] == "No Pests Detected"):
                        st.success("No significant pest issues detected in this image.")
                        
                        # Option to save the negative result
                        if st.button("Save 'No Pests Detected' Result"):
                            save_detection_to_db(field.id, "No Pests Detected", 0.9, "None", 
                                               "No significant pest issues were detected in the analyzed image.", 
                                               "Continue regular monitoring and preventive measures.", image)
                            st.success("Result saved to database.")
                    else:
                        # Display detection results
                        st.subheader("Detection Results")
                        
                        for i, detection in enumerate(filtered_detections):
                            with st.container():
                                col1, col2 = st.columns([1, 3])
                                
                                with col1:
                                    # Show confidence with a gauge
                                    confidence = detection["confidence"] * 100
                                    severity = detection["severity"]
                                    severity_color = "red" if severity == "High" else "orange" if severity == "Medium" else "green"
                                    
                                    st.markdown(f"""
                                    <div style="text-align: center;">
                                        <div style="font-size: 24px; font-weight: bold; color: {severity_color};">
                                            {confidence:.0f}%
                                        </div>
                                        <div style="font-size: 14px; color: #666;">
                                            Confidence
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown(f"#### {detection['class']}")
                                    st.markdown(f"**Severity:** {detection['severity']}")
                                    st.markdown(f"**Description:** {detection['description']}")
                                    
                                    # Expandable treatment recommendations
                                    with st.expander("Treatment Recommendations"):
                                        st.markdown(detection["treatment"])
                                
                                # Add a button to save this detection to database
                                if st.button(f"Save '{detection['class']}' Detection", key=f"save_detection_{i}"):
                                    image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
                                    
                                    # Save to database
                                    save_detection_to_db(field.id, detection["class"], detection["confidence"], 
                                                      detection["severity"], detection["description"], 
                                                      detection["treatment"], image)
                                    
                                    st.success(f"Saved {detection['class']} detection to database.")
                                
                                st.markdown("---")
                else:
                    st.error(f"Detection failed: {detection_results.get('error', 'Unknown error')}")

def show_detection_history(field):
    """Show pest detection history for a field"""
    st.header(f"Pest Detection History for {field.name}")
    
    # Get detection history
    detections = get_pest_detections_by_field(field.id)
    
    if not detections:
        st.info("No pest detection history found for this field.")
        return
    
    # Create tabs for detections by date
    detections.sort(key=lambda x: x.date, reverse=True)
    
    # Group detections by date
    detection_dates = {}
    for detection in detections:
        date_str = detection.date.strftime("%Y-%m-%d")
        if date_str not in detection_dates:
            detection_dates[date_str] = []
        detection_dates[date_str].append(detection)
    
    # Show detections by date in expanders
    for date_str, date_detections in detection_dates.items():
        display_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
        
        with st.expander(f"Detections on {display_date} ({len(date_detections)})"):
            for detection in date_detections:
                with st.container():
                    cols = st.columns([2, 3])
                    
                    with cols[0]:
                        # Show image if available
                        if detection.image_path:
                            try:
                                st.image(detection.image_path, width=200)
                            except:
                                st.info("Image not available")
                    
                    with cols[1]:
                        # Show detection details
                        st.markdown(f"#### {detection.detected_class}")
                        st.markdown(f"**Confidence:** {detection.confidence * 100:.1f}%")
                        st.markdown(f"**Severity:** {detection.severity}")
                        st.markdown(f"**Description:** {detection.description}")
                        
                        with st.expander("Treatment Recommendation"):
                            st.markdown(detection.treatment_recommendation)
                
                st.markdown("---")

def save_detection_to_db(field_id, detected_class, confidence, severity, description, treatment, image=None):
    """Save detection results to the database"""
    image_path = None
    
    # Save image if available
    if image is not None:
        # In a real application, we would save the image to a file or cloud storage
        # Here we'll just assume we have a path
        image_path = f"pest_images/{field_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    
    # Save detection to database
    save_pest_detection(
        field_id=field_id,
        detected_class=detected_class,
        confidence=confidence,
        severity=severity,
        description=description,
        treatment_recommendation=treatment,
        image_path=image_path
    )