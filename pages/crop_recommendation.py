import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
from db_utils import (
    get_farm_by_id, get_fields_by_farm, save_crop_recommendation,
    get_crop_recommendations_by_farm, mark_crop_recommendation_implemented
)
from utils.crop_recommendation import (
    get_crop_recommendations, get_rotation_suggestions, get_rotation_benefits
)

def show():
    st.title("Crop Recommendations")
    
    # Get farm ID from session state
    if 'selected_farm_id' not in st.session_state:
        st.error("No farm selected. Please select a farm from the sidebar.")
        return
    
    farm_id = st.session_state['selected_farm_id']
    farm = get_farm_by_id(farm_id)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Crop Recommendations", "Crop Rotation Planner", "Recommendation History"])
    
    # CROP RECOMMENDATIONS TAB
    with tab1:
        st.header("Crop Recommendation Engine")
        
        # Form for recommendation parameters
        with st.form("recommendation_form"):
            st.subheader("Enter Field Parameters")
            
            # Create two columns for input
            col1, col2 = st.columns(2)
            
            with col1:
                # Soil parameters
                st.write("**Soil Parameters**")
                soil_type = st.selectbox(
                    "Soil Type",
                    ["Loam", "Sandy Loam", "Clay Loam", "Clay", "Sandy", "Silt Loam"]
                )
                soil_ph = st.slider("Soil pH", 4.0, 9.0, 6.5, 0.1)
                soil_fertility = st.selectbox(
                    "Soil Fertility",
                    ["Low", "Medium", "High"]
                )
                
                # Water availability
                st.write("**Water Resources**")
                water_availability = st.selectbox(
                    "Water Availability",
                    ["Limited", "Moderate", "Abundant"]
                )
                irrigation_system = st.selectbox(
                    "Irrigation System",
                    ["None", "Drip", "Sprinkler", "Flood"]
                )
            
            with col2:
                # Climate parameters
                st.write("**Climate Parameters**")
                climate_zone = st.selectbox(
                    "Climate Zone",
                    ["Tropical", "Subtropical", "Temperate", "Arid", "Mediterranean"]
                )
                avg_temperature = st.slider("Average Temperature (°C)", 0, 40, 25, 1)
                annual_rainfall = st.slider("Annual Rainfall (mm)", 100, 3000, 1000, 50)
                
                # Market factors
                st.write("**Market Factors**")
                market_distance = st.slider("Distance to Market (km)", 1, 100, 20, 1)
                investment_capacity = st.selectbox(
                    "Investment Capacity",
                    ["Low", "Medium", "High"]
                )
            
            # Submit button
            submit = st.form_submit_button("Generate Recommendations")
        
        # Generate recommendations when submitted
        if submit:
            # Show spinner during "calculation"
            with st.spinner("Analyzing parameters and generating crop recommendations..."):
                # Prepare parameters
                params = {
                    "soil_type": soil_type,
                    "soil_ph": soil_ph,
                    "soil_fertility": soil_fertility,
                    "water_availability": water_availability,
                    "irrigation_system": irrigation_system,
                    "climate_zone": climate_zone,
                    "avg_temperature": avg_temperature,
                    "annual_rainfall": annual_rainfall,
                    "market_distance": market_distance,
                    "investment_capacity": investment_capacity
                }
                
                # Get recommendations
                recommendations = get_crop_recommendations(params)
                
                # Store in session state for later use
                st.session_state['crop_recommendations'] = recommendations
            
            # Show success message
            st.success("Generated crop recommendations based on your parameters!")
        
        # Display recommendations if available
        if 'crop_recommendations' in st.session_state:
            recommendations = st.session_state['crop_recommendations']
            
            st.subheader("Recommended Crops")
            
            # Display each recommendation as a card
            for i, rec in enumerate(recommendations):
                with st.container():
                    cols = st.columns([4, 1])
                    
                    with cols[0]:
                        # Main card with recommendation
                        with st.expander(f"{i+1}. {rec['crop']} - Suitability: {rec['suitability']}%", expanded=(i == 0)):
                            # Basic info
                            st.markdown(f"**Growing Season:** {rec['growing_season']}")
                            st.markdown(f"**Time to Harvest:** {rec['time_to_harvest']}")
                            
                            # Create columns for details
                            detail_cols = st.columns(3)
                            
                            with detail_cols[0]:
                                st.markdown("**Resource Requirements**")
                                st.markdown(f"Water: {rec['water_requirements']}")
                                st.markdown(f"Fertilizer: {rec['fertilizer_needs']}")
                                st.markdown(f"Investment: {rec['investment_level']}")
                            
                            with detail_cols[1]:
                                st.markdown("**Market Analysis**")
                                st.markdown(f"Market Demand: {rec['market_demand']}")
                                st.markdown(f"Price Trend: {rec['price_trend']}")
                                st.markdown(f"Est. Yield: {rec['estimated_yield']}")
                            
                            with detail_cols[2]:
                                st.markdown("**Key Benefits**")
                                for point in rec['rationale'].split('. '):
                                    if point.strip():
                                        st.markdown(f"• {point.strip()}")
                            
                            # Detailed sections
                            st.subheader("Cultivation Tips")
                            st.write(rec['cultivation_tips'])
                            
                            if 'risks' in rec and rec['risks']:
                                st.subheader("Potential Risks")
                                st.write(rec['risks'])
                    
                    with cols[1]:
                        # Save recommendation button
                        if st.button(f"Save #{i+1}", key=f"save_rec_{i}"):
                            save_crop_recommendation(
                                farm_id=farm_id,
                                crop=rec['crop'],
                                suitability=rec['suitability'],
                                growing_season=rec['growing_season'],
                                time_to_harvest=rec['time_to_harvest'],
                                water_requirements=rec['water_requirements'],
                                fertilizer_needs=rec['fertilizer_needs'],
                                market_demand=rec['market_demand'],
                                estimated_yield=rec['estimated_yield'],
                                price_trend=rec['price_trend'],
                                investment_level=rec['investment_level'],
                                rationale=rec['rationale'],
                                cultivation_tips=rec['cultivation_tips'],
                                risks=rec.get('risks', '')
                            )
                            st.success(f"Saved {rec['crop']} recommendation to database!")
                
                # Add some spacing between recommendations
                st.write("---")
            
            # Comparison chart
            st.subheader("Recommendation Comparison")
            
            # Extract data for the chart
            chart_data = pd.DataFrame({
                'Crop': [rec['crop'] for rec in recommendations],
                'Suitability': [rec['suitability'] for rec in recommendations],
                'Water Need': [100 if 'High' in rec['water_requirements'] else 
                               70 if 'Medium' in rec['water_requirements'] else 40 
                               for rec in recommendations],
                'Investment': [100 if 'High' in rec['investment_level'] else 
                               70 if 'Medium' in rec['investment_level'] else 40 
                               for rec in recommendations],
                'Market': [100 if 'High' in rec['market_demand'] else 
                           70 if 'Medium' in rec['market_demand'] else 40 
                           for rec in recommendations]
            })
            
            # Create bar chart
            fig = px.bar(
                chart_data,
                x='Crop',
                y='Suitability',
                color='Suitability',
                color_continuous_scale='Viridis',
                title='Crop Suitability Scores'
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title="Crop",
                yaxis_title="Suitability Score (%)",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Radar chart for comparing different aspects
            fig = px.line_polar(
                chart_data, 
                r=[chart_data['Suitability'], chart_data['Water Need'], 
                   chart_data['Investment'], chart_data['Market']],
                theta=['Suitability', 'Water Need', 'Investment', 'Market'],
                line_close=True,
                color=chart_data['Crop'],
                title="Multi-factor Comparison"
            )
            
            # Customize layout
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # CROP ROTATION PLANNER TAB
    with tab2:
        st.header("Crop Rotation Planner")
        
        # Get fields for this farm
        fields = get_fields_by_farm(farm_id)
        
        if not fields:
            st.warning("No fields found for this farm. Please add fields first.")
        else:
            # Field selection
            field_names = [field.name for field in fields]
            
            selected_field = st.selectbox(
                "Select Field for Rotation Planning",
                field_names
            )
            
            # Get the field object
            field = next((f for f in fields if f.name == selected_field), None)
            
            if field:
                st.write(f"**Current Crop:** {field.current_crop or 'None'}")
                
                # If no current crop, prompt to add one
                if not field.current_crop:
                    st.warning("No current crop specified for this field. Please update field information.")
                    
                    # Form to add a current crop
                    with st.form("add_current_crop"):
                        current_crops = st.multiselect(
                            "Select Crops Currently or Recently Grown in this Field",
                            ["Maize", "Wheat", "Rice", "Soybeans", "Beans", "Potatoes", 
                             "Tomatoes", "Cotton", "Sunflower", "Barley", "Oats", "Lentils"]
                        )
                        
                        if st.form_submit_button("Set Current Crops"):
                            # In a real application, we would update the field in the database
                            st.session_state['current_crops'] = current_crops
                            st.success("Current crops set for rotation planning.")
                            st.experimental_rerun()
                else:
                    # Use the current crop from the field
                    st.session_state['current_crops'] = [field.current_crop]
            
            # Generate rotation suggestions if we have current crops
            if 'current_crops' in st.session_state and st.session_state['current_crops']:
                current_crops = st.session_state['current_crops']
                
                # Get rotation suggestions
                rotation_suggestions = get_rotation_suggestions(current_crops)
                
                # Display rotation plan
                st.subheader("Suggested Crop Rotation Plan")
                
                # Create a timeline visualization
                seasons = ["Current", "Next Season", "Following Season", "Year 2 Season 1", "Year 2 Season 2"]
                crops = [", ".join(current_crops)]
                
                # Add suggested crops for future seasons
                for i in range(min(4, len(rotation_suggestions))):
                    crops.append(rotation_suggestions[i]['crop'])
                
                # Crop Rotation Timeline
                rotation_data = pd.DataFrame({
                    'Season': seasons[:len(crops)],
                    'Crop': crops,
                    'Order': range(len(crops))
                })
                
                fig = px.line(
                    rotation_data,
                    x='Order',
                    y='Crop',
                    text='Crop',
                    markers=True,
                    title="Crop Rotation Timeline"
                )
                
                # Add connecting lines and customize
                fig.update_traces(textposition='top center')
                fig.update_layout(
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(crops))),
                        ticktext=seasons[:len(crops)]
                    ),
                    xaxis_title="Season",
                    yaxis_title="",
                    yaxis_showticklabels=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show rotation benefits
                st.subheader("Benefits of This Rotation Plan")
                
                rotation_benefits = get_rotation_benefits(current_crops, [s['crop'] for s in rotation_suggestions])
                
                for benefit in rotation_benefits:
                    st.markdown(f"• {benefit}")
                
                # Detailed crop suggestions
                st.subheader("Detailed Rotation Suggestions")
                
                for i, suggestion in enumerate(rotation_suggestions[:4]):
                    with st.expander(f"Season {i+1}: {suggestion['crop']}", expanded=(i == 0)):
                        st.write(f"**Recommendation:** {suggestion['crop']}")
                        st.write(f"**Rationale:** {suggestion['rationale']}")
                        
                        if 'benefits' in suggestion:
                            st.write("**Benefits:**")
                            for benefit in suggestion['benefits']:
                                st.write(f"• {benefit}")
                        
                        if 'notes' in suggestion:
                            st.write(f"**Notes:** {suggestion['notes']}")
    
    # RECOMMENDATION HISTORY TAB
    with tab3:
        st.header("Recommendation History")
        
        # Get saved recommendations
        recommendations = get_crop_recommendations_by_farm(farm_id)
        
        if not recommendations:
            st.info("No saved crop recommendations found. Generate and save recommendations using the Crop Recommendations tab.")
        else:
            # Display each saved recommendation
            for i, rec in enumerate(recommendations):
                with st.expander(
                    f"{rec.date.strftime('%Y-%m-%d')} - {rec.crop} (Suitability: {rec.suitability}%)",
                    expanded=(i == 0)
                ):
                    # Implementation status
                    status_col, action_col = st.columns([3, 1])
                    
                    with status_col:
                        if rec.implemented:
                            st.success("✓ Implemented")
                        else:
                            st.info("○ Not Implemented")
                    
                    with action_col:
                        if not rec.implemented:
                            if st.button("Mark Implemented", key=f"implement_{rec.id}"):
                                mark_crop_recommendation_implemented(rec.id)
                                st.success("Marked as implemented!")
                                st.experimental_rerun()
                    
                    # Basic info
                    st.markdown(f"**Growing Season:** {rec.growing_season}")
                    st.markdown(f"**Time to Harvest:** {rec.time_to_harvest}")
                    
                    # Create columns for details
                    detail_cols = st.columns(3)
                    
                    with detail_cols[0]:
                        st.markdown("**Resource Requirements**")
                        st.markdown(f"Water: {rec.water_requirements}")
                        st.markdown(f"Fertilizer: {rec.fertilizer_needs}")
                        st.markdown(f"Investment: {rec.investment_level}")
                    
                    with detail_cols[1]:
                        st.markdown("**Market Analysis**")
                        st.markdown(f"Market Demand: {rec.market_demand}")
                        st.markdown(f"Price Trend: {rec.price_trend}")
                        st.markdown(f"Est. Yield: {rec.estimated_yield}")
                    
                    with detail_cols[2]:
                        st.markdown("**Key Benefits**")
                        for point in rec.rationale.split('. '):
                            if point.strip():
                                st.markdown(f"• {point.strip()}")
                    
                    # Detailed sections
                    st.subheader("Cultivation Tips")
                    st.write(rec.cultivation_tips)
                    
                    if rec.risks:
                        st.subheader("Potential Risks")
                        st.write(rec.risks)