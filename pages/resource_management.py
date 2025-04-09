import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db_utils import (
    get_farm_by_id, get_fields_by_farm, get_resources_by_farm,
    add_resource, update_resource_quantity, record_resource_usage,
    get_resource_usage_stats, get_resource_usage_by_field
)
from utils.resource_management import (
    get_water_requirements, get_fertilizer_requirements,
    get_water_saving_tips, get_fertilizer_application_tips
)
from utils.data_processing import generate_time_series

def show():
    st.title("Resource Management")
    
    # Get farm ID from session state
    if 'selected_farm_id' not in st.session_state:
        st.error("No farm selected. Please select a farm from the sidebar.")
        return
    
    farm_id = st.session_state['selected_farm_id']
    farm = get_farm_by_id(farm_id)
    
    if not farm:
        st.error("Selected farm not found in the database.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Resource Inventory", "Resource Planning", "Usage History"])
    
    # TAB 1: RESOURCE INVENTORY
    with tab1:
        st.header("Resource Inventory")
        
        # Current Resources
        resources = get_resources_by_farm(farm_id)
        
        if resources:
            # Group resources by type
            resource_types = {}
            for resource in resources:
                if resource.type not in resource_types:
                    resource_types[resource.type] = []
                resource_types[resource.type].append(resource)
            
            # Display resources by type
            for resource_type, type_resources in resource_types.items():
                st.subheader(f"{resource_type} Resources")
                
                # Create a DataFrame for easy display
                data = []
                for res in type_resources:
                    data.append({
                        "ID": res.id,
                        "Name": res.name,
                        "Quantity": res.quantity,
                        "Unit": res.unit,
                        "Last Updated": res.last_updated.strftime("%Y-%m-%d") if res.last_updated else "N/A"
                    })
                
                df = pd.DataFrame(data)
                
                # Display the dataframe
                st.dataframe(df, hide_index=True)
                
                # Create a chart of resource quantities
                if len(type_resources) > 1:
                    fig = px.bar(
                        df,
                        x="Name",
                        y="Quantity",
                        title=f"{resource_type} Quantities",
                        labels={"Name": "Resource", "Quantity": f"Quantity ({type_resources[0].unit})"},
                        color="Quantity",
                        color_continuous_scale="Viridis"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No resources found for this farm. Add resources below.")
        
        # Add New Resource Form
        st.subheader("Add New Resource")
        
        with st.form("add_resource_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Resource Name")
                resource_type = st.selectbox(
                    "Resource Type",
                    ["Water", "Fertilizer", "Seeds", "Pesticide", "Equipment", "Fuel", "Other"]
                )
            
            with col2:
                quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
                unit = st.text_input("Unit (e.g., liters, kg)")
            
            submit = st.form_submit_button("Add Resource")
            
            if submit:
                if name and resource_type and quantity >= 0 and unit:
                    add_resource(farm_id, name, resource_type, quantity, unit)
                    st.success(f"Added {quantity} {unit} of {name} to inventory.")
                    st.experimental_rerun()
                else:
                    st.error("Please fill all fields with valid values.")
        
        # Update Resource Form
        if resources:
            st.subheader("Update Resource Quantity")
            
            with st.form("update_resource_form"):
                # Create a dictionary of resource names and IDs for selection
                resource_options = {f"{r.name} ({r.quantity} {r.unit})": r.id for r in resources}
                
                # Create columns for the form
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_resource = st.selectbox(
                        "Select Resource",
                        list(resource_options.keys())
                    )
                    
                    # Get the selected resource ID
                    resource_id = resource_options[selected_resource]
                    
                    # Find the resource object
                    resource = next((r for r in resources if r.id == resource_id), None)
                    
                with col2:
                    # Show current quantity
                    if resource:
                        st.write(f"Current Quantity: {resource.quantity} {resource.unit}")
                        
                        # Input for new quantity
                        new_quantity = st.number_input(
                            "New Quantity",
                            min_value=0.0,
                            value=resource.quantity,
                            step=0.1
                        )
                
                # Submit button
                submit = st.form_submit_button("Update Quantity")
                
                if submit and resource:
                    if new_quantity >= 0:
                        update_resource_quantity(resource_id, new_quantity)
                        st.success(f"Updated {resource.name} quantity to {new_quantity} {resource.unit}.")
                        st.experimental_rerun()
                    else:
                        st.error("Quantity cannot be negative.")
        
        # Record Resource Usage Form
        if resources and get_fields_by_farm(farm_id):
            st.subheader("Record Resource Usage")
            
            with st.form("record_usage_form"):
                # Get fields for this farm
                fields = get_fields_by_farm(farm_id)
                field_options = {field.name: field.id for field in fields}
                
                # Create columns for the form
                col1, col2 = st.columns(2)
                
                with col1:
                    # Resource selection
                    resource_options = {f"{r.name} ({r.type})": r.id for r in resources}
                    selected_resource = st.selectbox(
                        "Select Resource",
                        list(resource_options.keys()),
                        key="usage_resource"
                    )
                    
                    # Get the selected resource ID
                    resource_id = resource_options[selected_resource]
                    
                    # Find the resource object
                    resource = next((r for r in resources if r.id == resource_id), None)
                    
                    # Field selection
                    selected_field = st.selectbox(
                        "Select Field",
                        list(field_options.keys())
                    )
                    
                    # Get the selected field ID
                    field_id = field_options[selected_field]
                
                with col2:
                    # Show current available quantity
                    if resource:
                        st.write(f"Available: {resource.quantity} {resource.unit}")
                        
                        # Input for usage quantity
                        usage_quantity = st.number_input(
                            f"Usage Quantity ({resource.unit})",
                            min_value=0.0,
                            max_value=resource.quantity,
                            step=0.1
                        )
                    
                    # Application method
                    application_method = st.text_input("Application Method (optional)")
                    
                    # Notes
                    notes = st.text_area("Notes (optional)", height=80)
                
                # Submit button
                submit = st.form_submit_button("Record Usage")
                
                if submit and resource:
                    if 0 < usage_quantity <= resource.quantity:
                        # Record the usage
                        record_resource_usage(resource_id, field_id, usage_quantity, application_method, notes)
                        
                        # Update the resource quantity
                        new_quantity = resource.quantity - usage_quantity
                        update_resource_quantity(resource_id, new_quantity)
                        
                        st.success(f"Recorded usage of {usage_quantity} {resource.unit} of {resource.name} on {selected_field}.")
                        st.experimental_rerun()
                    elif usage_quantity == 0:
                        st.warning("Usage quantity cannot be zero.")
                    else:
                        st.error("Usage quantity cannot exceed available quantity.")
    
    # TAB 2: RESOURCE PLANNING
    with tab2:
        st.header("Resource Planning")
        
        # Get fields for this farm
        fields = get_fields_by_farm(farm_id)
        
        if not fields:
            st.info("No fields found for this farm. Add fields to plan resources.")
        else:
            # Resource calculator
            st.subheader("Resource Requirement Calculator")
            
            # Field selection
            field_options = {field.name: field for field in fields}
            selected_field_name = st.selectbox(
                "Select Field",
                list(field_options.keys()),
                key="planning_field"
            )
            
            # Get the selected field
            field = field_options[selected_field_name]
            
            # Display field info
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Area:** {field.area_size or 'Not specified'} hectares")
                st.write(f"**Soil Type:** {field.soil_type or 'Not specified'}")
            
            with col2:
                st.write(f"**Current Crop:** {field.current_crop or 'None'}")
                if field.planting_date:
                    days_since_planting = (datetime.now() - field.planting_date).days
                    st.write(f"**Days Since Planting:** {days_since_planting}")
            
            # Create columns for water and fertilizer calculators
            water_col, fertilizer_col = st.columns(2)
            
            # WATER CALCULATOR
            with water_col:
                st.subheader("Water Requirements")
                
                with st.form("water_calculator_form"):
                    # Crop selection
                    crop = st.selectbox(
                        "Crop Type",
                        ["Maize", "Rice", "Wheat", "Soybeans", "Tomatoes", 
                         "Potatoes", "Beans", "Cotton", "Sunflower", "Cassava"],
                        index=0 if not field.current_crop else 0
                    )
                    
                    # Growth stage selection
                    growth_stage = st.selectbox(
                        "Growth Stage",
                        ["Germination", "Vegetative", "Flowering", "Yield Formation", "Ripening"]
                    )
                    
                    # Environmental parameters
                    temperature = st.slider("Temperature (°C)", 0, 40, 25)
                    rainfall = st.slider("Recent Rainfall (mm)", 0, 100, 0)
                    
                    # Calculate button
                    calculate = st.form_submit_button("Calculate Water Needs")
                    
                    if calculate:
                        if field.area_size and field.soil_type:
                            # Calculate water requirements
                            water_req = get_water_requirements(
                                crop, growth_stage, field.area_size, field.soil_type, 
                                temperature, rainfall
                            )
                            
                            # Store in session state for display
                            st.session_state['water_requirements'] = {
                                'total': water_req,
                                'per_ha': water_req / field.area_size if field.area_size > 0 else 0
                            }
                        else:
                            st.error("Field area size and soil type must be specified.")
                
                # Display water requirements if calculated
                if 'water_requirements' in st.session_state:
                    req = st.session_state['water_requirements']
                    
                    st.success(f"**Total Water Needed:** {req['total']:,} liters")
                    st.info(f"**Per Hectare:** {req['per_ha']:,.1f} liters/ha")
                    
                    # Water saving tip
                    with st.expander("Water Saving Tip"):
                        st.write(get_water_saving_tips())
            
            # FERTILIZER CALCULATOR
            with fertilizer_col:
                st.subheader("Fertilizer Requirements")
                
                with st.form("fertilizer_calculator_form"):
                    # Crop selection
                    fert_crop = st.selectbox(
                        "Crop Type",
                        ["Maize", "Rice", "Wheat", "Soybeans", "Tomatoes", 
                         "Potatoes", "Beans", "Cotton", "Sunflower", "Cassava"],
                        index=0 if not field.current_crop else 0,
                        key="fert_crop"
                    )
                    
                    # Growth stage selection
                    fert_growth_stage = st.selectbox(
                        "Growth Stage",
                        ["Germination", "Vegetative", "Flowering", "Yield Formation", "Ripening"],
                        key="fert_growth_stage"
                    )
                    
                    # Soil nutrients (optional)
                    st.write("Soil Nutrient Levels (optional, kg/ha)")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nitrogen = st.number_input("Nitrogen (N)", min_value=0.0, step=1.0)
                    
                    with col2:
                        phosphorus = st.number_input("Phosphorus (P)", min_value=0.0, step=1.0)
                    
                    with col3:
                        potassium = st.number_input("Potassium (K)", min_value=0.0, step=1.0)
                    
                    # Soil nutrients dictionary
                    soil_nutrients = {
                        "n": nitrogen,
                        "p": phosphorus,
                        "k": potassium
                    } if nitrogen > 0 or phosphorus > 0 or potassium > 0 else None
                    
                    # Calculate button
                    calculate_fert = st.form_submit_button("Calculate Fertilizer Needs")
                    
                    if calculate_fert:
                        if field.area_size:
                            # Calculate fertilizer requirements
                            fert_req = get_fertilizer_requirements(
                                fert_crop, fert_growth_stage, field.area_size, soil_nutrients
                            )
                            
                            # Store in session state for display
                            st.session_state['fertilizer_requirements'] = fert_req
                        else:
                            st.error("Field area size must be specified.")
                
                # Display fertilizer requirements if calculated
                if 'fertilizer_requirements' in st.session_state:
                    fert_req = st.session_state['fertilizer_requirements']
                    
                    # Display required nutrients
                    st.success("**Required Nutrients:**")
                    for nutrient, amount in fert_req['nutrient_requirements'].items():
                        st.write(f"• {nutrient}: {amount} kg")
                    
                    # Display recommended fertilizer types
                    st.info("**Recommended Fertilizer Types:**")
                    for fert_type in fert_req['fertilizer_types']:
                        st.write(f"• {fert_type}")
                    
                    # Application timing and notes
                    with st.expander("Application Timing"):
                        st.write(fert_req['application_timing'])
                    
                    with st.expander("Application Notes"):
                        st.write(fert_req['notes'])
                    
                    # Fertilizer application tip
                    with st.expander("Fertilizer Application Tip"):
                        st.write(get_fertilizer_application_tips())
            
            # Resource Forecast
            st.subheader("Resource Forecast (30 Days)")
            
            # Get current resources
            resources = get_resources_by_farm(farm_id)
            resource_types = set(r.type for r in resources)
            
            # Generate forecast for each resource type
            if resources:
                # Create columns for water and fertilizer forecasts if those types exist
                forecast_cols = st.columns(min(2, len(resource_types)))
                
                col_idx = 0
                for resource_type in ["Water", "Fertilizer"]:
                    if resource_type in resource_types:
                        with forecast_cols[col_idx]:
                            st.write(f"**{resource_type} Forecast**")
                            
                            # Generate a synthetic forecast for demonstration
                            # In a real app, this would use actual historical data and machine learning
                            forecast_data = generate_time_series(
                                days=30,
                                base_value=1000 if resource_type == "Water" else 50,
                                volatility=100 if resource_type == "Water" else 5,
                                trend=10 if resource_type == "Water" else 1
                            )
                            
                            # Create forecast chart
                            fig = px.line(
                                forecast_data,
                                x="date",
                                y="value",
                                title=f"Projected {resource_type} Usage",
                                labels={"date": "Date", "value": f"Usage ({resources[col_idx].unit})"}
                            )
                            
                            # Add current inventory line
                            total_inventory = sum(r.quantity for r in resources if r.type == resource_type)
                            fig.add_hline(
                                y=total_inventory, 
                                line_dash="dash", 
                                line_color="green",
                                annotation_text=f"Current Inventory ({total_inventory:.1f})",
                                annotation_position="bottom right"
                            )
                            
                            # Add "Low Inventory" threshold line (30% of current)
                            low_threshold = total_inventory * 0.3
                            fig.add_hline(
                                y=low_threshold, 
                                line_dash="dash", 
                                line_color="red",
                                annotation_text="Low Inventory Threshold",
                                annotation_position="bottom left"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Calculate days until resupply needed
                            if forecast_data["value"].sum() > 0:
                                usage_per_day = forecast_data["value"].mean()
                                days_until_resupply = int(low_threshold / usage_per_day) if usage_per_day > 0 else 30
                                days_until_resupply = min(30, max(0, days_until_resupply))
                                
                                if days_until_resupply < 7:
                                    st.warning(f"⚠️ Resupply needed in approximately {days_until_resupply} days!")
                                elif days_until_resupply < 14:
                                    st.info(f"ℹ️ Resupply may be needed in about {days_until_resupply} days.")
                                else:
                                    st.success(f"✓ Inventory should be sufficient for at least {days_until_resupply} days.")
                        
                        col_idx += 1
                        if col_idx >= len(forecast_cols):
                            break
            else:
                st.info("Add resources to see forecast data.")
    
    # TAB 3: USAGE HISTORY
    with tab3:
        st.header("Resource Usage History")
        
        # Get fields for this farm
        fields = get_fields_by_farm(farm_id)
        
        if not fields:
            st.info("No fields found for this farm.")
        else:
            # Field selection for usage history
            field_options = {field.name: field.id for field in fields}
            field_options["All Fields"] = None  # Option to view all fields
            
            selected_field_name = st.selectbox(
                "Select Field",
                list(field_options.keys()),
                key="history_field"
            )
            
            # Get the selected field ID (None for all fields)
            selected_field_id = field_options[selected_field_name]
            
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
            
            # Ensure valid date range
            if start_date <= end_date:
                # Get resource usage for the selected field(s) and date range
                if selected_field_id is not None:
                    usage_records = get_resource_usage_by_field(
                        selected_field_id,
                        start_date=start_date,
                        end_date=end_date
                    )
                else:
                    # Combine usage from all fields
                    usage_records = []
                    for field_id in field_options.values():
                        if field_id is not None:
                            field_usage = get_resource_usage_by_field(
                                field_id,
                                start_date=start_date,
                                end_date=end_date
                            )
                            usage_records.extend(field_usage)
                
                if usage_records:
                    # Process usage records
                    usage_data = []
                    for record in usage_records:
                        field = next((f for f in fields if f.id == record.field_id), None)
                        field_name = field.name if field else "Unknown"
                        
                        usage_data.append({
                            "Date": record.date,
                            "Field": field_name,
                            "Resource": record.resource.name,
                            "Type": record.resource.type,
                            "Quantity": record.quantity,
                            "Unit": record.resource.unit,
                            "Application Method": record.application_method or "Not specified",
                            "Notes": record.notes or ""
                        })
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(usage_data)
                    
                    # Display usage table
                    st.subheader("Usage Records")
                    st.dataframe(df[["Date", "Field", "Resource", "Type", "Quantity", "Unit"]], hide_index=True)
                    
                    # Create summary visualizations
                    st.subheader("Usage Summary")
                    
                    # Summary by resource type
                    type_summary = df.groupby("Type").agg({"Quantity": "sum"}).reset_index()
                    
                    # Create pie chart for resource type distribution
                    fig = px.pie(
                        type_summary,
                        names="Type",
                        values="Quantity",
                        title="Resource Usage by Type"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary by field
                    if selected_field_id is None and len(field_options) > 1:
                        field_summary = df.groupby("Field").agg({"Quantity": "sum"}).reset_index()
                        
                        # Create bar chart for field distribution
                        fig = px.bar(
                            field_summary,
                            x="Field",
                            y="Quantity",
                            title="Resource Usage by Field",
                            color="Field"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Timeline of usage
                    # Convert date column to datetime if it's not already
                    if not pd.api.types.is_datetime64_dtype(df["Date"]):
                        df["Date"] = pd.to_datetime(df["Date"])
                    
                    # Group by date and resource type
                    timeline_data = df.groupby(["Date", "Type"]).agg({"Quantity": "sum"}).reset_index()
                    
                    # Create line chart
                    fig = px.line(
                        timeline_data,
                        x="Date",
                        y="Quantity",
                        color="Type",
                        title="Resource Usage Timeline",
                        markers=True
                    )
                    
                    # Customize layout
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Quantity Used",
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed usage records in expandable sections
                    st.subheader("Detailed Records")
                    
                    for i, record in enumerate(sorted(usage_data, key=lambda x: x["Date"], reverse=True)):
                        with st.expander(f"{record['Date'].strftime('%Y-%m-%d')} - {record['Resource']} ({record['Quantity']} {record['Unit']})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Field:** {record['Field']}")
                                st.write(f"**Resource:** {record['Resource']} ({record['Type']})")
                                st.write(f"**Quantity:** {record['Quantity']} {record['Unit']}")
                            
                            with col2:
                                st.write(f"**Application Method:** {record['Application Method']}")
                                st.write(f"**Notes:** {record['Notes']}")
                else:
                    st.info(f"No resource usage records found for {selected_field_name} in the selected date range.")
            else:
                st.error("End date must be after start date.")