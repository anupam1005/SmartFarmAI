import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import weather_api

def show():
    st.header("Weather Insights")
    
    # Location input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        location = st.text_input("Farm Location", "")
        if not location:
            st.info("Enter your location to get weather data specific to your farm")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Get Weather Data"):
            st.success("Weather data updated!")
    
    # Current weather information
    st.subheader("Current Weather Conditions")
    
    try:
        # Get current weather data
        current_weather = weather_api.get_current_weather(location)
        
        # Display current weather in three columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Temperature", f"{current_weather.get('temp', 'N/A')}°C", 
                     delta=f"{current_weather.get('temp_change', 0)}°C from yesterday")
            st.metric("Humidity", f"{current_weather.get('humidity', 'N/A')}%")
        
        with col2:
            st.metric("Wind Speed", f"{current_weather.get('wind_speed', 'N/A')} km/h")
            st.metric("Precipitation", f"{current_weather.get('precipitation', 'N/A')} mm")
        
        with col3:
            st.metric("UV Index", current_weather.get('uv_index', 'N/A'))
            st.metric("Soil Moisture", f"{current_weather.get('soil_moisture', 'N/A')}%")
        
    except Exception as e:
        st.warning(f"Unable to fetch current weather data. Please check your internet connection and location input.")
        
        # Example data as fallback
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Temperature", "N/A")
            st.metric("Humidity", "N/A")
        
        with col2:
            st.metric("Wind Speed", "N/A")
            st.metric("Precipitation", "N/A")
        
        with col3:
            st.metric("UV Index", "N/A")
            st.metric("Soil Moisture", "N/A")
    
    # Weather forecast
    st.subheader("7-Day Weather Forecast")
    
    try:
        # Get forecast data
        forecast = weather_api.get_weather_forecast(location)
        
        if forecast and len(forecast) > 0:
            # Convert forecast to DataFrame
            forecast_df = pd.DataFrame(forecast)
            
            # Create temperature forecast chart
            temp_fig = px.line(
                forecast_df,
                x='date',
                y=['temp_max', 'temp_min'],
                labels={'value': 'Temperature (°C)', 'variable': 'Measurement', 'date': 'Date'},
                title='Temperature Forecast',
                color_discrete_map={'temp_max': 'red', 'temp_min': 'blue'}
            )
            
            temp_fig.update_layout(height=300)
            st.plotly_chart(temp_fig, use_container_width=True)
            
            # Create precipitation forecast chart
            precip_fig = px.bar(
                forecast_df,
                x='date',
                y='precipitation',
                labels={'precipitation': 'Precipitation (mm)', 'date': 'Date'},
                title='Precipitation Forecast',
                color='precipitation',
                color_continuous_scale=px.colors.sequential.Blues
            )
            
            precip_fig.update_layout(height=250)
            st.plotly_chart(precip_fig, use_container_width=True)
            
            # Display daily forecast cards
            st.subheader("Daily Forecast Details")
            
            # Create columns for the first 4 days
            cols = st.columns(4)
            
            # Display forecast details for each day
            for i, (col, (_, day)) in enumerate(zip(cols, forecast_df.iterrows())):
                with col:
                    st.markdown(f"**{day['date']}**")
                    st.markdown(f"**{day['condition']}**")
                    st.markdown(f"🌡️ {day['temp_max']}°C / {day['temp_min']}°C")
                    st.markdown(f"💧 {day['precipitation']} mm")
                    st.markdown(f"💨 {day['wind_speed']} km/h")
            
            # Create columns for the next 3 days
            if len(forecast_df) > 4:
                cols = st.columns(4)
                for i, (col, (_, day)) in enumerate(zip(cols, forecast_df.iloc[4:].iterrows())):
                    with col:
                        st.markdown(f"**{day['date']}**")
                        st.markdown(f"**{day['condition']}**")
                        st.markdown(f"🌡️ {day['temp_max']}°C / {day['temp_min']}°C")
                        st.markdown(f"💧 {day['precipitation']} mm")
                        st.markdown(f"💨 {day['wind_speed']} km/h")
        
        else:
            st.info("No forecast data available. Please check your location.")
            
    except Exception as e:
        st.warning(f"Unable to fetch weather forecast. Please check your internet connection and location input.")
        
        # Show example forecast as fallback
        dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        example_forecast = {
            'date': dates,
            'temp_max': [28, 27, 29, 30, 28, 26, 27],
            'temp_min': [18, 17, 19, 20, 19, 16, 17],
            'precipitation': [0, 5, 20, 10, 0, 0, 5],
            'condition': ['Sunny', 'Partly Cloudy', 'Rain', 'Scattered Showers', 'Sunny', 'Sunny', 'Partly Cloudy'],
            'wind_speed': [5, 8, 12, 10, 7, 6, 9]
        }
        
        forecast_df = pd.DataFrame(example_forecast)
        
        st.info("Showing example forecast data. Enter a valid location for actual weather data.")
        
        # Create example temperature forecast chart
        temp_fig = px.line(
            forecast_df,
            x='date',
            y=['temp_max', 'temp_min'],
            labels={'value': 'Temperature (°C)', 'variable': 'Measurement', 'date': 'Date'},
            title='Example Temperature Forecast',
            color_discrete_map={'temp_max': 'red', 'temp_min': 'blue'}
        )
        
        temp_fig.update_layout(height=300)
        st.plotly_chart(temp_fig, use_container_width=True)
    
    # Weather alerts and advisories
    st.subheader("Weather Alerts & Farming Advisories")
    
    alerts = [
        {
            "type": "Heavy Rain",
            "severity": "Moderate",
            "description": "Heavy rainfall expected in the next 48 hours. Consider postponing fertilizer application.",
            "recommendations": "Ensure proper drainage in your fields. Cover sensitive seedlings."
        },
        {
            "type": "Dry Spell",
            "severity": "Low",
            "description": "Below-average rainfall expected next week.",
            "recommendations": "Prepare irrigation systems. Consider mulching to retain soil moisture."
        }
    ]
    
    for alert in alerts:
        severity_color = "orange" if alert["severity"] == "Moderate" else "yellow" if alert["severity"] == "Low" else "red"
        
        st.markdown(f"""
        <div style='padding: 10px; border-left: 5px solid {severity_color}; background-color: rgba(255, 255, 255, 0.1);'>
            <h4 style='margin-top: 0;'>{alert['type']} - {alert['severity']} Alert</h4>
            <p>{alert['description']}</p>
            <p><strong>Recommendations:</strong> {alert['recommendations']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Weather patterns and almanac
    st.subheader("Weather Patterns & Historical Data")
    
    # Example historical data - in a real app, this would come from historical weather API
    # Creating example rainfall patterns
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    historical_data = {
        'Month': months,
        'This Year': [20, 25, 40, 80, 120, 150, 130, 100, 80, 45, 30, 25],
        'Last Year': [25, 30, 45, 90, 110, 140, 120, 90, 70, 50, 35, 30],
        'Average': [22, 28, 42, 85, 115, 145, 125, 95, 75, 48, 32, 27]
    }
    
    hist_df = pd.DataFrame(historical_data)
    
    # Create historical rainfall chart
    hist_fig = px.line(
        hist_df,
        x='Month',
        y=['This Year', 'Last Year', 'Average'],
        labels={'value': 'Rainfall (mm)', 'variable': 'Period'},
        title='Monthly Rainfall Comparison',
        markers=True
    )
    
    hist_fig.update_layout(height=400)
    st.plotly_chart(hist_fig, use_container_width=True)
    
    # Weather-based farming recommendations
    with st.expander("Weather-Based Farming Recommendations"):
        st.markdown("""
        ### Current Recommendations
        
        - **Planting**: Given the current rainfall pattern, it's a good time to plant drought-resistant varieties
        - **Harvesting**: Schedule harvesting activities for the end of the week when dry conditions are expected
        - **Pest Control**: Increased humidity may lead to fungal diseases - monitor crops closely
        - **Irrigation**: Reduce irrigation for the next 3 days due to expected rainfall
        
        ### Seasonal Outlook
        
        - The coming month is expected to have above-average rainfall
        - Consider planting crops that benefit from higher moisture levels
        - Prepare drainage systems to prevent waterlogging
        """)
