import streamlit as st
import os
from datetime import datetime
from database import init_db
from db_utils import get_all_farms, setup_demo_farm

# Import page modules
from pages.dashboard import show as dashboard_show
from pages.pest_detection import show as pest_detection_show
from pages.resource_management import show as resource_management_show
from pages.weather import show as weather_show
from pages.crop_recommendation import show as crop_recommendation_show

# App configuration
st.set_page_config(
    page_title="SmartFarm - Precision Agriculture Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Create demo farm if none exists
setup_demo_farm()

# Custom CSS
with open(".streamlit/style.css", "w") as f:
    f.write("""
    /* Custom CSS for the SmartFarm App */
    .css-18e3th9 {
        padding-top: 1rem;
    }
    
    /* Better header styling */
    h1, h2, h3 {
        margin-bottom: 1rem;
    }
    
    /* Improve spacing for metrics */
    div.stMetric {
        background-color: rgba(28, 131, 225, 0.1);
        padding: 15px;
        border-radius: 5px;
    }
    
    /* Format buttons */
    .stButton > button {
        width: 100%;
    }
    
    /* Better dataframe styling */
    .dataframe {
        font-size: 0.9rem;
    }
    """)

st.markdown(f'<style>{open(".streamlit/style.css").read()}</style>', unsafe_allow_html=True)

# Authentication placeholder
# In a real application, we would implement proper user authentication here
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = True

# Initialize session state variables
if 'selected_farm_id' not in st.session_state:
    farms = get_all_farms()
    if farms:
        st.session_state['selected_farm_id'] = farms[0].id

# Sidebar
with st.sidebar:
    st.image("assets/default_farm.svg", width=100)
    st.title("SmartFarm")
    st.caption("Precision Agriculture Platform")
    
    # Farm selection
    farms = get_all_farms()
    if farms:
        farm_options = {farm.name: farm.id for farm in farms}
        selected_farm_name = st.selectbox(
            "Select Farm",
            list(farm_options.keys())
        )
        st.session_state['selected_farm_id'] = farm_options[selected_farm_name]
    else:
        st.error("No farms found in the database.")
    
    st.divider()
    
    # Navigation
    st.subheader("Navigation")
    pages = {
        "Dashboard": dashboard_show,
        "Pest & Disease Detection": pest_detection_show,
        "Resource Management": resource_management_show,
        "Weather Insights": weather_show,
        "Crop Recommendations": crop_recommendation_show
    }
    
    selected_page = st.radio("Select Page", list(pages.keys()))
    
    st.divider()
    
    # Display date and time
    st.caption(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # App information
    st.sidebar.info("""
    **SmartFarm v1.0**
    An AI-powered platform for smallholder farmers.
    """)

# Display the selected page
if st.session_state['authenticated']:
    pages[selected_page]()
else:
    st.warning("Please login to access the SmartFarm platform.")
    
    # Simple login form (placeholder)
    with st.form("login_form"):
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # In a real application, we would validate credentials here
            st.session_state['authenticated'] = True
            st.experimental_rerun()