import streamlit as st
import os
from datetime import datetime
from database import create_tables, init_db

# Import page modules
from pages import dashboard, crop_recommendation, pest_detection, resource_management, weather

# Initialize database
init_db()

# Set up page configuration
st.set_page_config(
    page_title="SmartFarm - Farm Management Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #5A5A5A;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    
    .stButton button {
        background-color: #2E7D32;
        color: white;
    }
    
    .stButton button:hover {
        background-color: #1B5E20;
        color: white;
    }
    
    .metric-container {
        background-color: #f7f7f7;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
    }
    
    footer {visibility: hidden;}
    .css-18e3th9 {padding-top: 1rem;}
    .css-18e3th9 {padding-bottom: 1rem;}
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("🌱 SmartFarm")
        st.markdown("#### AI-Powered Farm Management")
        
        # Show farm stats in sidebar
        display_farm_stats()
        
        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Crop Recommendation", "Pest Detection", "Resource Management", "Weather"]
        )
        
        # App information
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "SmartFarm helps smallholder farmers optimize crop health, detect pests, and manage resources effectively using AI technology."
        )
        st.markdown(f"**Version:** 1.0.0")
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%B %d, %Y')}")
    
    # Display selected page
    if page == "Dashboard":
        dashboard.show()
    elif page == "Crop Recommendation":
        crop_recommendation.show()
    elif page == "Pest Detection":
        pest_detection.show()
    elif page == "Resource Management":
        resource_management.show()
    elif page == "Weather":
        weather.show()

def display_farm_stats():
    """Display farm statistics in the sidebar"""
    try:
        from db_utils import get_all_farms, get_fields_count, get_health_records_count, get_pest_detections_count
        
        farms_count = len(get_all_farms())
        fields_count = get_fields_count()
        health_records_count = get_health_records_count()
        pest_records_count = get_pest_detections_count()
        
        # Display stats
        st.markdown("### Farm Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Farms:** {farms_count}")
            st.markdown(f"**Fields:** {fields_count}")
        with col2:
            st.markdown(f"**Health Records:** {health_records_count}")
            st.markdown(f"**Pest Detections:** {pest_records_count}")
        
        st.markdown("---")
    except Exception as e:
        st.sidebar.warning("Database not ready. Initialize database to view statistics.")

if __name__ == "__main__":
    main()