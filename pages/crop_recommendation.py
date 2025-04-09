import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import crop_recommendation

def show():
    st.header("Crop Recommendation System")
    
    st.markdown("""
    Our crop recommendation system helps you choose the best crops to plant based on your soil conditions, 
    local climate, and market opportunities. Input your farm parameters below to get personalized recommendations.
    """)
    
    # Input form for crop recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Soil Parameters")
        soil_type = st.selectbox("Soil Type", ["Clay", "Sandy", "Loam", "Silt", "Clay Loam", "Sandy Loam"])
        soil_ph = st.slider("Soil pH", min_value=4.0, max_value=9.0, value=6.5, step=0.1)
        nitrogen = st.slider("Nitrogen Content (mg/kg)", min_value=0, max_value=150, value=50)
        phosphorus = st.slider("Phosphorus Content (mg/kg)", min_value=0, max_value=150, value=40)
        potassium = st.slider("Potassium Content (mg/kg)", min_value=0, max_value=200, value=50)
        organic_matter = st.slider("Organic Matter (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
    
    with col2:
        st.subheader("Climate & Farm Conditions")
        annual_rainfall = st.slider("Annual Rainfall (mm)", min_value=500, max_value=3000, value=1200)
        temperature = st.slider("Average Temperature (°C)", min_value=15, max_value=40, value=25)
        farm_size = st.number_input("Farm Size (hectares)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
        irrigation = st.selectbox("Irrigation Availability", ["None", "Limited", "Adequate", "Abundant"])
        market_access = st.selectbox("Market Access", ["Poor", "Fair", "Good", "Excellent"])
        region = st.text_input("Your Region", "")
    
    # Get recommendations button
    if st.button("Get Crop Recommendations"):
        with st.spinner("Analyzing farm conditions and generating recommendations..."):
            # Collect input parameters
            params = {
                "soil_type": soil_type,
                "soil_ph": soil_ph,
                "nitrogen": nitrogen,
                "phosphorus": phosphorus,
                "potassium": potassium,
                "organic_matter": organic_matter,
                "annual_rainfall": annual_rainfall,
                "temperature": temperature,
                "farm_size": farm_size,
                "irrigation": irrigation,
                "market_access": market_access,
                "region": region
            }
            
            try:
                # Get recommendations from the model
                recommendations = crop_recommendation.get_crop_recommendations(params)
                
                if recommendations and len(recommendations) > 0:
                    st.success("Recommendations generated successfully!")
                    
                    # Display recommendations
                    st.subheader("Recommended Crops for Your Farm")
                    
                    # Convert recommendations to DataFrame
                    recommendations_df = pd.DataFrame(recommendations)
                    
                    # Create bar chart for suitability scores
                    fig = px.bar(
                        recommendations_df,
                        x='crop',
                        y='suitability',
                        color='suitability',
                        labels={'suitability': 'Suitability Score', 'crop': 'Crop'},
                        range_color=[0, 100],
                        color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
                        title='Crop Suitability Scores'
                    )
                    
                    fig.update_layout(xaxis_tickangle=-45, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display detailed recommendations
                    for i, crop in enumerate(recommendations):
                        with st.expander(f"{i+1}. {crop['crop']} - Suitability Score: {crop['suitability']}/100"):
                            st.markdown(f"### {crop['crop']}")
                            
                            # Display crop details
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### Key Information")
                                st.markdown(f"**Growing Season:** {crop['growing_season']}")
                                st.markdown(f"**Time to Harvest:** {crop['time_to_harvest']}")
                                st.markdown(f"**Water Requirements:** {crop['water_requirements']}")
                                st.markdown(f"**Fertilizer Needs:** {crop['fertilizer_needs']}")
                            
                            with col2:
                                st.markdown("#### Economic Factors")
                                st.markdown(f"**Market Demand:** {crop['market_demand']}")
                                st.markdown(f"**Estimated Yield:** {crop['estimated_yield']}")
                                st.markdown(f"**Price Trend:** {crop['price_trend']}")
                                st.markdown(f"**Investment Level:** {crop['investment_level']}")
                            
                            st.markdown("#### Why This Crop")
                            st.markdown(crop['rationale'])
                            
                            st.markdown("#### Cultivation Tips")
                            st.markdown(crop['cultivation_tips'])
                            
                            # Display any risks or challenges
                            if 'risks' in crop and crop['risks']:
                                st.markdown("#### Potential Risks")
                                st.markdown(crop['risks'])
                
                else:
                    st.warning("No suitable crop recommendations were found. Please adjust your parameters.")
            
            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")
                st.info("Please check your inputs and try again.")
    
    # Crop rotation suggestions
    st.markdown("---")
    st.subheader("Crop Rotation Planner")
    
    st.markdown("""
    Crop rotation helps maintain soil health, prevent pest buildup, and optimize nutrient use.
    Select your current crops to get rotation suggestions for the next season.
    """)
    
    # Current crop selection
    current_crops = st.multiselect(
        "Select your current crops",
        ["Maize", "Beans", "Tomatoes", "Peppers", "Onions", "Cabbage", "Cassava", "Sweet Potatoes", "Groundnuts", "Sorghum", "Rice"]
    )
    
    if current_crops and len(current_crops) > 0:
        if st.button("Get Rotation Suggestions"):
            with st.spinner("Generating crop rotation plan..."):
                try:
                    # Get rotation suggestions
                    rotation_plan = crop_recommendation.get_rotation_suggestions(current_crops)
                    
                    if rotation_plan and len(rotation_plan) > 0:
                        st.success("Rotation plan generated!")
                        
                        # Display rotation plan
                        st.markdown("### Suggested Crop Rotation Plan")
                        
                        # Convert rotation plan to DataFrame
                        rotation_df = pd.DataFrame(rotation_plan)
                        st.dataframe(rotation_df, use_container_width=True)
                        
                        # Display rotation benefits
                        st.markdown("### Benefits of This Rotation")
                        
                        benefits = crop_recommendation.get_rotation_benefits(current_crops, rotation_plan)
                        
                        for benefit in benefits:
                            st.markdown(f"- {benefit}")
                    
                    else:
                        st.warning("No suitable rotation suggestions found. Please select different current crops.")
                
                except Exception as e:
                    st.error(f"Error generating rotation plan: {str(e)}")
    
    # Seasonal crop calendar
    st.markdown("---")
    st.subheader("Seasonal Crop Calendar")
    
    st.markdown("The calendar below shows the optimal planting and harvesting times for various crops in your region.")
    
    # Create example seasonal calendar data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    calendar_data = {
        'Crop': ['Maize', 'Beans', 'Tomatoes', 'Peppers', 'Cassava', 'Sweet Potatoes'],
        'Planting': ['Mar-Apr', 'Apr-May', 'Feb-Mar', 'Mar-Apr', 'Apr-May', 'Mar-Apr'],
        'Harvesting': ['Jul-Aug', 'Jul-Aug', 'May-Jun', 'Jun-Jul', 'Nov-Dec', 'Jul-Aug']
    }
    
    # Create a planting calendar visualization
    planting_cells = []
    harvesting_cells = []
    
    for crop in calendar_data['Crop']:
        planting_period = next((p for c, p in zip(calendar_data['Crop'], calendar_data['Planting']) if c == crop), '')
        harvesting_period = next((h for c, h in zip(calendar_data['Crop'], calendar_data['Harvesting']) if c == crop), '')
        
        planting_months = []
        harvesting_months = []
        
        if '-' in planting_period:
            start, end = planting_period.split('-')
            start_idx = months.index(start)
            end_idx = months.index(end)
            
            if start_idx <= end_idx:
                planting_months = months[start_idx:end_idx+1]
            else:
                planting_months = months[start_idx:] + months[:end_idx+1]
        
        if '-' in harvesting_period:
            start, end = harvesting_period.split('-')
            start_idx = months.index(start)
            end_idx = months.index(end)
            
            if start_idx <= end_idx:
                harvesting_months = months[start_idx:end_idx+1]
            else:
                harvesting_months = months[start_idx:] + months[:end_idx+1]
        
        planting_row = [1 if m in planting_months else 0 for m in months]
        harvesting_row = [1 if m in harvesting_months else 0 for m in months]
        
        planting_cells.append(planting_row)
        harvesting_cells.append(harvesting_row)
    
    # Create heatmap for planting
    planting_df = pd.DataFrame(planting_cells, columns=months, index=calendar_data['Crop'])
    
    fig = px.imshow(
        planting_df,
        labels=dict(x="Month", y="Crop", color="Activity"),
        x=months,
        y=calendar_data['Crop'],
        color_continuous_scale=["white", "green"],
        title="Planting Calendar",
        aspect="auto"
    )
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Create heatmap for harvesting
    harvesting_df = pd.DataFrame(harvesting_cells, columns=months, index=calendar_data['Crop'])
    
    fig = px.imshow(
        harvesting_df,
        labels=dict(x="Month", y="Crop", color="Activity"),
        x=months,
        y=calendar_data['Crop'],
        color_continuous_scale=["white", "orange"],
        title="Harvesting Calendar",
        aspect="auto"
    )
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend for the calendars
    st.markdown("""
    **Legend:**
    - **Green cells**: Optimal planting time
    - **Orange cells**: Optimal harvesting time
    
    These planting and harvesting times are based on general guidelines for your region's climate. 
    Actual timing may vary based on specific local conditions and weather patterns.
    """)
