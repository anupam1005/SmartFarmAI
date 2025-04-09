import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from db_utils import (
    get_all_farms,
    get_fields_by_farm,
    get_resources_by_farm,
    get_resources_by_type,
    add_resource,
    update_resource_quantity,
    record_resource_usage,
    get_resource_usage_by_field,
    get_resource_usage_stats
)

def show():
    st.markdown("<h1 class='main-header'>Resource Management</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Track and optimize your farm resources</p>", unsafe_allow_html=True)
    
    # Layout with tabs for different resource management functions
    tab1, tab2, tab3 = st.tabs(["Inventory", "Resource Usage", "Usage Analysis"])
    
    # Get farms for selection
    farms = get_all_farms()
    
    if not farms:
        for tab in [tab1, tab2, tab3]:
            with tab:
                st.warning("No farms found. Please add a farm first.")
        return
    
    # Farm selector in sidebar
    with st.sidebar:
        farm_names = [farm.name for farm in farms]
        selected_farm_name = st.selectbox("Select Farm", farm_names, key="farm_selector")
        
        # Get selected farm
        selected_farm = next((farm for farm in farms if farm.name == selected_farm_name), None)
        
        if not selected_farm:
            st.error("Selected farm not found.")
            return
    
    # Inventory Management Tab
    with tab1:
        show_inventory_management(selected_farm)
    
    # Resource Usage Tab
    with tab2:
        show_resource_usage(selected_farm)
    
    # Usage Analysis Tab
    with tab3:
        show_usage_analysis(selected_farm)

def show_inventory_management(farm):
    """Show and manage resource inventory"""
    st.header("Resource Inventory")
    
    # Get current resources for the farm
    resources = get_resources_by_farm(farm.id)
    
    # Show current inventory
    if resources:
        # Create dataframe for display
        resource_data = []
        
        for resource in resources:
            resource_data.append({
                "ID": resource.id,
                "Name": resource.name,
                "Type": resource.type,
                "Quantity": resource.quantity,
                "Unit": resource.unit,
                "Last Updated": resource.last_updated.strftime("%Y-%m-%d %H:%M") if resource.last_updated else "Unknown"
            })
        
        resource_df = pd.DataFrame(resource_data)
        
        # Show inventory table with edit capability
        st.subheader("Current Inventory")
        
        # Use grid to show data
        edited_df = st.data_editor(
            resource_df,
            column_config={
                "ID": st.column_config.Column(disabled=True),
                "Name": st.column_config.Column(disabled=True),
                "Type": st.column_config.Column(disabled=True),
                "Unit": st.column_config.Column(disabled=True),
                "Last Updated": st.column_config.Column(disabled=True),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity",
                    help="Edit to update resource quantity",
                    min_value=0
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Check for changes and update database
        if not resource_df.equals(edited_df):
            for _, row in edited_df.iterrows():
                resource_id = row["ID"]
                new_quantity = row["Quantity"]
                
                # Find original quantity
                original = resource_df.loc[resource_df["ID"] == resource_id, "Quantity"].values[0]
                
                # Update if changed
                if new_quantity != original:
                    update_resource_quantity(resource_id, new_quantity)
                    st.success(f"Updated {row['Name']} quantity to {new_quantity} {row['Unit']}")
        
        # Create visualizations
        st.subheader("Inventory Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of resource types
            type_counts = resource_df.groupby("Type").size().reset_index(name="Count")
            
            if not type_counts.empty:
                fig = px.pie(
                    type_counts, 
                    values="Count", 
                    names="Type",
                    title="Resource Types Distribution",
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart of resource quantities
            # Normalize to common unit types for comparison
            resource_df["NormalizedQuantity"] = resource_df.apply(
                lambda row: normalize_quantity(row["Quantity"], row["Unit"], row["Type"]), 
                axis=1
            )
            
            fig = px.bar(
                resource_df.sort_values("NormalizedQuantity"), 
                x="Name", 
                y="NormalizedQuantity",
                color="Type",
                title="Resource Quantities (Normalized)",
                labels={"NormalizedQuantity": "Normalized Quantity"},
                color_discrete_sequence=px.colors.sequential.Greens
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No resources found. Add resources below to get started.")
    
    # Form to add new resource
    st.subheader("Add New Resource")
    
    with st.form("add_resource_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Resource Name", placeholder="e.g., NPK Fertilizer")
            
            # Define common resource types
            resource_types = [
                "Water", 
                "Fertilizer - Nitrogen", 
                "Fertilizer - Phosphorus", 
                "Fertilizer - Potassium",
                "Fertilizer - Compound", 
                "Fertilizer - Organic",
                "Pesticide - Insecticide",
                "Pesticide - Fungicide",
                "Pesticide - Herbicide",
                "Seeds",
                "Fuel",
                "Tools",
                "Other"
            ]
            
            resource_type = st.selectbox("Resource Type", resource_types)
        
        with col2:
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
            
            # Define appropriate units based on resource type
            if "Water" in resource_type:
                unit_options = ["Liters", "Gallons", "Cubic Meters"]
            elif "Fertilizer" in resource_type:
                unit_options = ["Kilograms", "Pounds", "Tons", "Bags"]
            elif "Pesticide" in resource_type:
                unit_options = ["Liters", "Gallons", "Kilograms", "Pounds"]
            elif "Seeds" in resource_type:
                unit_options = ["Kilograms", "Pounds", "Bags", "Units"]
            elif "Fuel" in resource_type:
                unit_options = ["Liters", "Gallons"]
            else:
                unit_options = ["Units", "Kilograms", "Liters", "Pieces"]
            
            unit = st.selectbox("Unit", unit_options)
        
        submit_button = st.form_submit_button("Add Resource")
        
        if submit_button:
            if not name:
                st.error("Resource name is required")
            else:
                # Add resource to database
                add_resource(farm.id, name, resource_type, quantity, unit)
                st.success(f"Added {name} to resources")
                st.rerun()

def show_resource_usage(farm):
    """Record and view resource usage"""
    st.header("Resource Usage")
    
    # Get resources for the farm
    resources = get_resources_by_farm(farm.id)
    
    # Get fields for the farm
    fields = get_fields_by_farm(farm.id)
    
    if not resources:
        st.info("No resources found. Please add resources in the Inventory tab.")
        return
    
    if not fields:
        st.info("No fields found. Please add fields to record resource usage.")
        return
    
    # Form to record resource usage
    st.subheader("Record Resource Usage")
    
    with st.form("record_usage_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Create resource selector with info about current quantity
            resource_options = {}
            for resource in resources:
                resource_options[resource.id] = f"{resource.name} ({resource.quantity} {resource.unit} available)"
            
            resource_id = st.selectbox(
                "Resource", 
                options=list(resource_options.keys()),
                format_func=lambda x: resource_options[x]
            )
            
            # Get the selected resource
            selected_resource = next((r for r in resources if r.id == resource_id), None)
            
            # Field selector
            field_id = st.selectbox(
                "Field", 
                options=[field.id for field in fields],
                format_func=lambda x: next((field.name for field in fields if field.id == x), "Unknown")
            )
        
        with col2:
            # Date selector with default to today
            date = st.date_input("Date", value=datetime.now().date())
            
            # Quantity input with appropriate unit
            if selected_resource:
                usage_quantity = st.number_input(
                    f"Quantity ({selected_resource.unit})", 
                    min_value=0.0,
                    max_value=float(selected_resource.quantity),
                    step=0.1
                )
                
                # Show current availability
                st.info(f"Available: {selected_resource.quantity} {selected_resource.unit}")
            else:
                usage_quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
        
        # Application method and notes
        application_method = st.selectbox(
            "Application Method", 
            options=["Manual", "Spraying", "Drip Irrigation", "Broadcast", "Injection", "Other"]
        )
        
        notes = st.text_area("Notes", placeholder="Optional notes about this resource usage")
        
        submit_button = st.form_submit_button("Record Usage")
        
        if submit_button:
            if not selected_resource:
                st.error("Please select a resource")
            elif usage_quantity <= 0:
                st.error("Please enter a quantity greater than zero")
            elif usage_quantity > selected_resource.quantity:
                st.error(f"Insufficient {selected_resource.name} available")
            else:
                # Record usage in database
                record_resource_usage(
                    resource_id=resource_id,
                    field_id=field_id,
                    quantity=usage_quantity,
                    application_method=application_method,
                    notes=notes
                )
                
                # Update resource quantity
                new_quantity = selected_resource.quantity - usage_quantity
                update_resource_quantity(resource_id, new_quantity)
                
                st.success(f"Recorded usage of {usage_quantity} {selected_resource.unit} of {selected_resource.name}")
                st.rerun()
    
    # Show recent resource usage
    st.subheader("Recent Resource Usage")
    
    # Get usage data for each field
    all_usage_data = []
    
    for field in fields:
        # Get usage for the past 30 days
        start_date = datetime.now() - timedelta(days=30)
        usage_records = get_resource_usage_by_field(field.id, start_date=start_date)
        
        for record in usage_records:
            # Get resource info
            resource = next((r for r in resources if r.id == record.resource_id), None)
            
            if resource:
                all_usage_data.append({
                    "Date": record.date,
                    "Field": field.name,
                    "Resource": resource.name,
                    "Type": resource.type,
                    "Quantity": record.quantity,
                    "Unit": resource.unit,
                    "Method": record.application_method,
                    "Notes": record.notes
                })
    
    if all_usage_data:
        usage_df = pd.DataFrame(all_usage_data)
        usage_df = usage_df.sort_values("Date", ascending=False)
        
        # Display table
        st.dataframe(usage_df, use_container_width=True, hide_index=True)
        
        # Visualization of recent usage
        st.subheader("Usage Visualization")
        
        # Group by type and field
        type_field_usage = usage_df.groupby(["Type", "Field"])["Quantity"].sum().reset_index()
        
        # Create stacked bar chart
        fig = px.bar(
            type_field_usage, 
            x="Type", 
            y="Quantity", 
            color="Field",
            title="Resource Usage by Type and Field",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No resource usage records found for the past 30 days.")

def show_usage_analysis(farm):
    """Analyze resource usage patterns and efficiency"""
    st.header("Resource Usage Analysis")
    
    # Get resources and fields
    resources = get_resources_by_farm(farm.id)
    fields = get_fields_by_farm(farm.id)
    
    if not resources or not fields:
        st.info("Insufficient data for analysis. Please add resources and fields, and record usage data.")
        return
    
    # Get usage statistics
    resource_types = list(set([r.type for r in resources]))
    
    # Analysis period selector
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_period = st.selectbox(
            "Analysis Period",
            options=[30, 60, 90, 180, 365],
            format_func=lambda x: f"Past {x} days"
        )
    
    with col2:
        selected_type = st.selectbox(
            "Resource Type",
            options=["All"] + resource_types
        )
    
    # Get statistics based on selections
    if selected_type == "All":
        usage_stats = get_resource_usage_stats(farm.id, days=analysis_period)
    else:
        usage_stats = get_resource_usage_stats(farm.id, resource_type=selected_type, days=analysis_period)
    
    if not usage_stats or not usage_stats.get('total_usage'):
        st.info(f"No usage data found for the selected period and resource type.")
        return
    
    # Display usage statistics
    st.subheader("Usage Statistics")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Usage", 
            f"{usage_stats['total_usage']:.1f} units",
            delta=f"{usage_stats.get('usage_change', 0):.1f}%",
            delta_color="inverse" if selected_type in ["Water", "Fertilizer", "Pesticide"] else "normal"
        )
    
    with col2:
        st.metric(
            "Daily Average", 
            f"{usage_stats['daily_avg']:.2f} units/day"
        )
    
    with col3:
        st.metric(
            "Usage Trend", 
            "Increasing" if usage_stats.get('trend', 0) > 0.05 else
            "Decreasing" if usage_stats.get('trend', 0) < -0.05 else "Stable",
            delta=f"{usage_stats.get('trend', 0) * 100:.1f}%",
            delta_color="inverse" if selected_type in ["Water", "Fertilizer", "Pesticide"] else "normal"
        )
    
    # Create visualizations based on the data
    if 'usage_by_day' in usage_stats and len(usage_stats['usage_by_day']) > 1:
        usage_df = pd.DataFrame(usage_stats['usage_by_day'])
        
        # Time series chart of usage
        fig = px.line(
            usage_df, 
            x="date", 
            y="quantity",
            title=f"{selected_type} Usage Over Time",
            labels={"date": "Date", "quantity": "Quantity Used"}
        )
        
        # Add trend line
        if len(usage_df) > 2:
            fig.add_traces(
                px.scatter(usage_df, x="date", y="quantity", trendline="ols").data[1]
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Usage by field
    if 'usage_by_field' in usage_stats and usage_stats['usage_by_field']:
        field_usage = pd.DataFrame(usage_stats['usage_by_field'])
        
        fig = px.pie(
            field_usage,
            values="quantity",
            names="field_name",
            title=f"{selected_type} Usage by Field",
            color_discrete_sequence=px.colors.sequential.Greens
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Efficiency metrics if available
    if 'efficiency' in usage_stats and usage_stats['efficiency']:
        st.subheader("Resource Efficiency Metrics")
        
        efficiency_data = []
        for field_id, metrics in usage_stats['efficiency'].items():
            # Get field name
            field_name = next((f.name for f in fields if f.id == field_id), f"Field {field_id}")
            
            efficiency_data.append({
                "Field": field_name,
                "Efficiency Score": metrics['score'],
                "Usage per Hectare": metrics['usage_per_ha'],
                "Yield per Unit": metrics.get('yield_per_unit', 0)
            })
        
        if efficiency_data:
            eff_df = pd.DataFrame(efficiency_data)
            
            # Bar chart of efficiency scores
            fig = px.bar(
                eff_df.sort_values("Efficiency Score"), 
                x="Field", 
                y="Efficiency Score",
                color="Efficiency Score",
                title="Resource Efficiency by Field",
                color_continuous_scale=px.colors.sequential.Greens,
                range_color=[0, 100]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Table with detailed metrics
            st.dataframe(eff_df, use_container_width=True, hide_index=True)
    
    # Recommendations based on analysis
    if 'recommendations' in usage_stats and usage_stats['recommendations']:
        st.subheader("Optimization Recommendations")
        
        for rec in usage_stats['recommendations']:
            with st.container():
                col1, col2 = st.columns([1, 5])
                
                with col1:
                    priority_color = "#FF5252" if rec['priority'] == "High" else "#FFC107" if rec['priority'] == "Medium" else "#4CAF50"
                    st.markdown(f"""
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background-color: {priority_color};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                    ">
                        {rec['priority'][0]}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{rec['issue']}**")
                    st.markdown(rec['recommendation'])
                
                st.markdown("---")

def normalize_quantity(quantity, unit, resource_type):
    """
    Normalize quantity to a common unit for comparison
    
    Args:
        quantity: Numerical quantity
        unit: Unit string (e.g., "Liters", "Kilograms")
        resource_type: Type of resource
        
    Returns:
        Normalized quantity value
    """
    # For volumetric units (water, liquid fertilizers, pesticides)
    if unit in ["Liters", "Gallons", "Cubic Meters"]:
        if unit == "Gallons":
            return quantity * 3.78541  # Convert to liters
        elif unit == "Cubic Meters":
            return quantity * 1000  # Convert to liters
        else:
            return quantity  # Already in liters
    
    # For mass units (solid fertilizers, seeds)
    elif unit in ["Kilograms", "Pounds", "Tons"]:
        if unit == "Pounds":
            return quantity * 0.453592  # Convert to kilograms
        elif unit == "Tons":
            return quantity * 1000  # Convert to kilograms
        else:
            return quantity  # Already in kilograms
    
    # For count units (pieces, units, bags)
    else:
        # Can't easily normalize these, so just return as is
        return quantity