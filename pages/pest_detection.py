import streamlit as st
import cv2
import numpy as np
import os
from PIL import Image
from datetime import datetime
from models import pest_detection_model
from db_utils import get_fields_by_farm, save_pest_detection, get_pest_detections_by_field

def show():
    st.title("Pest & Disease Detection")
    
    # Get farm ID from session state
    if 'selected_farm_id' not in st.session_state:
        st.error("No farm selected. Please select a farm from the sidebar.")
        return
    
    farm_id = st.session_state['selected_farm_id']
    
    # Get fields for the farm
    fields = get_fields_by_farm(farm_id)
    
    if not fields:
        st.warning("No fields found for this farm. Please add fields first.")
        return
    
    # Create tabs for detection and history
    tab1, tab2 = st.tabs(["Detect Pests & Diseases", "Detection History"])
    
    with tab1:
        st.header("Detect Pests & Diseases")
        
        # Field selection
        field_names = [field.name for field in fields]
        field_ids = [field.id for field in fields]
        
        selected_field_name = st.selectbox(
            "Select Field",
            field_names,
            key="pest_detection_field"
        )
        selected_field_index = field_names.index(selected_field_name)
        selected_field_id = field_ids[selected_field_index]
        
        # File uploader for images
        uploaded_file = st.file_uploader(
            "Upload an image of your crop for pest and disease detection",
            type=["jpg", "jpeg", "png"]
        )
        
        # Camera input as an alternative
        camera_input = st.camera_input("Or take a photo")
        
        # Process the image if available
        if uploaded_file is not None or camera_input is not None:
            # Determine which input to use
            image_input = uploaded_file if uploaded_file is not None else camera_input
            
            # Display the uploaded image
            image = Image.open(image_input)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Process the image when the user clicks the button
            if st.button("Analyze Image for Pests and Diseases"):
                with st.spinner("Analyzing image for pests and diseases..."):
                    # Convert PIL Image to numpy array for OpenCV processing
                    image_array = np.array(image)
                    
                    # If image is RGBA, convert to RGB
                    if image_array.shape[-1] == 4:
                        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
                    
                    # Perform the detection
                    detection_result = pest_detection_model.detect_pests(image_array)
                    
                    # Display the results
                    st.success("Analysis complete!")
                    
                    # Create two columns for results
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Display the highlighted image if available
                        highlighted_image = detection_result.get("highlighted_image")
                        if highlighted_image is not None:
                            st.subheader("Detected Issue Areas")
                            st.image(highlighted_image, caption="Areas of concern highlighted in red", use_column_width=True)
                        
                        # Display the detection details
                        st.subheader("Detection Results")
                        st.write(f"**Detected Issue:** {detection_result['detected_class'].replace('_', ' ')}")
                        st.write(f"**Confidence:** {detection_result['confidence']:.1f}%")
                        st.write(f"**Severity:** {detection_result['severity']}")
                        
                        # Description and treatment
                        st.subheader("Description")
                        st.write(detection_result['description'])
                        
                        st.subheader("Treatment Recommendations")
                        st.write(detection_result['treatment_recommendation'])
                    
                    with col2:
                        # Quick actions
                        st.subheader("Actions")
                        
                        # Save the detection to the database
                        if st.button("Save This Detection"):
                            # Save the detection record
                            # In a real application, we would save the image to a file storage
                            # and store the path in the database
                            image_path = None  # We're not saving the image in this demo
                            
                            save_pest_detection(
                                field_id=selected_field_id,
                                detected_class=detection_result['detected_class'],
                                confidence=detection_result['confidence'],
                                severity=detection_result['severity'],
                                description=detection_result['description'],
                                treatment_recommendation=detection_result['treatment_recommendation'],
                                image_path=image_path
                            )
                            
                            st.success("Detection record saved successfully!")
                        
                        # Print report option
                        if st.button("Print Report"):
                            st.info("Printing functionality would be implemented here.")
                        
                        # Share option
                        if st.button("Share with Expert"):
                            st.info("Sharing functionality would be implemented here.")
        else:
            # Placeholder when no image is uploaded
            st.info("Please upload an image or take a photo to analyze for pests and diseases.")
            
            # Example information
            st.subheader("What This Tool Can Detect")
            st.write("""
            This tool can help identify common crop pests and diseases, including:
            - Aphid infestations
            - Whitefly infestations
            - Tomato early blight
            - Tomato late blight
            - Maize common rust
            - Bean anthracnose
            - Cassava mosaic disease
            - And more...
            """)
            
            # Tips
            st.subheader("Tips for Best Results")
            st.write("""
            - Take clear, well-lit photos
            - Focus on the affected plant parts (leaves, stems, fruits)
            - Include both healthy and affected areas for comparison
            - Take multiple photos from different angles if needed
            """)
    
    with tab2:
        st.header("Detection History")
        
        # Field filter for history
        field_filter = st.selectbox(
            "Filter by Field",
            ["All Fields"] + field_names,
            key="pest_detection_history_field"
        )
        
        # Get detection history
        if field_filter == "All Fields":
            # In a real app, we would implement pagination or limiting
            all_detections = []
            for field in fields:
                detections = get_pest_detections_by_field(field.id)
                for detection in detections:
                    all_detections.append({
                        "field_id": field.id,
                        "field_name": next(f.name for f in fields if f.id == field.id),
                        "detection": detection
                    })
        else:
            field_index = field_names.index(field_filter)
            field_id = field_ids[field_index]
            detections = get_pest_detections_by_field(field_id)
            all_detections = [{
                "field_id": field_id,
                "field_name": field_filter,
                "detection": detection
            } for detection in detections]
        
        # Display the detection history
        if all_detections:
            for i, detection_data in enumerate(all_detections):
                detection = detection_data["detection"]
                field_name = detection_data["field_name"]
                
                with st.expander(
                    f"{detection.date.strftime('%Y-%m-%d %H:%M')} - {field_name} - {detection.detected_class.replace('_', ' ')}",
                    expanded=(i == 0)  # Expand the first one by default
                ):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Field:** {field_name}")
                        st.write(f"**Date:** {detection.date.strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Detected Issue:** {detection.detected_class.replace('_', ' ')}")
                        st.write(f"**Confidence:** {detection.confidence:.1f}%")
                        st.write(f"**Severity:** {detection.severity}")
                        
                        # Description and treatment
                        st.subheader("Description")
                        st.write(detection.description)
                        
                        st.subheader("Treatment Recommendation")
                        st.write(detection.treatment_recommendation)
                    
                    with col2:
                        # If we had saved images, we would display them here
                        if detection.image_path:
                            st.image(detection.image_path, caption="Detected Image", use_column_width=True)
                        else:
                            st.write("No image available")
        else:
            st.info("No pest detection records found. Use the 'Detect Pests & Diseases' tab to analyze your crops.")