import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from db_utils import (
    get_all_farms, 
    get_fields_by_farm, 
    get_recent_activities,
    get_health_records_by_field,
    get_pest_detections_by_field,
    get_resources_by_farm,
    get_resource_usage_by_field,
    get_crop_recommendations_by_farm
)

def show():
    st.markdown("<h1 class='main-header'>Farm Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Monitor and manage your farm at a glance</p>", unsafe_allow_html=True)
    
    # Get farm data
    farms = get_all_farms()
    
    if not farms:
        st.warning("No farms found in the database. Please add a farm to get started.")
        return
    
    # Farm selector
    farm_names = [farm.name for farm in farms]
    selected_farm_name = st.selectbox("Select Farm", farm_names)
    
    # Get selected farm
    selected_farm = next((farm for farm in farms if farm.name == selected_farm_name), None)
    
    if not selected_farm:
        st.error("Selected farm not found.")
        return
    
    # Display farm info
    st.markdown(f"### {selected_farm.name}")
    st.markdown(f"**Location:** {selected_farm.location or 'Not specified'}")
    st.markdown(f"**Area:** {selected_farm.area_size or 0} hectares")
    
    # Layout for dashboard sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_field_overview(selected_farm)
    
    with col2:
        show_activity_feed(selected_farm)
    
    # Second row with crop health and resource metrics
    col3, col4 = st.columns([1, 1])
    
    with col3:
        show_crop_health_summary(selected_farm)
    
    with col4:
        show_resource_summary(selected_farm)
    
    # Third row with recommendations and alerts
    st.markdown("### Recommendations & Alerts")
    show_recommendations_and_alerts(selected_farm)

def show_field_overview(farm):
    """Show overview of fields for the selected farm"""
    st.markdown("### Field Overview")
    
    # Get fields for the farm
    fields = get_fields_by_farm(farm.id)
    
    if not fields:
        st.info("No fields found for this farm. Add fields to see them here.")
        return
    
    # Create a dataframe for the fields
    field_data = []
    for field in fields:
        days_to_harvest = calculate_days_to_harvest(field)
        
        field_data.append({
            "Field Name": field.name,
            "Area": field.area_size or 0,
            "Current Crop": field.current_crop or "None",
            "Soil Type": field.soil_type or "Unknown",
            "Days to Harvest": days_to_harvest if days_to_harvest is not None else "N/A",
            "Field ID": field.id
        })
    
    field_df = pd.DataFrame(field_data)
    
    # Display field map/visualization
    fig = go.Figure()
    
    # Create rectangles for each field with size proportional to area
    max_area = field_df["Area"].max() if not field_df.empty else 1
    min_size = 0.1  # Minimum size for very small fields
    
    for i, field in enumerate(field_data):
        # Calculate size relative to the largest field
        rel_size = (field["Area"] / max_area) if max_area > 0 else min_size
        size = max(rel_size, min_size)
        
        # Position fields in a grid-like layout
        row = i // 3
        col = i % 3
        
        # Create rectangle
        fig.add_shape(
            type="rect",
            x0=col * 1.2, 
            y0=row * 1.2,
            x1=col * 1.2 + size, 
            y1=row * 1.2 + size,
            line=dict(color="green"),
            fillcolor="lightgreen",
            opacity=0.8,
        )
        
        # Add field name
        fig.add_annotation(
            x=col * 1.2 + size/2,
            y=row * 1.2 + size/2,
            text=field["Field Name"],
            showarrow=False,
            font=dict(color="black", size=10)
        )
    
    # Set layout
    fig.update_layout(
        title="Field Map",
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show table with field details
    if not field_df.empty:
        display_cols = ["Field Name", "Area", "Current Crop", "Soil Type", "Days to Harvest"]
        st.dataframe(field_df[display_cols], use_container_width=True, hide_index=True)

def show_activity_feed(farm):
    """Show recent farm activities"""
    st.markdown("### Recent Activities")
    
    # Get recent activities
    activities = get_recent_activities(farm.id, limit=5)
    
    if not activities:
        st.info("No recent activities found.")
        return
    
    # Display activities
    for activity in activities:
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Show icon based on activity type
                icon = "🚜"  # default
                if "plant" in activity.activity_type.lower():
                    icon = "🌱"
                elif "harvest" in activity.activity_type.lower():
                    icon = "🌾"
                elif "irrigat" in activity.activity_type.lower():
                    icon = "💧"
                elif "fertiliz" in activity.activity_type.lower():
                    icon = "🧪"
                elif "pest" in activity.activity_type.lower():
                    icon = "🐛"
                
                st.markdown(f"<h1 style='font-size: 24px; margin: 0;'>{icon}</h1>", unsafe_allow_html=True)
            
            with col2:
                # Format date nicely
                date_str = activity.date.strftime("%b %d, %Y")
                
                st.markdown(f"**{activity.activity_type}** - {date_str}")
                st.markdown(f"<small>{activity.description or ''}</small>", unsafe_allow_html=True)
                
                # Show status with color
                status_color = "#4CAF50" if activity.status == "Completed" else "#FFC107" if activity.status == "In Progress" else "#9E9E9E"
                st.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{activity.status}</span>", unsafe_allow_html=True)
            
            st.markdown("---")

def show_crop_health_summary(farm):
    """Show summary of crop health across fields"""
    st.markdown("### Crop Health Summary")
    
    # Get fields for the farm
    fields = get_fields_by_farm(farm.id)
    
    if not fields:
        st.info("No fields found for this farm.")
        return
    
    # Create data for crop health visualization
    health_data = []
    
    for field in fields:
        # Get latest health record for the field
        health_records = get_health_records_by_field(field.id, limit=1)
        
        if health_records:
            latest_record = health_records[0]
            health_data.append({
                "Field": field.name,
                "Health Score": latest_record.health_score,
                "Status": latest_record.health_status,
                "Last Updated": latest_record.date.strftime("%b %d")
            })
        else:
            health_data.append({
                "Field": field.name,
                "Health Score": 0,
                "Status": "No Data",
                "Last Updated": "Never"
            })
    
    # Create health score gauge chart
    if health_data:
        health_df = pd.DataFrame(health_data)
        avg_health = health_df["Health Score"].mean()
        
        # Gauge chart for average health
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_health,
            title={"text": "Average Crop Health"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "green"},
                "steps": [
                    {"range": [0, 40], "color": "red"},
                    {"range": [40, 70], "color": "yellow"},
                    {"range": [70, 100], "color": "lightgreen"}
                ],
                "threshold": {
                    "line": {"color": "green", "width": 4},
                    "thickness": 0.75,
                    "value": avg_health
                }
            }
        ))
        
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
        
        # Bar chart for field health scores
        fig = px.bar(
            health_df, 
            x="Field", 
            y="Health Score",
            color="Health Score",
            color_continuous_scale=["red", "yellow", "green"],
            range_color=[0, 100],
            text="Status"
        )
        
        fig.update_layout(
            title="Health by Field",
            xaxis_title=None,
            yaxis_title="Health Score",
            height=250,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No health data available.")

def show_resource_summary(farm):
    """Show summary of farm resources"""
    st.markdown("### Resource Summary")
    
    # Get resources for the farm
    resources = get_resources_by_farm(farm.id)
    
    if not resources:
        st.info("No resources found for this farm.")
        return
    
    # Create data for resource visualization
    resource_data = []
    
    for resource in resources:
        resource_data.append({
            "Resource": resource.name,
            "Type": resource.type,
            "Quantity": resource.quantity,
            "Unit": resource.unit
        })
    
    # Create a DataFrame
    resource_df = pd.DataFrame(resource_data)
    
    # Group by type
    type_summary = resource_df.groupby("Type")["Quantity"].sum().reset_index()
    
    # Pie chart of resource types
    fig = px.pie(
        type_summary,
        values="Quantity",
        names="Type",
        color_discrete_sequence=px.colors.sequential.Greens,
        title="Resource Distribution by Type"
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", y=-0.1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Table with resource details
    st.dataframe(resource_df, use_container_width=True, hide_index=True)

def show_recommendations_and_alerts(farm):
    """Show recommendations and alerts for the farm"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recommendations")
        
        # Get crop recommendations
        recommendations = get_crop_recommendations_by_farm(farm.id, limit=3)
        
        if recommendations:
            for rec in recommendations:
                with st.container():
                    st.markdown(f"**{rec.crop} - {rec.suitability:.1f}% Suitable**")
                    st.markdown(f"{rec.rationale[:100]}..." if len(rec.rationale) > 100 else rec.rationale)
                    st.markdown("---")
        else:
            st.info("No crop recommendations available.")
    
    with col2:
        st.markdown("#### Pest Alerts")
        
        # Get fields for the farm
        fields = get_fields_by_farm(farm.id)
        
        if not fields:
            st.info("No fields found for this farm.")
            return
        
        # Collect pest detections from all fields
        all_detections = []
        
        for field in fields:
            detections = get_pest_detections_by_field(field.id, limit=2)
            if detections:
                for detection in detections:
                    all_detections.append({
                        "Field": field.name,
                        "Pest": detection.detected_class,
                        "Severity": detection.severity,
                        "Date": detection.date
                    })
        
        # Display pest alerts
        if all_detections:
            # Sort by date (most recent first)
            all_detections.sort(key=lambda x: x["Date"], reverse=True)
            
            for detection in all_detections[:3]:  # Show at most 3
                with st.container():
                    severity_color = "#FF5252" if detection["Severity"] == "High" else "#FFC107" if detection["Severity"] == "Medium" else "#4CAF50"
                    
                    st.markdown(f"**{detection['Pest']}** in {detection['Field']}")
                    st.markdown(f"<span style='color: {severity_color}; font-weight: bold;'>{detection['Severity']} Severity</span> - {detection['Date'].strftime('%b %d')}", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("No pest alerts available.")

def calculate_days_to_harvest(field):
    """Helper function to calculate days to harvest based on planting and expected harvest dates"""
    if field.planting_date and field.expected_harvest_date:
        today = datetime.now().date()
        harvest_date = field.expected_harvest_date.date()
        
        if harvest_date > today:
            return (harvest_date - today).days
        else:
            return 0  # Past harvest date
    
    return None  # Dates not available