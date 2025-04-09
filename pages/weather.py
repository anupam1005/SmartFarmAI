import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

from utils.weather_api import (
    get_current_weather, 
    get_weather_forecast, 
    get_historical_weather,
    format_weather_for_display,
    get_icon_url,
    calculate_growing_degree_days,
    calculate_chill_hours
)

from db_utils import (
    get_all_farms,
    save_weather_record,
    get_weather_history,
    get_latest_weather
)

def show():
    st.markdown("<h1 class='main-header'>Weather Monitoring</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Monitor weather conditions and forecasts for your farm</p>", unsafe_allow_html=True)
    
    # Farm location selection
    farms = get_all_farms()
    
    if not farms:
        st.warning("No farms found. Please add a farm to track weather.")
        return
    
    # Get locations from farms
    locations = [farm.location for farm in farms if farm.location]
    
    # Add custom location option
    if locations:
        locations = ["Custom Location"] + locations
    else:
        locations = ["Custom Location"]
    
    location_option = st.selectbox("Select Location", locations)
    
    if location_option == "Custom Location":
        location = st.text_input("Enter location (city, country or coordinates)", "")
    else:
        location = location_option
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Current Weather", "Forecast", "Historical Data"])
    
    if location:
        # Current Weather Tab
        with tab1:
            show_current_weather(location)
        
        # Forecast Tab
        with tab2:
            show_weather_forecast(location)
        
        # Historical Weather Tab
        with tab3:
            show_historical_weather(location)
    else:
        for tab in [tab1, tab2, tab3]:
            with tab:
                st.info("Please select or enter a location to view weather data.")

def show_current_weather(location):
    """Show current weather conditions for a location"""
    st.header("Current Weather")
    
    # Check if we have recent weather data in database
    latest_weather = get_latest_weather(location)
    
    # If data is older than 1 hour, fetch new data
    if not latest_weather or (datetime.now() - latest_weather.date).total_seconds() > 3600:
        with st.spinner("Fetching current weather data..."):
            weather_data = get_current_weather(location)
            
            # Save to database if successful
            if weather_data and not weather_data.get('simulated', False):
                save_weather_record(
                    location=weather_data['location'],
                    temperature=weather_data['temperature'],
                    humidity=weather_data['humidity'],
                    precipitation=weather_data['precipitation'],
                    wind_speed=weather_data['wind_speed'],
                    wind_direction=weather_data['wind_direction'],
                    condition=weather_data['conditions']
                )
    else:
        # Use data from database
        weather_data = {
            'location': latest_weather.location,
            'temperature': latest_weather.temperature,
            'humidity': latest_weather.humidity,
            'precipitation': latest_weather.precipitation,
            'wind_speed': latest_weather.wind_speed,
            'wind_direction': latest_weather.wind_direction,
            'conditions': latest_weather.condition,
            'timestamp': latest_weather.date.strftime('%Y-%m-%d %H:%M:%S'),
            'icon': get_condition_icon(latest_weather.condition)
        }
    
    # Format data for display
    display_data = format_weather_for_display(weather_data) if weather_data else None
    
    if display_data:
        # Show simulated data notice if applicable
        if weather_data.get('simulated', False):
            st.info("⚠️ Using simulated weather data. Add an OpenWeatherMap API key for real data.")
        
        # Weather display layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Weather icon and condition
            icon_url = get_icon_url(display_data['icon'])
            st.image(icon_url, width=100)
            st.markdown(f"<h2 style='margin-top: -15px; text-align: center;'>{display_data['conditions']}</h2>", unsafe_allow_html=True)
        
        with col2:
            # Location and main data
            st.markdown(f"<h2>{display_data['location']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p>{display_data['date']} | {display_data['time']}</p>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 48px; font-weight: bold;'>{display_data['temperature']}</span>
                <div style='margin-left: 20px;'>
                    <div>Feels like: {display_data['feels_like']}</div>
                    <div>Humidity: {display_data['humidity']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional metrics
        st.markdown("### Weather Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Wind", display_data['wind'])
        
        with col2:
            st.metric("Precipitation", display_data['precipitation'])
        
        with col3:
            st.metric("Humidity", display_data['humidity'])
        
        # Agricultural impact section
        st.markdown("### Agricultural Impact")
        
        # Growing conditions assessment based on crop requirements
        temp = weather_data['temperature']
        humidity = weather_data['humidity']
        
        # Simple assessment of growing conditions
        if 15 <= temp <= 30 and 40 <= humidity <= 80:
            condition = "Favorable"
            condition_color = "#4CAF50"
        elif (10 <= temp < 15 or 30 < temp <= 35) and (30 <= humidity < 40 or 80 < humidity <= 90):
            condition = "Moderate"
            condition_color = "#FF9800"
        else:
            condition = "Challenging"
            condition_color = "#F44336"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='metric-container'>
                <div style='font-size: 16px; color: #666;'>Current Growing Conditions</div>
                <div style='font-size: 24px; font-weight: bold; color: {condition_color};'>{condition}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Activity recommendations based on weather
            st.markdown("#### Recommended Activities")
            
            if weather_data['conditions'] == "Rain" or weather_data['precipitation'] > 5:
                st.markdown("- Postpone spraying and fertilizer application")
                st.markdown("- Check drainage systems")
                st.markdown("- Monitor for disease pressure")
            elif weather_data['conditions'] == "Clear" and temp > 30:
                st.markdown("- Ensure adequate irrigation")
                st.markdown("- Apply mulch to conserve moisture")
                st.markdown("- Consider shade for sensitive crops")
            elif weather_data['wind_speed'] > 10:
                st.markdown("- Postpone spraying operations")
                st.markdown("- Check for structural damage")
                st.markdown("- Provide wind protection for seedlings")
            else:
                st.markdown("- Ideal for general field operations")
                st.markdown("- Good conditions for spraying if needed")
                st.markdown("- Regular monitoring recommended")
        
        with col2:
            # Risk assessment
            risks = []
            
            if temp < 5:
                risks.append(("Frost Risk", "High" if temp < 0 else "Medium"))
            elif temp > 35:
                risks.append(("Heat Stress", "High" if temp > 38 else "Medium"))
            
            if weather_data['conditions'] in ["Rain", "Drizzle"] or weather_data['precipitation'] > 0:
                disease_risk = "High" if humidity > 80 and temp > 15 else "Medium"
                risks.append(("Disease Pressure", disease_risk))
            
            if weather_data['wind_speed'] > 8:
                wind_risk = "High" if weather_data['wind_speed'] > 15 else "Medium"
                risks.append(("Wind Damage", wind_risk))
            
            if len(risks) == 0:
                risks.append(("Overall Risk", "Low"))
            
            st.markdown("#### Risk Assessment")
            
            for risk, level in risks:
                level_color = "#F44336" if level == "High" else "#FF9800" if level == "Medium" else "#4CAF50"
                st.markdown(f"""
                <div style='margin-bottom: 10px;'>
                    <div style='font-size: 14px; color: #666;'>{risk}</div>
                    <div style='font-size: 18px; font-weight: bold; color: {level_color};'>{level}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error(f"Unable to fetch weather data for {location}. Please check location name and try again.")

def show_weather_forecast(location):
    """Show weather forecast for a location"""
    st.header("Weather Forecast")
    
    # Allow user to select forecast range
    days = st.slider("Forecast Days", 1, 5, 3)
    
    with st.spinner("Fetching forecast data..."):
        forecast_data = get_weather_forecast(location, days=days)
    
    if forecast_data:
        # Show simulated data notice if applicable
        if forecast_data.get('simulated', False):
            st.info("⚠️ Using simulated forecast data. Add an OpenWeatherMap API key for real forecast data.")
        
        # Format data for display
        display_data = format_weather_for_display(forecast_data)
        
        if display_data:
            st.subheader(f"Forecast for {display_data['location']}")
            
            # Group forecasts by day
            days_data = display_data['days']
            
            # Create forecast cards
            for day, items in days_data.items():
                st.markdown(f"### {day}")
                
                # Create grid with forecast periods
                cols = st.columns(min(4, len(items)))
                
                for i, item in enumerate(items[:len(cols)]):
                    with cols[i]:
                        st.markdown(f"""
                        <div style='text-align: center; padding: 10px; background-color: #f0f8f0; border-radius: 5px;'>
                            <div style='font-weight: bold;'>{item['time']}</div>
                            <img src='{get_icon_url(item['icon'])}' width='50'>
                            <div style='font-size: 20px; font-weight: bold;'>{item['temperature']}</div>
                            <div>{item['conditions']}</div>
                            <div>💧 {item['humidity']}</div>
                            <div>💨 {item['wind']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Calculate chill hours if relevant
            chill_hours = calculate_chill_hours(forecast_data)
            
            if chill_hours:
                st.subheader("Chill Hours Forecast")
                st.info(f"Predicted chill hours for the forecast period: {chill_hours['total_chill_hours']} hours")
                
                # Create chart of daily chill hours
                chill_df = pd.DataFrame({
                    'Date': chill_hours['chart_data']['dates'],
                    'Chill Hours': chill_hours['chart_data']['daily_chill']
                })
                
                fig = px.bar(
                    chill_df,
                    x='Date',
                    y='Chill Hours',
                    title="Predicted Daily Chill Hours",
                    color='Chill Hours',
                    color_continuous_scale=px.colors.sequential.Blues
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Agricultural forecast insights
            st.subheader("Agricultural Forecast Insights")
            
            # Extract conditions for analysis
            all_forecast_items = []
            for day_items in days_data.values():
                all_forecast_items.extend(day_items)
            
            # Check for conditions that impact farming
            rain_periods = [item for item in all_forecast_items if 'rain' in item['conditions'].lower() or 'shower' in item['conditions'].lower()]
            wind_periods = [item for item in all_forecast_items if float(item['wind'].split()[0]) > 5]
            
            # Show insights
            if rain_periods:
                rain_times = [f"{item['date']} at {item['time']}" for item in rain_periods[:3]]
                st.warning(f"⚠️ Rain expected: {', '.join(rain_times)}")
                
                total_rain = sum([float(item['precipitation'].split()[0]) for item in rain_periods])
                st.markdown(f"Total expected precipitation: {total_rain:.1f} mm")
            
            if wind_periods:
                st.warning(f"⚠️ Windy conditions expected during {len(wind_periods)} forecast periods")
            
            # Spraying conditions assessment
            good_spray_periods = [
                item for item in all_forecast_items 
                if float(item['wind'].split()[0]) < 5 and 'rain' not in item['conditions'].lower() 
                and float(item['temperature'].rstrip('°C')) > 10
            ]
            
            if good_spray_periods:
                spray_times = [f"{item['date']} at {item['time']}" for item in good_spray_periods[:3]]
                st.success(f"✅ Good spraying conditions: {', '.join(spray_times)}")
        else:
            st.error("Error formatting forecast data.")
    else:
        st.error(f"Unable to fetch forecast data for {location}. Please check location name and try again.")

def show_historical_weather(location):
    """Show historical weather data and agricultural metrics"""
    st.header("Historical Weather Data")
    
    # Time period selection
    period_options = {
        "7 days": 7,
        "14 days": 14,
        "30 days": 30,
        "60 days": 60,
        "90 days": 90
    }
    
    selected_period = st.selectbox("Select Time Period", list(period_options.keys()))
    days = period_options[selected_period]
    
    # Get historical data from database first
    db_historical = get_weather_history(location, days=days)
    
    if not db_historical or len(db_historical) < days // 2:  # If insufficient data in DB
        with st.spinner(f"Fetching historical weather data for the past {days} days..."):
            # Get simulated historical data
            historical_data = get_historical_weather(location, days=days)
            
            # Save to database if not simulated
            if historical_data and not historical_data[0].get('simulated', True):
                for record in historical_data:
                    save_weather_record(
                        location=record['location'],
                        temperature=record['temperature'],
                        humidity=record['humidity'],
                        precipitation=record['precipitation'],
                        wind_speed=record['wind_speed'],
                        wind_direction=record['wind_direction'],
                        condition=record['conditions']
                    )
    else:
        # Convert database records to the same format
        historical_data = []
        for record in db_historical:
            historical_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'location': record.location,
                'temperature': record.temperature,
                'humidity': record.humidity,
                'precipitation': record.precipitation,
                'wind_speed': record.wind_speed,
                'wind_direction': record.wind_direction,
                'conditions': record.condition
            })
    
    if historical_data:
        # Show simulated data notice if applicable
        if historical_data[0].get('simulated', False):
            st.info("⚠️ Using simulated historical data. Add a weather API key for real historical data.")
        
        # Create DataFrame for visualization
        hist_df = pd.DataFrame(historical_data)
        
        # Convert date strings to datetime objects if needed
        if isinstance(hist_df['date'][0], str):
            hist_df['date'] = pd.to_datetime(hist_df['date'])
        
        # Sort by date
        hist_df = hist_df.sort_values('date')
        
        # Show historical data visualization
        st.subheader("Temperature Trends")
        
        fig = px.line(
            hist_df, 
            x='date', 
            y='temperature',
            title=f"Temperature History - Past {days} Days",
            labels={"temperature": "Temperature (°C)", "date": "Date"}
        )
        
        # Add daily min/max range
        daily_data = hist_df.groupby(hist_df['date'].dt.date).agg({
            'temperature': ['min', 'max', 'mean']
        }).reset_index()
        
        # Rename columns
        daily_data.columns = ['date', 'min_temp', 'max_temp', 'avg_temp']
        
        fig2 = px.line(
            daily_data,
            x='date',
            y=['min_temp', 'max_temp', 'avg_temp'],
            title="Daily Temperature Range",
            labels={
                "date": "Date", 
                "value": "Temperature (°C)",
                "variable": "Metric"
            },
            color_discrete_map={
                "min_temp": "blue",
                "max_temp": "red",
                "avg_temp": "green"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Create additional visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Precipitation history
            fig_precip = px.bar(
                hist_df,
                x='date',
                y='precipitation',
                title="Precipitation History",
                labels={"precipitation": "Precipitation (mm)", "date": "Date"},
                color='precipitation',
                color_continuous_scale=px.colors.sequential.Blues
            )
            st.plotly_chart(fig_precip, use_container_width=True)
        
        with col2:
            # Humidity history
            fig_humidity = px.line(
                hist_df,
                x='date',
                y='humidity',
                title="Humidity History",
                labels={"humidity": "Humidity (%)", "date": "Date"}
            )
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        # Calculate and show Growing Degree Days
        gdd = calculate_growing_degree_days(historical_data)
        
        if gdd:
            st.subheader("Growing Degree Days (GDD)")
            
            # Explanation
            st.markdown("""
            Growing Degree Days (GDD) measure heat accumulation to predict plant and pest development.
            The base temperature used is 10°C (50°F), common for many crops.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # GDD metrics
                st.metric("Total GDD", f"{gdd['total_gdd']:.1f}")
                st.metric("Average Daily GDD", f"{gdd['avg_daily_gdd']:.1f}")
            
            with col2:
                # Min/Max
                st.metric("Maximum Daily GDD", f"{gdd['max_daily_gdd']:.1f}")
                st.metric("Minimum Daily GDD", f"{gdd['min_daily_gdd']:.1f}")
            
            # GDD chart
            gdd_df = pd.DataFrame({
                'Date': gdd['chart_data']['dates'],
                'Daily GDD': gdd['chart_data']['daily_gdd'],
                'Cumulative GDD': gdd['chart_data']['cumulative_gdd']
            })
            
            fig_gdd = px.bar(
                gdd_df,
                x='Date',
                y='Daily GDD',
                title="Daily Growing Degree Days",
                labels={"Daily GDD": "GDD", "Date": "Date"},
                color='Daily GDD',
                color_continuous_scale=px.colors.sequential.Greens
            )
            
            fig_cum_gdd = px.line(
                gdd_df,
                x='Date',
                y='Cumulative GDD',
                title="Cumulative Growing Degree Days",
                labels={"Cumulative GDD": "GDD", "Date": "Date"}
            )
            
            st.plotly_chart(fig_gdd, use_container_width=True)
            st.plotly_chart(fig_cum_gdd, use_container_width=True)
            
            # Show crop development implications
            st.subheader("Crop Development Implications")
            
            total_gdd = gdd['total_gdd']
            
            # Simple GDD thresholds for common crops
            gdd_thresholds = {
                "Corn": {
                    "Emergence": 125,
                    "4-leaf stage": 345,
                    "8-leaf stage": 780,
                    "Tasseling": 1135,
                    "Maturity": 2000
                },
                "Wheat": {
                    "Emergence": 100,
                    "Tillering": 300,
                    "Jointing": 600,
                    "Heading": 900,
                    "Maturity": 1500
                },
                "Soybeans": {
                    "Emergence": 130,
                    "First Trifoliate": 320,
                    "Flowering": 800,
                    "Pod Development": 1200,
                    "Maturity": 1700
                }
            }
            
            # Display tables showing GDD progress for common crops
            for crop, stages in gdd_thresholds.items():
                st.write(f"##### {crop}")
                
                stage_data = []
                for stage, threshold in stages.items():
                    progress = min(100, (total_gdd / threshold) * 100)
                    stage_data.append({
                        "Stage": stage,
                        "GDD Required": threshold,
                        "Progress": f"{progress:.1f}%" if progress < 100 else "Complete",
                        "Progress_Value": progress  # For sorting
                    })
                
                stage_df = pd.DataFrame(stage_data)
                st.dataframe(stage_df[["Stage", "GDD Required", "Progress"]], hide_index=True)
    else:
        st.error(f"Unable to fetch historical weather data for {location}. Please check location name and try again.")

def get_condition_icon(condition):
    """Map weather condition to icon code"""
    condition = condition.lower() if condition else ""
    
    if "clear" in condition:
        return "01d"
    elif "few clouds" in condition:
        return "02d"
    elif "scattered clouds" in condition:
        return "03d"
    elif "clouds" in condition:
        return "04d"
    elif "shower rain" in condition or "drizzle" in condition:
        return "09d"
    elif "rain" in condition:
        return "10d"
    elif "thunderstorm" in condition:
        return "11d"
    elif "snow" in condition:
        return "13d"
    elif "mist" in condition or "fog" in condition:
        return "50d"
    else:
        return "01d"  # Default