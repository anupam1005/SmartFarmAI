"""
SmartFarm Application Entry Point
This file is configured to run Streamlit with specific settings for external access.
"""
import os
import sys
import streamlit.web.bootstrap as bootstrap
from streamlit.web.server import Server

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the app module
from app import main

# Set up Streamlit config
if __name__ == "__main__":
    # Configuration for external access
    bootstrap_args = {
        "server.address": "0.0.0.0",
        "server.port": 5000,
        "server.headless": True,
        "server.enableCORS": False,
        "server.enableXsrfProtection": False,
        "browser.serverAddress": "0.0.0.0",
        "global.developmentMode": False
    }
    
    # Run the Streamlit application with these arguments
    bootstrap.run(main, "", args=[], flag_options=bootstrap_args)