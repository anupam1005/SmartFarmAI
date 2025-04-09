import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.weather_api import (
    get_current_weather, get_weather_forecast, get_historical_weather,
    get_agricultural_weather_metrics
)
from db_utils import get_farm_by_id

def show():
    st.title("Weather Insights")
    
    # Get farm ID from session state
    if 'selected_farm_id' not in st.session_state:
        st.error("No farm selected. Please select a farm from the sidebar.")
        return
    
    farm_id = st.session_state['selected_farm_id']
    farm = get_farm_by_id(farm_id)
    
    if not farm or not farm.location:
        st.warning("No location set for this farm. Please update your farm details to include a location.")
        location = "Default Location"
    else:
        location = farm.location
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Current Weather", "Forecast", "Historical Data"])
    
    # CURRENT WEATHER TAB
    with tab1:
        st.header("Current Weather Conditions")
        
        # Location input with default from farm
        weather_location = st.text_input("Location", value=location)
        
        # Get current weather data
        weather_data = get_current_weather(weather_location)
        
        # Display current weather
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Main weather display
            st.subheader(f"Weather for {weather_data['location']}")
            
            # Display date and time
            st.write(f"**Date:** {weather_data['date']}")
            st.write(f"**Time:** {weather_data['time']}")
            
            # Weather metrics
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric("Temperature", f"{weather_data['temperature']}°C")
                st.metric("Humidity", f"{weather_data['humidity']}%")
            
            with metrics_col2:
                st.metric("Precipitation", f"{weather_data['precipitation']} mm")
                st.metric("Condition", weather_data['condition'])
            
            with metrics_col3:
                st.metric("Wind Speed", f"{weather_data['wind_speed']} km/h")
                st.metric("Wind Direction", weather_data['wind_direction'])
            
            # Agricultural metrics
            st.subheader("Agricultural Weather Metrics")
            
            try:
                ag_metrics = get_agricultural_weather_metrics(weather_data)
                
                ag_col1, ag_col2, ag_col3 = st.columns(3)
                
                with ag_col1:
                    st.metric("Growing Degree Days", f"{ag_metrics['growing_degree_days']}°C")
                    st.metric("Vapor Pressure Deficit", f"{ag_metrics['vapor_pressure_deficit']} kPa")
                
                with ag_col2:
                    st.metric("Evapotranspiration", f"{ag_metrics['evapotranspiration']} mm")
                    st.metric("Dew Point", f"{ag_metrics['dew_point']}°C")
                
                with ag_col3:
                    st.metric("Frost Risk", ag_metrics['frost_risk'])
                    st.metric("Heat Stress Risk", ag_metrics['heat_risk'])
            except Exception as e:
                st.error(f"Error calculating agricultural metrics: {e}")
        
        with col2:
            # Weather summary and recommendations
            st.subheader("Farm Recommendations")
            
            # Generate recommendations based on weather conditions
            recommendations = []
            
            # Temperature-based recommendations
            if weather_data['temperature'] < 5:
                recommendations.append("Low temperature alert. Protect sensitive crops from frost damage.")
            elif weather_data['temperature'] > 30:
                recommendations.append("High temperature alert. Ensure adequate irrigation to prevent heat stress.")
            
            # Precipitation-based recommendations
            if weather_data['precipitation'] > 10:
                recommendations.append("Heavy precipitation detected. Check for field drainage issues and potential erosion.")
            elif weather_data['precipitation'] == 0 and weather_data['temperature'] > 25:
                recommendations.append("Hot and dry conditions. Consider increasing irrigation to maintain crop health.")
            
            # Wind-based recommendations
            if weather_data['wind_speed'] > 20:
                recommendations.append("Strong winds detected. Secure any loose equipment and check for crop damage.")
            
            # Display recommendations
            if recommendations:
                for rec in recommendations:
                    st.info(rec)
            else:
                st.success("Weather conditions are favorable for farming activities.")
            
            # Weather-based activity suggestions
            st.subheader("Suggested Activities")
            
            activities = []
            
            # Generate activity suggestions based on weather
            if weather_data['condition'] == "Clear" and 15 <= weather_data['temperature'] <= 30:
                activities.append("Ideal conditions for field work and harvesting.")
            
            if weather_data['condition'] == "Rain":
                activities.append("Delay spraying operations and harvesting.")
                activities.append("Good opportunity for indoor maintenance tasks.")
            
            if weather_data['precipitation'] == 0 and weather_data['humidity'] < 60:
                activities.append("Good conditions for applying foliar treatments.")
            
            # Display activity suggestions
            if activities:
                for activity in activities:
                    st.write(f"• {activity}")
            else:
                st.write("• Regular farm operations can proceed as scheduled.")
    
    # FORECAST TAB
    with tab2:
        st.header("7-Day Weather Forecast")
        
        # Location input with default from farm
        forecast_location = st.text_input("Location", value=location, key="forecast_location")
        
        # Get forecast data
        forecast_data = get_weather_forecast(forecast_location, days=7)
        
        # Convert to DataFrame for easier manipulation
        forecast_df = pd.DataFrame(forecast_data)
        
        # Create temperature trend chart
        st.subheader("Temperature Forecast")
        
        fig = px.line(
            forecast_df,
            x="date",
            y="temperature",
            title="Temperature Trend (°C)",
            markers=True
        )
        
        # Add range for optimal growing temperatures (example: 15-30°C)
        fig.add_shape(
            type="rect",
            x0=forecast_df["date"].min(),
            x1=forecast_df["date"].max(),
            y0=15,
            y1=30,
            fillcolor="rgba(0,255,0,0.1)",
            line=dict(width=0),
            layer="below"
        )
        
        # Customize layout
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create precipitation chart
        st.subheader("Precipitation Forecast")
        
        fig = px.bar(
            forecast_df,
            x="date",
            y="precipitation",
            title="Expected Precipitation (mm)",
            color="precipitation",
            color_continuous_scale="Blues"
        )
        
        # Customize layout
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Precipitation (mm)",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display daily forecast details in an expandable section
        st.subheader("Daily Forecast Details")
        
        for i, day_data in enumerate(forecast_data):
            with st.expander(f"Day {i+1}: {day_data['date']} - {day_data['condition']}", expanded=(i == 0)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Temperature", f"{day_data['temperature']}°C")
                    st.metric("Humidity", f"{day_data['humidity']}%")
                
                with col2:
                    st.metric("Precipitation", f"{day_data['precipitation']} mm")
                    st.metric("Wind Speed", f"{day_data['wind_speed']} km/h")
                
                with col3:
                    st.metric("Condition", day_data['condition'])
                    st.metric("Wind Direction", day_data['wind_direction'])
                
                # Try to get agricultural metrics
                try:
                    ag_metrics = get_agricultural_weather_metrics(day_data)
                    
                    st.subheader("Agricultural Metrics")
                    ag_col1, ag_col2 = st.columns(2)
                    
                    with ag_col1:
                        st.metric("Growing Degree Days", f"{ag_metrics['growing_degree_days']}°C")
                        st.metric("Evapotranspiration", f"{ag_metrics['evapotranspiration']} mm")
                    
                    with ag_col2:
                        st.metric("Frost Risk", ag_metrics['frost_risk'])
                        st.metric("Heat Risk", ag_metrics['heat_risk'])
                except Exception:
                    pass
    
    # HISTORICAL DATA TAB
    with tab3:
        st.header("Historical Weather Data")
        
        # Location input with default from farm
        historical_location = st.text_input("Location", value=location, key="historical_location")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date", 
                value=datetime.now() - timedelta(days=30),
                max_value=datetime.now()
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Get historical data
        if start_date <= end_date:
            historical_data = get_historical_weather(historical_location, start_date, end_date)
            
            # Convert to DataFrame
            hist_df = pd.DataFrame(historical_data)
            
            # Create temperature trend chart
            st.subheader("Historical Temperature Trends")
            
            fig = px.line(
                hist_df,
                x="date",
                y="temperature",
                title="Temperature History (°C)",
                markers=True
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Temperature (°C)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create precipitation chart
            st.subheader("Historical Precipitation")
            
            fig = px.bar(
                hist_df,
                x="date",
                y="precipitation",
                title="Precipitation History (mm)",
                color="precipitation",
                color_continuous_scale="Blues"
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Precipitation (mm)",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display statistics
            st.subheader("Weather Statistics")
            
            # Temperature stats
            temp_mean = hist_df["temperature"].mean()
            temp_max = hist_df["temperature"].max()
            temp_min = hist_df["temperature"].min()
            
            # Precipitation stats
            precip_total = hist_df["precipitation"].sum()
            precip_days = (hist_df["precipitation"] > 0).sum()
            
            # Display statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg. Temperature", f"{temp_mean:.1f}°C")
                st.metric("Rainfall Days", f"{precip_days}")
            
            with col2:
                st.metric("Max. Temperature", f"{temp_max:.1f}°C")
                st.metric("Total Rainfall", f"{precip_total:.1f} mm")
            
            with col3:
                st.metric("Min. Temperature", f"{temp_min:.1f}°C")
                if end_date - start_date > timedelta(days=0):
                    st.metric("Daily Avg. Rainfall", f"{precip_total / (end_date - start_date).days:.1f} mm")
            
            # Weather distribution
            st.subheader("Weather Condition Distribution")
            
            # Count occurrences of each condition
            condition_counts = hist_df["condition"].value_counts().reset_index()
            condition_counts.columns = ["Condition", "Count"]
            
            # Create pie chart
            fig = px.pie(
                condition_counts,
                names="Condition",
                values="Count",
                title="Weather Condition Distribution"
            )
            
            # Customize layout
            fig.update_layout(
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Raw data table
            with st.expander("View Raw Data"):
                st.dataframe(hist_df, hide_index=True)
        else:
            st.error("End date must be after start date.")