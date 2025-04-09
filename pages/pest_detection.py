import streamlit as st
import numpy as np
import cv2
import io
from PIL import Image
from models import pest_detection_model

def show():
    st.header("Pest & Disease Detection")
    
    st.markdown("""
    Upload a clear image of your plant to detect pests or diseases. For best results:
    - Take close-up photos of affected leaves/stems
    - Ensure good lighting
    - Include multiple angles if possible
    """)
    
    # File uploader for images
    uploaded_file = st.file_uploader("Upload plant image", type=["jpg", "jpeg", "png"])
    
    col1, col2 = st.columns(2)
    
    if uploaded_file is not None:
        # Process the uploaded image
        image = Image.open(uploaded_file)
        
        # Convert to numpy array for OpenCV processing
        image_array = np.array(image)
        
        # Resize for display and model input
        resized_img = cv2.resize(image_array, (400, 400))
        
        with col1:
            st.subheader("Uploaded Image")
            st.image(resized_img, channels="RGB", use_column_width=True)
        
        with col2:
            st.subheader("Analysis Results")
            
            # Create a placeholder for the spinner during processing
            with st.spinner("Analyzing image..."):
                # Call the pest detection model
                try:
                    result = pest_detection_model.detect_pests(image_array)
                    
                    if result and 'detected_class' in result:
                        st.success(f"Detection Complete!")
                        
                        # Display detection results
                        st.markdown(f"**Detected Issue:** {result['detected_class']}")
                        st.markdown(f"**Confidence:** {result['confidence']:.2f}%")
                        st.markdown(f"**Severity Level:** {result['severity']}")
                        
                        # Show treatment recommendations
                        st.subheader("Recommended Treatment")
                        st.markdown(result['treatment_recommendation'])
                        
                        # Additional insights or visual markers
                        if 'highlighted_image' in result and result['highlighted_image'] is not None:
                            st.subheader("Affected Areas Highlighted")
                            st.image(result['highlighted_image'], channels="RGB", use_column_width=True)
                    else:
                        st.info("No pests or diseases detected. Your plant appears healthy.")
                        
                except Exception as e:
                    st.error(f"Error analyzing image: {str(e)}")
                    st.markdown("Please try uploading a different image with better lighting and focus.")
    
    else:
        # Show sample images and instructions when no file is uploaded
        st.info("Please upload an image to begin analysis")
        
        # Display SVG placeholder
        st.markdown("""
        <div style="display: flex; justify-content: center;">
            <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="#f0f0f0" />
                <text x="50%" y="50%" font-family="Arial" font-size="20" fill="#555" text-anchor="middle">Image Preview Area</text>
                <text x="50%" y="65%" font-family="Arial" font-size="14" fill="#777" text-anchor="middle">Upload an image to detect pests</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)
    
    # Common pest and disease information section
    st.markdown("---")
    st.subheader("Common Pests & Diseases")
    
    # Create tabs for different categories
    pest_tab, disease_tab, prevention_tab = st.tabs(["Common Pests", "Common Diseases", "Prevention Tips"])
    
    with pest_tab:
        st.markdown("""
        ### Aphids
        **Signs**: Clusters of small insects on new growth, sticky honeydew, curling leaves  
        **Crops Affected**: Most vegetables, especially cabbage, beans, and tomatoes  
        **Treatment**: Neem oil spray, insecticidal soap, introduce ladybugs
        
        ### Fall Armyworm
        **Signs**: Irregular holes in leaves, sawdust-like waste  
        **Crops Affected**: Maize, sorghum, millet  
        **Treatment**: Early detection, biological controls, specific pesticides
        
        ### Whiteflies
        **Signs**: Small white insects on leaf undersides, yellowing leaves  
        **Crops Affected**: Tomatoes, peppers, sweet potatoes  
        **Treatment**: Yellow sticky traps, insecticidal soap, remove infected leaves
        """)
    
    with disease_tab:
        st.markdown("""
        ### Late Blight
        **Signs**: Dark water-soaked spots on leaves, white mold under leaves  
        **Crops Affected**: Tomatoes, potatoes  
        **Treatment**: Fungicides, remove infected plants, improve air circulation
        
        ### Powdery Mildew
        **Signs**: White powdery spots on leaves and stems  
        **Crops Affected**: Squash, melons, cucumbers  
        **Treatment**: Bicarbonate solutions, neem oil, remove infected parts
        
        ### Cassava Mosaic Disease
        **Signs**: Yellow mottling of leaves, leaf distortion  
        **Crops Affected**: Cassava  
        **Treatment**: Use resistant varieties, remove infected plants, control whiteflies
        """)
    
    with prevention_tab:
        st.markdown("""
        ### Cultural Practices
        - Crop rotation to break pest and disease cycles
        - Adequate plant spacing for better air circulation
        - Regular monitoring of plants
        - Removing crop debris after harvest
        
        ### Natural Controls
        - Introducing beneficial insects (ladybugs, predatory mites)
        - Companion planting to repel pests
        - Organic mulches to suppress disease
        
        ### Timing Strategies
        - Plant early or late to avoid peak pest seasons
        - Time planting to ensure harvest before disease pressure peaks
        - Monitor weather patterns to predict disease outbreaks
        """)
        
    # Historical detections - in a real application, this would come from a database
    st.markdown("---")
    st.subheader("Your Detection History")
    
    # Example historical data - in production this would come from a database
    if st.checkbox("Show detection history"):
        history_data = {
            "Date": ["2023-10-15", "2023-10-10", "2023-09-28", "2023-09-15"],
            "Crop": ["Tomato", "Maize", "Beans", "Tomato"],
            "Detection": ["Early Blight", "Fall Armyworm", "Bean Rust", "Aphids"],
            "Severity": ["Moderate", "High", "Low", "Moderate"],
            "Status": ["Treated", "Treated", "Resolved", "Resolved"]
        }
        
        import pandas as pd
        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True)
