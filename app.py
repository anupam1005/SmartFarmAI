import streamlit as st
import os
import sys

# Add the current directory to path to allow importing from local modules
sys.path.append('.')
from pages.dashboard import show as dashboard_show
from pages.pest_detection import show as pest_detection_show
from pages.resource_management import show as resource_management_show
from pages.weather import show as weather_show
from pages.crop_recommendation import show as crop_recommendation_show

# Set page configuration
st.set_page_config(
    page_title="SmartFarm - AI for Smallholder Farmers",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("🌱 SmartFarm")
st.subheader("AI-powered platform for smallholder farmers")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Pest & Disease Detection", "Resource Management", "Weather Insights", "Crop Recommendations"]
)

# Display user information in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Farm Information")
farm_name = st.sidebar.text_input("Farm Name", "My Farm")
location = st.sidebar.text_input("Location", "")
farm_size = st.sidebar.number_input("Farm Size (hectares)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
st.sidebar.markdown("---")
st.sidebar.info("SmartFarm helps smallholder farmers optimize crop health, detect pests, and manage resources efficiently.")

# Main content based on navigation
if page == "Dashboard":
    dashboard_show()
elif page == "Pest & Disease Detection":
    pest_detection_show()
elif page == "Resource Management":
    resource_management_show()
elif page == "Weather Insights":
    weather_show()
elif page == "Crop Recommendations":
    crop_recommendation_show()

# Footer
st.markdown("---")
st.caption("© 2023 SmartFarm - AI-powered farming solutions for smallholder farmers")
