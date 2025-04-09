import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

from db_utils import (
    get_all_farms,
    get_fields_by_farm,
    get_health_records_by_field,
    save_crop_recommendation,
    get_crop_recommendations_by_farm,
    mark_crop_recommendation_implemented
)

from utils.crop_recommendation import (
    get_crop_recommendations,
    get_crop_info,
    get_crop_price_trend,
    get_crop_demand
)

def show():
    st.markdown("<h1 class='main-header'>Crop Recommendations</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Get AI-powered crop recommendations based on your farm conditions</p>", unsafe_allow_html=True)
    
    # Farm selector
    farms = get_all_farms()
    
    if not farms:
        st.warning("No farms found. Please add a farm first.")
        return
    
    # Sidebar for farm selection and filters
    with st.sidebar:
        farm_names = [farm.name for farm in farms]
        selected_farm_name = st.selectbox("Select Farm", farm_names)
        
        # Get selected farm
        selected_farm = next((farm for farm in farms if farm.name == selected_farm_name), None)
        
        if not selected_farm:
            st.error("Selected farm not found.")
            return
        
        # Recommendation filters
        st.subheader("Recommendation Filters")
        
        investment_level = st.select_slider(
            "Investment Level",
            options=["Low", "Medium", "High"],
            value="Medium"
        )
        
        prioritize = st.radio(
            "Prioritize",
            ["Profit", "Sustainability", "Risk Minimization", "Water Efficiency"]
        )
        
        time_horizon = st.select_slider(
            "Time Horizon",
            options=["Short (3-4 months)", "Medium (5-8 months)", "Long (9+ months)"],
            value="Medium (5-8 months)"
        )
        
        # Show current/past recommendations
        st.subheader("Past Recommendations")
        show_past = st.checkbox("Show Past Recommendations", value=False)
    
    # Main area - tabs for recommendation and analysis
    if show_past:
        # Show past recommendations for the farm
        show_past_recommendations(selected_farm)
    else:
        # Show new recommendation interface
        show_recommendation_interface(selected_farm, investment_level, prioritize, time_horizon)

def show_recommendation_interface(farm, investment_level, prioritize, time_horizon):
    """Show interface for generating new crop recommendations"""
    st.header(f"Crop Recommendations for {farm.name}")
    
    # Get fields for this farm
    fields = get_fields_by_farm(farm.id)
    
    if not fields:
        st.info("No fields found for this farm. Please add fields first.")
        return
    
    # Options for field selection
    field_options = {field.id: field.name for field in fields}
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Field selector
        selected_field_id = st.selectbox(
            "Select Field for Recommendation",
            options=list(field_options.keys()),
            format_func=lambda x: field_options[x]
        )
        
        # Get selected field
        selected_field = next((field for field in fields if field.id == selected_field_id), None)
        
        if not selected_field:
            st.error("Selected field not found.")
            return
        
        # Show field details
        st.markdown(f"**Area:** {selected_field.area_size or 0} hectares")
        st.markdown(f"**Soil Type:** {selected_field.soil_type or 'Unknown'}")
        st.markdown(f"**Current Crop:** {selected_field.current_crop or 'None'}")
        
        # Get soil health from latest health record
        health_records = get_health_records_by_field(selected_field.id, limit=1)
        
        if health_records:
            latest_record = health_records[0]
            
            # Display soil health metrics
            st.subheader("Soil Health Metrics")
            
            # Display nutrient status with colored indicators
            cols = st.columns(3)
            
            with cols[0]:
                n_color = "#4CAF50" if latest_record.nitrogen_status == "Good" else "#FFC107" if latest_record.nitrogen_status == "Medium" else "#F44336"
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background-color: #f7f7f7; border-radius: 5px;'>
                    <div style='font-size: 16px; color: #666;'>Nitrogen</div>
                    <div style='font-size: 20px; font-weight: bold; color: {n_color};'>{latest_record.nitrogen_status}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cols[1]:
                p_color = "#4CAF50" if latest_record.phosphorus_status == "Good" else "#FFC107" if latest_record.phosphorus_status == "Medium" else "#F44336"
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background-color: #f7f7f7; border-radius: 5px;'>
                    <div style='font-size: 16px; color: #666;'>Phosphorus</div>
                    <div style='font-size: 20px; font-weight: bold; color: {p_color};'>{latest_record.phosphorus_status}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cols[2]:
                k_color = "#4CAF50" if latest_record.potassium_status == "Good" else "#FFC107" if latest_record.potassium_status == "Medium" else "#F44336"
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background-color: #f7f7f7; border-radius: 5px;'>
                    <div style='font-size: 16px; color: #666;'>Potassium</div>
                    <div style='font-size: 20px; font-weight: bold; color: {k_color};'>{latest_record.potassium_status}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No health records found for this field. Recommendations will be based on general factors only.")
    
    with col2:
        # Manual input of additional parameters
        st.subheader("Additional Parameters")
        
        # Location characteristics (if not in health record)
        rainfall = st.slider("Average Rainfall (mm/month)", 0, 500, 150)
        temperature = st.slider("Average Temperature (°C)", 0, 40, 22)
        
        # Economic factors
        market_access = st.select_slider(
            "Market Access",
            options=["Poor", "Moderate", "Good", "Excellent"],
            value="Good"
        )
        
        # Farming practices
        practices = st.multiselect(
            "Farming Practices",
            ["Conventional", "Organic", "Conservation", "Precision Agriculture", "Integrated Pest Management"],
            default=["Conventional"]
        )
    
    # Generate recommendation button
    if st.button("Generate Recommendations", type="primary"):
        with st.spinner("Analyzing farm data and generating recommendations..."):
            # Gather input data
            input_data = {
                "field_id": selected_field.id,
                "field_name": selected_field.name,
                "soil_type": selected_field.soil_type,
                "current_crop": selected_field.current_crop,
                "area_size": selected_field.area_size,
                "rainfall": rainfall,
                "temperature": temperature,
                "investment_level": investment_level,
                "priority": prioritize,
                "time_horizon": time_horizon,
                "market_access": market_access,
                "practices": practices
            }
            
            # Add soil health data if available
            if health_records:
                input_data["nitrogen_status"] = latest_record.nitrogen_status
                input_data["phosphorus_status"] = latest_record.phosphorus_status
                input_data["potassium_status"] = latest_record.potassium_status
                input_data["health_score"] = latest_record.health_score
                input_data["health_record_id"] = latest_record.id
            
            # Get crop recommendations
            recommendations = get_crop_recommendations(input_data)
            
            if recommendations:
                display_recommendations(recommendations, farm.id, selected_field.id)
            else:
                st.error("Failed to generate recommendations. Please try again.")
    
    # Additional tips and information
    with st.expander("Recommendation Tips"):
        st.markdown("""
        **Tips for better recommendations:**
        
        1. **Update soil health data** regularly for more accurate recommendations
        2. **Consider crop rotation** principles when selecting crops
        3. **Select different priorities** to see a range of crop options
        4. **Adjust time horizon** based on your planning needs
        5. **Try different investment levels** to see options at various price points
        """)

def display_recommendations(recommendations, farm_id, field_id):
    """Display crop recommendations and allow for saving"""
    st.subheader("Recommended Crops")
    
    # Create tabs for each recommended crop
    tabs = st.tabs([rec["crop"] for rec in recommendations])
    
    for i, (tab, recommendation) in enumerate(zip(tabs, recommendations)):
        with tab:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Main recommendation details
                st.markdown(f"### {recommendation['crop']} ({recommendation['suitability']:.1f}% Suitable)")
                
                # Crop image placeholder
                st.image("assets/default_farm.svg", width=150)
                
                # Rationale
                st.markdown("#### Why This Crop?")
                st.markdown(recommendation["rationale"])
                
                # Cultivation tips
                st.markdown("#### Cultivation Tips")
                st.markdown(recommendation["cultivation_tips"])
                
                # Risks
                st.markdown("#### Potential Risks")
                st.markdown(recommendation.get("risks", "No specific risks identified."))
            
            with col2:
                # Key metrics
                st.markdown("#### Key Metrics")
                
                metrics = [
                    {"label": "Growing Season", "value": recommendation["growing_season"]},
                    {"label": "Time to Harvest", "value": recommendation["time_to_harvest"]},
                    {"label": "Water Requirements", "value": recommendation["water_requirements"]},
                    {"label": "Fertilizer Needs", "value": recommendation["fertilizer_needs"]},
                    {"label": "Market Demand", "value": recommendation["market_demand"]},
                    {"label": "Estimated Yield", "value": recommendation["estimated_yield"]},
                    {"label": "Price Trend", "value": recommendation["price_trend"]},
                    {"label": "Investment Level", "value": recommendation["investment_level"]}
                ]
                
                for metric in metrics:
                    st.markdown(f"""
                    <div style='margin-bottom: 10px;'>
                        <div style='font-size: 14px; color: #666;'>{metric['label']}</div>
                        <div style='font-size: 16px; font-weight: bold;'>{metric['value']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Save recommendation button
                if st.button("Save This Recommendation", key=f"save_{i}"):
                    # Save to database
                    save_crop_recommendation(
                        farm_id=farm_id,
                        crop=recommendation["crop"],
                        suitability=recommendation["suitability"],
                        growing_season=recommendation["growing_season"],
                        time_to_harvest=recommendation["time_to_harvest"],
                        water_requirements=recommendation["water_requirements"],
                        fertilizer_needs=recommendation["fertilizer_needs"],
                        market_demand=recommendation["market_demand"],
                        estimated_yield=recommendation["estimated_yield"],
                        price_trend=recommendation["price_trend"],
                        investment_level=recommendation["investment_level"],
                        rationale=recommendation["rationale"],
                        cultivation_tips=recommendation["cultivation_tips"],
                        risks=recommendation.get("risks", "")
                    )
                    
                    st.success(f"Saved {recommendation['crop']} recommendation!")

def show_past_recommendations(farm):
    """Show past crop recommendations for a farm"""
    st.header(f"Past Recommendations for {farm.name}")
    
    # Get saved recommendations
    recommendations = get_crop_recommendations_by_farm(farm.id)
    
    if not recommendations:
        st.info("No saved recommendations found for this farm.")
        return
    
    # Group recommendations by implemented status
    active_recs = [r for r in recommendations if not r.implemented]
    implemented_recs = [r for r in recommendations if r.implemented]
    
    # Show active recommendations
    if active_recs:
        st.subheader("Active Recommendations")
        
        for rec in active_recs:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"#### {rec.crop}")
                    st.markdown(f"**Suitability:** {rec.suitability:.1f}%")
                    
                    # Truncate rationale if too long
                    rationale = rec.rationale
                    if len(rationale) > 150:
                        rationale = rationale[:150] + "..."
                        
                    st.markdown(rationale)
                
                with col2:
                    # Key metrics
                    st.markdown(f"**Growing Season:** {rec.growing_season}")
                    st.markdown(f"**Harvest Time:** {rec.time_to_harvest}")
                    st.markdown(f"**Market Demand:** {rec.market_demand}")
                    st.markdown(f"**Investment:** {rec.investment_level}")
                
                with col3:
                    # Implementation button
                    st.markdown("&nbsp;", unsafe_allow_html=True)  # Spacer
                    if st.button("Mark Implemented", key=f"implement_{rec.id}"):
                        mark_crop_recommendation_implemented(rec.id)
                        st.success("Recommendation marked as implemented!")
                        st.rerun()
                
                st.markdown("---")
    
    # Show implemented recommendations
    if implemented_recs:
        with st.expander("Implemented Recommendations"):
            for rec in implemented_recs:
                st.markdown(f"**{rec.crop}** (Implemented on {rec.implementation_date.strftime('%Y-%m-%d') if rec.implementation_date else 'Unknown'})")
                st.markdown(f"Suitability: {rec.suitability:.1f}%")
                st.markdown("---")
    
    # Historical analysis
    if len(recommendations) > 1:
        st.subheader("Recommendation Analysis")
        
        # Create data for visualization
        rec_data = []
        
        for rec in recommendations:
            rec_data.append({
                "Crop": rec.crop,
                "Suitability": rec.suitability,
                "Date": rec.date,
                "Status": "Implemented" if rec.implemented else "Active",
                "Market Demand": rec.market_demand,
                "Investment Level": rec.investment_level
            })
        
        rec_df = pd.DataFrame(rec_data)
        
        # Crop suitability chart
        fig = px.bar(
            rec_df.sort_values("Suitability", ascending=False), 
            x="Crop", 
            y="Suitability",
            color="Status",
            title="Crop Suitability Comparison",
            color_discrete_map={"Implemented": "#4CAF50", "Active": "#2196F3"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Market demand distribution
        demand_counts = rec_df["Market Demand"].value_counts().reset_index()
        demand_counts.columns = ["Demand", "Count"]
        
        fig2 = px.pie(
            demand_counts,
            values="Count",
            names="Demand",
            title="Market Demand Distribution of Recommendations",
            color_discrete_sequence=px.colors.sequential.Greens
        )
        
        st.plotly_chart(fig2, use_container_width=True)