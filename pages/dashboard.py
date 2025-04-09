import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from models import crop_health_model
from utils import data_processing

def show():
    st.header("Farm Dashboard")
    
    # Overview statistics
    st.subheader("Farm Overview")
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Average Crop Health", value="76%", delta="4%")
    
    with col2:
        st.metric(label="Water Usage", value="12,400 L", delta="-5%")
    
    with col3:
        st.metric(label="Weather Risk", value="Low", delta="Stable")
    
    with col4:
        st.metric(label="Pest Risk", value="Medium", delta="↑2%")
    
    # Farm status and visualizations
    st.markdown("---")
    
    # Create two columns layout for the main content
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.subheader("Crop Health Status")
        
        # Crop health visualization
        crops = ["Maize", "Tomatoes", "Beans", "Cassava", "Sweet Potatoes"]
        health_scores = [82, 65, 78, 90, 72]
        
        # Create bar chart
        fig = px.bar(
            x=crops,
            y=health_scores,
            color=health_scores,
            color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
            labels={"x": "Crop", "y": "Health Score", "color": "Health"},
            title="Crop Health by Field",
            text=health_scores
        )
        
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(coloraxis_colorbar=dict(title="Health %"))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Crop health assessment upload
        st.subheader("Crop Health Assessment")
        st.markdown("""
        Upload an image of your crops for health analysis. The AI will assess the condition
        and provide recommendations.
        """)
        
        uploaded_file = st.file_uploader("Upload crop image", type=["jpg", "jpeg", "png"])
        
        analysis_col1, analysis_col2 = st.columns(2)
        
        if uploaded_file is not None:
            # Process the uploaded image
            from PIL import Image
            import io
            import numpy as np
            
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            with analysis_col1:
                st.image(image, caption="Uploaded Image", use_column_width=True)
            
            with analysis_col2:
                with st.spinner("Analyzing crop health..."):
                    # Analyze crop health using model
                    analysis_result = crop_health_model.analyze_crop_health(image_array)
                    
                    # Display health score with gauge
                    health_score = analysis_result["health_score"]
                    
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=health_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Health Score"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkgreen"},
                            'steps': [
                                {'range': [0, 40], 'color': "red"},
                                {'range': [40, 70], 'color': "orange"},
                                {'range': [70, 100], 'color': "green"},
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': health_score
                            }
                        }
                    ))
                    
                    fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display health status and color analysis
                    st.markdown(f"**Health Status:** {analysis_result['health_status']}")
                    
                    # Color composition
                    color_data = {
                        'Component': ['Healthy Tissue', 'Stressed Tissue', 'Damaged Tissue'],
                        'Percentage': [
                            analysis_result['color_analysis']['green_percentage'],
                            analysis_result['color_analysis']['yellow_percentage'],
                            analysis_result['color_analysis']['brown_percentage']
                        ]
                    }
                    
                    # Create a color pie chart
                    color_fig = px.pie(
                        color_data, 
                        values='Percentage', 
                        names='Component',
                        color='Component',
                        color_discrete_map={
                            'Healthy Tissue': 'green',
                            'Stressed Tissue': 'gold',
                            'Damaged Tissue': 'brown'
                        },
                        title="Leaf Tissue Analysis"
                    )
                    
                    color_fig.update_traces(textposition='inside', textinfo='percent+label')
                    color_fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(color_fig, use_container_width=True)
            
            # Nutrient status and recommendations
            st.subheader("Analysis Results")
            
            nutrient_col, rec_col = st.columns(2)
            
            with nutrient_col:
                st.markdown("#### Nutrient Status")
                
                nutrient_status = analysis_result["nutrient_status"]
                
                # Create a styled table for nutrient status
                html_table = f"""
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Nutrient</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Status</th>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">Nitrogen (N)</td>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: {'green' if nutrient_status['nitrogen'] == 'Adequate' else 'orange'}; color: white;">{nutrient_status['nitrogen']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">Phosphorus (P)</td>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: {'green' if nutrient_status['phosphorus'] == 'Adequate' else 'orange'}; color: white;">{nutrient_status['phosphorus']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">Potassium (K)</td>
                        <td style="padding: 8px; border: 1px solid #ddd; background-color: {'green' if nutrient_status['potassium'] == 'Adequate' else 'orange'}; color: white;">{nutrient_status['potassium']}</td>
                    </tr>
                </table>
                """
                
                st.markdown(html_table, unsafe_allow_html=True)
            
            with rec_col:
                st.markdown("#### Recommendations")
                
                for i, recommendation in enumerate(analysis_result["recommendations"]):
                    st.markdown(f"{i+1}. {recommendation}")
        
        else:
            # Show sample or instructions
            st.info("Please upload an image to analyze crop health")
    
    with right_col:
        # Farm activity feed
        st.subheader("Recent Activities")
        
        activities = [
            {"date": "Today", "activity": "Irrigation system maintenance", "status": "Completed"},
            {"date": "Yesterday", "activity": "Fertilizer application - Maize field", "status": "Completed"},
            {"date": "2 days ago", "activity": "Pest inspection - Tomato crop", "status": "Found issues"},
            {"date": "3 days ago", "activity": "Harvested 500kg Beans", "status": "Completed"},
            {"date": "5 days ago", "activity": "Soil testing - Northern plots", "status": "Completed"}
        ]
        
        for activity in activities:
            status_color = "green" if activity["status"] == "Completed" else "orange"
            st.markdown(f"""
            <div style="padding: 10px; border-left: 4px solid {status_color}; margin-bottom: 10px; background-color: rgba(255, 255, 255, 0.1);">
                <span style="color: gray; font-size: 12px;">{activity["date"]}</span>
                <p style="margin: 0; padding: 0;">{activity["activity"]}</p>
                <span style="color: {status_color}; font-size: 12px;">{activity["status"]}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Weather preview
        st.subheader("Weather Overview")
        
        # Current weather
        temp = 28
        humidity = 65
        
        col1, col2 = st.columns(2)
        col1.metric("Temperature", f"{temp}°C", delta="2°C")
        col2.metric("Humidity", f"{humidity}%", delta="-5%")
        
        # Simple forecast
        forecast = [
            {"day": "Today", "temp": 28, "condition": "Sunny"},
            {"day": "Tomorrow", "temp": 27, "condition": "Partly Cloudy"},
            {"day": "Day 3", "temp": 29, "condition": "Scattered Showers"}
        ]
        
        for day in forecast:
            icon = "☀️" if day["condition"] == "Sunny" else "⛅" if day["condition"] == "Partly Cloudy" else "🌧️"
            st.text(f"{day['day']}: {icon} {day['temp']}°C - {day['condition']}")
        
        st.caption("See Weather page for detailed forecast")
        
        # Resource status
        st.subheader("Resource Status")
        
        resources = {
            "Water": 75,
            "Fertilizer": 45,
            "Seeds": 80,
            "Fuel": 30
        }
        
        # Create resource gauge charts
        for resource, level in resources.items():
            color = "green" if level > 60 else "orange" if level > 30 else "red"
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=level,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': resource},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': color},
                    'threshold': {
                        'thickness': 0.75,
                        'value': level
                    }
                }
            ))
            
            fig.update_layout(height=100, margin=dict(l=20, r=20, t=50, b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    # Farm performance trends
    st.markdown("---")
    st.subheader("Farm Performance Trends")
    
    # Generate time series data
    crop_yields = data_processing.generate_time_series(days=30, base_value=500, volatility=50, trend=5)
    water_usage = data_processing.generate_time_series(days=30, base_value=1000, volatility=100, trend=-2)
    
    # Create time series chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=crop_yields['date'], 
        y=crop_yields['value'],
        mode='lines+markers',
        name='Crop Yield (kg)',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=water_usage['date'], 
        y=water_usage['value'],
        mode='lines+markers',
        name='Water Usage (L)',
        line=dict(color='blue', width=2),
        yaxis="y2"
    ))
    
    fig.update_layout(
        title="Crop Yield vs. Water Usage - Last 30 Days",
        xaxis=dict(title="Date"),
        yaxis=dict(
            title="Crop Yield (kg)",
            titlefont=dict(color="green"),
            tickfont=dict(color="green")
        ),
        yaxis2=dict(
            title="Water Usage (L)",
            titlefont=dict(color="blue"),
            tickfont=dict(color="blue"),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Alerts and notifications
    st.markdown("---")
    st.subheader("Alerts & Notifications")
    
    alerts = [
        {"type": "Weather", "severity": "High", "message": "Heavy rainfall expected in the next 48 hours. Consider postponing fertilizer application."},
        {"type": "Pests", "severity": "Medium", "message": "Early signs of aphid infestation detected in tomato plants. Monitor closely and consider preventive measures."},
        {"type": "Resources", "severity": "Low", "message": "Fertilizer stock is below 50%. Consider restocking within the next two weeks."}
    ]
    
    for alert in alerts:
        severity_color = "red" if alert["severity"] == "High" else "orange" if alert["severity"] == "Medium" else "blue"
        
        st.markdown(f"""
        <div style="padding: 10px; border-left: 5px solid {severity_color}; background-color: rgba(255, 255, 255, 0.1);">
            <h4 style="margin-top: 0; color: {severity_color};">{alert['type']} Alert - {alert['severity']} Priority</h4>
            <p>{alert['message']}</p>
        </div>
        """, unsafe_allow_html=True)