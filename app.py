import streamlit as st
import os
from datetime import datetime
from database import create_tables, init_db

# Import page modules
from pages import dashboard, crop_recommendation, pest_detection, resource_management, weather
from utils.weather_api import get_current_weather, format_weather_for_display, get_icon_url
from pages.weather import get_condition_icon

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
    
    # Add weather widget in top right corner
    display_weather_widget()
    
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

def display_weather_widget():
    """Display a compact weather widget in the top right corner"""
    # Get all farms to find a default location
    try:
        from db_utils import get_all_farms
        
        farms = get_all_farms()
        default_location = farms[0].location if farms and farms[0].location else "London"
        
        # Add custom CSS for the weather widget
        st.markdown("""
        <style>
        .weather-widget {
            position: fixed;
            top: 10px;
            right: 10px;
            background-color: #f0f8ff;
            border-radius: 5px;
            padding: 8px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 200px;
            font-size: 12px;
            text-align: center;
        }
        .weather-widget img {
            margin: 0 auto;
            display: block;
            width: 40px;
        }
        .temperature {
            font-size: 16px;
            font-weight: bold;
            margin: 2px 0;
        }
        .location {
            font-weight: bold;
            color: #1E88E5;
        }
        .condition {
            margin-bottom: 2px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get current weather data
        weather_data = get_current_weather(default_location)
        
        if weather_data:
            # Format for display
            display_data = format_weather_for_display(weather_data)
            
            # Create the weather widget HTML
            icon_url = get_icon_url(display_data['icon'])
            
            weather_html = f"""
            <div class="weather-widget">
                <div class="location">{display_data['location']}</div>
                <img src="{icon_url}" alt="{display_data['conditions']}">
                <div class="temperature">{display_data['temperature']}</div>
                <div class="condition">{display_data['conditions']}</div>
                <div class="humidity">Humidity: {display_data['humidity']}</div>
            </div>
            """
            
            # Display the widget
            st.markdown(weather_html, unsafe_allow_html=True)
    except Exception as e:
        # Silently fail if there's an error with the weather widget
        pass

if __name__ == "__main__":
    main()