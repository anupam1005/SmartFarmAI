import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from db_utils import (
    get_farm_by_id, get_fields_by_farm, get_resource_usage_stats,
    get_health_records_by_field, get_detection_history,
    get_recent_activities, get_latest_health_record
)

def show():
    st.title("Farm Dashboard")
    
    # Get farm ID from session state
    if 'selected_farm_id' not in st.session_state:
        st.error("No farm selected. Please select a farm from the sidebar.")
        return
    
    farm_id = st.session_state['selected_farm_id']
    farm = get_farm_by_id(farm_id)
    
    if not farm:
        st.error("Selected farm not found in the database.")
        return
    
    # Display farm information at the top
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.header(farm.name)
        st.write(f"**Location:** {farm.location or 'Not specified'}")
        st.write(f"**Size:** {farm.area_size or 'Not specified'} hectares")
    
    with col2:
        # Get weather from session_state if available (in a real app, would pull from API)
        if 'current_weather' in st.session_state:
            weather = st.session_state['current_weather']
            st.metric("Temperature", f"{weather['temperature']}°C")
            st.metric("Condition", weather['condition'])
        else:
            # Placeholder weather data
            st.metric("Temperature", "25°C")
            st.metric("Condition", "Partly Cloudy")
    
    with col3:
        # Quick stats
        fields = get_fields_by_farm(farm_id)
        st.metric("Fields", len(fields) if fields else 0)
        
        # Calculate total planted area
        planted_area = sum(field.area_size or 0 for field in fields if field.current_crop)
        st.metric("Planted Area", f"{planted_area:.1f} ha")
    
    # Create main dashboard sections
    tab1, tab2, tab3 = st.tabs(["Farm Overview", "Health Status", "Activity Feed"])
    
    # TAB 1: FARM OVERVIEW
    with tab1:
        # Create two columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Field status section
            st.subheader("Field Status")
            
            if fields:
                # Create data for fields table
                field_data = []
                for field in fields:
                    # Get latest health record for the field if available
                    health_record = get_latest_health_record(field.id)
                    
                    health_status = "Unknown"
                    health_score = None
                    if health_record:
                        health_status = health_record.health_status
                        health_score = health_record.health_score
                    
                    # Determine the status color
                    if health_status == "Healthy":
                        status_color = "green"
                    elif health_status == "Moderate Stress":
                        status_color = "orange"
                    elif health_status == "Unhealthy":
                        status_color = "red"
                    else:
                        status_color = "gray"
                    
                    # Create a dictionary with field information
                    field_info = {
                        "Field": field.name,
                        "Crop": field.current_crop or "None",
                        "Size (ha)": field.area_size or "N/A",
                        "Soil Type": field.soil_type or "Unknown",
                        "Health Status": health_status,
                        "Health Score": health_score,
                        "Status Color": status_color,
                        "Planting Date": field.planting_date.strftime("%Y-%m-%d") if field.planting_date else "Not set",
                        "Days to Harvest": calculate_days_to_harvest(field)
                    }
                    
                    field_data.append(field_info)
                
                # Convert to DataFrame
                df = pd.DataFrame(field_data)
                
                # Display the fields in a styled table
                for i, row in df.iterrows():
                    with st.container():
                        cols = st.columns([3, 2, 2, 2, 3])
                        
                        with cols[0]:
                            st.subheader(row["Field"])
                            st.caption(f"{row['Size (ha)']} ha - {row['Soil Type']}")
                        
                        with cols[1]:
                            st.write("**Crop:**")
                            st.write(row["Crop"])
                        
                        with cols[2]:
                            st.write("**Status:**")
                            st.markdown(f":<span style='color:{row['Status Color']}'>{row['Health Status']}</span>", 
                                         unsafe_allow_html=True)
                        
                        with cols[3]:
                            st.write("**Planted:**")
                            st.write(row["Planting Date"])
                        
                        with cols[4]:
                            if row["Days to Harvest"] and row["Days to Harvest"] != "N/A":
                                progress = min(1.0, 1 - (row["Days to Harvest"] / 100))  # Simplified calculation
                                st.progress(progress)
                                st.caption(f"{row['Days to Harvest']} days to harvest")
                            else:
                                st.write("No harvest date set")
                    
                    st.divider()
            else:
                st.info("No fields found for this farm. Add fields to see them here.")
        
        with col2:
            # Resource usage summary
            st.subheader("Resource Usage (30 Days)")
            
            # Get resource usage stats
            resources = get_resource_usage_stats(farm_id, days=30)
            
            if resources:
                # Summarize by resource type
                resource_summary = {}
                
                for usage in resources:
                    resource = usage.resource
                    if resource.type not in resource_summary:
                        resource_summary[resource.type] = {
                            "total": 0,
                            "unit": resource.unit
                        }
                    resource_summary[resource.type]["total"] += usage.quantity
                
                # Create visualization for resource usage
                resource_types = list(resource_summary.keys())
                resource_values = [summary["total"] for summary in resource_summary.values()]
                
                # Display a pie chart of resource usage by type
                if resource_types:
                    fig = px.pie(
                        names=resource_types,
                        values=resource_values,
                        title="Resource Usage by Type",
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display resource usage metrics
                for resource_type, summary in resource_summary.items():
                    st.metric(
                        f"{resource_type} Usage",
                        f"{summary['total']:.1f} {summary['unit']}"
                    )
            else:
                st.info("No resource usage data available for the last 30 days.")
            
            # Quick access buttons
            st.subheader("Quick Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Detect Pests", key="quick_detect"):
                    # In a real app, this would navigate to the Pest Detection page
                    st.session_state['current_page'] = "Pest & Disease Detection"
                    st.experimental_rerun()
            
            with col2:
                if st.button("Add Resource", key="quick_resource"):
                    # In a real app, this would navigate to the Resource Management page
                    st.session_state['current_page'] = "Resource Management"
                    st.experimental_rerun()
            
            if st.button("View Weather Forecast", key="quick_weather"):
                # In a real app, this would navigate to the Weather page
                st.session_state['current_page'] = "Weather Insights"
                st.experimental_rerun()
    
    # TAB 2: HEALTH STATUS
    with tab2:
        st.subheader("Farm Health Overview")
        
        if not fields:
            st.info("No fields found for this farm. Add fields to see health data.")
        else:
            # Create metrics for overall health
            overall_health_score = 0
            fields_with_health = 0
            health_by_field = {}
            
            # Calculate average health score and collect health data by field
            for field in fields:
                health_record = get_latest_health_record(field.id)
                if health_record and health_record.health_score is not None:
                    overall_health_score += health_record.health_score
                    fields_with_health += 1
                    health_by_field[field.name] = {
                        "score": health_record.health_score,
                        "green": health_record.green_percentage,
                        "yellow": health_record.yellow_percentage,
                        "brown": health_record.brown_percentage,
                        "nitrogen": health_record.nitrogen_status,
                        "phosphorus": health_record.phosphorus_status,
                        "potassium": health_record.potassium_status
                    }
            
            # Display overall health metrics
            if fields_with_health > 0:
                avg_health = overall_health_score / fields_with_health
                
                # Determine overall status
                overall_status = "Unhealthy"
                if avg_health >= 75:
                    overall_status = "Healthy"
                elif avg_health >= 50:
                    overall_status = "Moderate Stress"
                
                # Display the metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average Health Score", f"{avg_health:.1f}")
                
                with col2:
                    st.metric("Overall Status", overall_status)
                
                with col3:
                    st.metric("Fields Analyzed", f"{fields_with_health}/{len(fields)}")
                
                # Create health visualization
                if health_by_field:
                    # Prepare data for charts
                    field_names = list(health_by_field.keys())
                    health_scores = [data["score"] for data in health_by_field.values()]
                    
                    # Bar chart for health scores by field
                    fig = px.bar(
                        x=field_names,
                        y=health_scores,
                        labels={"x": "Field", "y": "Health Score"},
                        title="Health Score by Field",
                        color=health_scores,
                        color_continuous_scale="RdYlGn",  # Red to Yellow to Green
                        range_color=[0, 100]
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create a multi-bar chart for vegetation breakdown
                    vegetation_data = []
                    
                    for field_name, data in health_by_field.items():
                        vegetation_data.extend([
                            {"Field": field_name, "Type": "Green", "Percentage": data["green"]},
                            {"Field": field_name, "Type": "Yellow", "Percentage": data["yellow"]},
                            {"Field": field_name, "Type": "Brown", "Percentage": data["brown"]}
                        ])
                    
                    veg_df = pd.DataFrame(vegetation_data)
                    
                    fig = px.bar(
                        veg_df,
                        x="Field",
                        y="Percentage",
                        color="Type",
                        title="Vegetation Breakdown by Field",
                        color_discrete_map={"Green": "green", "Yellow": "gold", "Brown": "brown"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Nutrient status table
                    st.subheader("Nutrient Status by Field")
                    
                    nutrient_data = []
                    for field_name, data in health_by_field.items():
                        nutrient_data.append({
                            "Field": field_name,
                            "Nitrogen": data["nitrogen"],
                            "Phosphorus": data["phosphorus"],
                            "Potassium": data["potassium"]
                        })
                    
                    nutrient_df = pd.DataFrame(nutrient_data)
                    st.dataframe(nutrient_df, hide_index=True)
                
                # Recent health issues
                st.subheader("Recent Health Issues")
                
                # Collect health records with issues
                health_issues = []
                
                for field in fields:
                    records = get_health_records_by_field(field.id, limit=5)
                    for record in records:
                        if record.health_status != "Healthy":
                            health_issues.append({
                                "Date": record.date,
                                "Field": field.name,
                                "Status": record.health_status,
                                "Score": record.health_score,
                                "Issues": []
                            })
                            
                            # Add specific issues
                            if record.nitrogen_status == "Deficient":
                                health_issues[-1]["Issues"].append("Nitrogen deficiency")
                            if record.phosphorus_status == "Deficient":
                                health_issues[-1]["Issues"].append("Phosphorus deficiency")
                            if record.potassium_status == "Deficient":
                                health_issues[-1]["Issues"].append("Potassium deficiency")
                
                # Sort by date and take most recent
                health_issues.sort(key=lambda x: x["Date"], reverse=True)
                health_issues = health_issues[:5]  # Show 5 most recent
                
                if health_issues:
                    for issue in health_issues:
                        with st.container():
                            cols = st.columns([1, 2, 2])
                            
                            with cols[0]:
                                st.write(f"**{issue['Date'].strftime('%Y-%m-%d')}**")
                                st.write(f"Field: {issue['Field']}")
                            
                            with cols[1]:
                                st.write(f"Status: {issue['Status']}")
                                st.write(f"Score: {issue['Score']:.1f}")
                            
                            with cols[2]:
                                st.write("Issues:")
                                for problem in issue["Issues"]:
                                    st.write(f"• {problem}")
                            
                            st.divider()
                else:
                    st.info("No health issues recorded recently.")
            else:
                st.info("No health records available. Use the health analysis tool to scan your fields.")
    
    # TAB 3: ACTIVITY FEED
    with tab3:
        st.subheader("Recent Activities")
        
        # Get recent activities
        activities = get_recent_activities(farm_id, limit=10)
        
        if activities:
            for activity in activities:
                with st.container():
                    cols = st.columns([1, 3, 1])
                    
                    with cols[0]:
                        st.write(f"**{activity.date.strftime('%Y-%m-%d')}**")
                    
                    with cols[1]:
                        st.write(f"**{activity.activity_type}**")
                        st.write(activity.description)
                    
                    with cols[2]:
                        status_color = "green" if activity.status == "Completed" else "orange" if activity.status == "In Progress" else "gray"
                        st.markdown(f"**Status:** <span style='color:{status_color}'>{activity.status}</span>", unsafe_allow_html=True)
                    
                    st.divider()
        else:
            st.info("No activities recorded. Activities will appear here as you use the system.")
        
        # Pest detection history
        st.subheader("Recent Pest Detections")
        
        # Get pest detection history
        detections = get_detection_history(limit=5)
        
        if detections:
            for detection in detections:
                with st.container():
                    cols = st.columns([1, 2, 2])
                    
                    # Get field name
                    field_name = next((field.name for field in fields if field.id == detection.field_id), "Unknown")
                    
                    with cols[0]:
                        st.write(f"**{detection.date.strftime('%Y-%m-%d')}**")
                        st.write(f"Field: {field_name}")
                    
                    with cols[1]:
                        st.write(f"Detected: {detection.detected_class.replace('_', ' ')}")
                        st.write(f"Confidence: {detection.confidence:.1f}%")
                    
                    with cols[2]:
                        severity_color = "green" if detection.severity == "Low" else "orange" if detection.severity == "Medium" else "red"
                        st.markdown(f"**Severity:** <span style='color:{severity_color}'>{detection.severity}</span>", unsafe_allow_html=True)
                        st.write("Action: " + (detection.treatment_recommendation[:50] + "..." if len(detection.treatment_recommendation) > 50 else detection.treatment_recommendation))
                    
                    st.divider()
        else:
            st.info("No pest detections recorded. Use the pest detection tool to scan your crops.")

def calculate_days_to_harvest(field):
    """Helper function to calculate days to harvest based on planting and expected harvest dates"""
    if not field.planting_date or not field.expected_harvest_date:
        return "N/A"
    
    days_to_harvest = (field.expected_harvest_date - datetime.now()).days
    return max(0, days_to_harvest)