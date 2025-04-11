"""
SmartFarm Application Entry Point
This file is configured to run Streamlit with specific settings for external access.
"""
import os
import sys
import streamlit as st
import app  # Import the main app to run it

if __name__ == "__main__":
    # Force environment variables for external access
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_SERVER_PORT"] = "5000"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    os.environ["STREAMLIT_BROWSER_SERVER_PORT"] = "5000"
    os.environ["STREAMLIT_BROWSER_SERVER_ADDRESS"] = "0.0.0.0"
    
    # Run the main app
    app.main()