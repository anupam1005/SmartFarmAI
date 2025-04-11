#!/usr/bin/env python
"""
SmartFarm Application Launcher
This file configures and starts the Streamlit application with external access settings
"""
import os
import subprocess
import sys

def main():
    """Configure and start the Streamlit application"""
    # Define command with all parameters to enable external access
    command = [
        "streamlit", "run", "app.py",
        "--server.address=0.0.0.0",
        "--server.port=5000",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--global.developmentMode=false",
        "--browser.serverPort=5000",
        "--browser.serverAddress=0.0.0.0"
    ]
    
    # Set environment variables to force external access
    env = os.environ.copy()
    env["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    env["STREAMLIT_SERVER_PORT"] = "5000"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    env["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    env["STREAMLIT_BROWSER_SERVER_PORT"] = "5000"
    env["STREAMLIT_BROWSER_SERVER_ADDRESS"] = "0.0.0.0"
    
    print("Starting Streamlit with external access configuration...")
    process = None
    try:
        # Run the process and wait for it to complete
        process = subprocess.Popen(command, env=env)
        process.wait()
    except KeyboardInterrupt:
        print("Shutting down Streamlit server...")
        if process:
            process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        if process:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()