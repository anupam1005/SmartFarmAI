import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import resource_management

def show():
    st.header("Resource Management")
    
    # Create tabs for different resources
    water_tab, fertilizer_tab, planning_tab = st.tabs(["Water Management", "Fertilizer Tracking", "Planning & Optimization"])
    
    #----- Water Management Tab -----
    with water_tab:
        st.subheader("Water Usage Tracking")
        
        # Water resource input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input form for water usage
            with st.form("water_usage_form"):
                st.markdown("### Record Water Usage")
                
                # Form inputs
                date = st.date_input("Date", datetime.now())
                crop_type = st.selectbox("Crop", ["Maize", "Tomatoes", "Beans", "Cassava", "Sweet Potato"])
                water_amount = st.number_input("Water Amount (liters)", min_value=0.0, max_value=10000.0, step=10.0)
                water_source = st.selectbox("Water Source", ["Rainwater", "Irrigation", "Well", "River/Stream"])
                irrigation_method = st.selectbox("Irrigation Method", ["Drip", "Sprinkler", "Flood", "Manual"])
                
                # Submit button
                submit_water = st.form_submit_button("Record Usage")
                
                if submit_water:
                    # In production, this would save to a database
                    st.success(f"Recorded {water_amount} liters of water usage for {crop_type} on {date}")
                    
        with col2:
            # Display water efficiency metrics
            st.markdown("### Water Efficiency")
            
            # Example efficiency data - in production this would be calculated
            efficiency_scores = {
                'Maize': 78,
                'Tomatoes': 85,
                'Beans': 72,
                'Cassava': 90,
                'Sweet Potato': 81
            }
            
            # Create a gauge chart for overall water efficiency
            avg_efficiency = sum(efficiency_scores.values()) / len(efficiency_scores)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_efficiency,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Water Efficiency Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "blue"},
                    'steps': [
                        {'range': [0, 50], 'color': "red"},
                        {'range': [50, 75], 'color': "orange"},
                        {'range': [75, 100], 'color': "green"},
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': avg_efficiency
                    }
                }
            ))
            
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            # Water saving tips
            st.markdown("### Water Saving Tips")
            st.info(resource_management.get_water_saving_tips())
        
        # Water usage history
        st.subheader("Water Usage History")
        
        # Example data for water usage history - in production this would come from a database
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14, -1, -1)]
        water_usage = [120, 110, 135, 95, 80, 75, 130, 120, 145, 125, 105, 95, 85, 110, 100]
        rainfall = [0, 0, 15, 22, 5, 0, 0, 0, 0, 10, 25, 5, 0, 0, 0]
        
        water_df = pd.DataFrame({
            'Date': dates,
            'Water Usage (L)': water_usage,
            'Rainfall (mm)': rainfall
        })
        
        # Plot water usage and rainfall
        fig = px.bar(
            water_df,
            x='Date',
            y=['Water Usage (L)', 'Rainfall (mm)'],
            barmode='group',
            labels={'value': 'Amount', 'variable': 'Metric'},
            title='Water Usage vs Rainfall',
            color_discrete_map={'Water Usage (L)': 'blue', 'Rainfall (mm)': 'skyblue'}
        )
        
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Water alerts and recommendations
        with st.expander("Water Management Recommendations"):
            st.markdown("""
            - **Current Status**: Moderate water stress detected in Tomato crops
            - **Weather Forecast Impact**: Expected rainfall in the next 3 days may reduce irrigation needs
            - **Recommendation**: Reduce irrigation for Tomatoes by 20% for the next week
            - **Water Conservation**: Consider adding mulch around plants to reduce evaporation
            """)
    
    #----- Fertilizer Tracking Tab -----
    with fertilizer_tab:
        st.subheader("Fertilizer Management")
        
        # Fertilizer input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input form for fertilizer usage
            with st.form("fertilizer_usage_form"):
                st.markdown("### Record Fertilizer Application")
                
                # Form inputs
                date = st.date_input("Application Date", datetime.now(), key="fert_date")
                crop_type = st.selectbox("Crop", ["Maize", "Tomatoes", "Beans", "Cassava", "Sweet Potato"], key="fert_crop")
                fertilizer_type = st.selectbox("Fertilizer Type", ["NPK 17-17-17", "Urea", "DAP", "Organic Compost", "Manure"])
                amount = st.number_input("Amount (kg)", min_value=0.0, max_value=1000.0, step=1.0)
                application_method = st.selectbox("Application Method", ["Broadcast", "Side-dressing", "Foliar Spray", "Drip Fertigation"])
                
                # Submit button
                submit_fertilizer = st.form_submit_button("Record Application")
                
                if submit_fertilizer:
                    # In production, this would save to a database
                    st.success(f"Recorded {amount} kg of {fertilizer_type} application for {crop_type} on {date}")
        
        with col2:
            # Display fertilizer stocks
            st.markdown("### Fertilizer Stock Levels")
            
            # Example stock data - in production this would come from database
            fertilizer_stocks = {
                'NPK 17-17-17': 65,
                'Urea': 40,
                'DAP': 25,
                'Organic Compost': 90,
                'Manure': 70
            }
            
            # Create bar chart for fertilizer stocks
            stock_df = pd.DataFrame({
                'Fertilizer': list(fertilizer_stocks.keys()),
                'Stock (%)': list(fertilizer_stocks.values())
            })
            
            fig = px.bar(
                stock_df,
                x='Fertilizer',
                y='Stock (%)',
                color='Stock (%)',
                color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
                range_color=[0, 100],
                text='Stock (%)'
            )
            
            fig.update_layout(height=300, xaxis_tickangle=-45)
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        # Fertilizer application history
        st.subheader("Fertilizer Application History")
        
        # Example data for fertilizer history - in production this would come from a database
        fert_history = {
            'Date': ['2023-10-15', '2023-10-05', '2023-09-25', '2023-09-10', '2023-08-28'],
            'Crop': ['Maize', 'Tomatoes', 'Beans', 'Maize', 'Tomatoes'],
            'Fertilizer Type': ['NPK 17-17-17', 'Organic Compost', 'DAP', 'Urea', 'NPK 17-17-17'],
            'Amount (kg)': [25, 40, 15, 20, 30],
            'Application Method': ['Broadcast', 'Side-dressing', 'Broadcast', 'Foliar Spray', 'Broadcast']
        }
        
        fert_df = pd.DataFrame(fert_history)
        st.dataframe(fert_df, use_container_width=True)
        
        # Fertilizer recommendations
        with st.expander("Fertilizer Recommendations"):
            st.markdown("""
            - **Current Soil Status**: Nitrogen deficiency detected in Maize crop areas
            - **Recommendation**: Apply 50kg/hectare of Urea within the next week
            - **Application Method**: Side-dressing would be most effective for current growth stage
            - **Remember**: Apply fertilizers in the early morning or late afternoon to reduce nutrient loss
            """)
            
        # Soil nutrient levels visualization
        st.subheader("Soil Nutrient Levels")
        
        # Example data for soil nutrients - in production this would come from soil tests
        nutrients = {
            'Nutrient': ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Calcium (Ca)', 'Magnesium (Mg)'],
            'Current Level': [45, 60, 70, 80, 55],
            'Optimal Level': [70, 65, 75, 85, 60]
        }
        
        nut_df = pd.DataFrame(nutrients)
        
        # Create comparative bar chart
        fig = px.bar(
            nut_df,
            x='Nutrient',
            y=['Current Level', 'Optimal Level'],
            barmode='group',
            color_discrete_map={'Current Level': 'orange', 'Optimal Level': 'green'},
            title='Current vs. Optimal Nutrient Levels'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    #----- Planning & Optimization Tab -----
    with planning_tab:
        st.subheader("Resource Planning & Optimization")
        
        # Resource efficiency metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Resource Efficiency Metrics")
            
            # Example efficiency metrics - in production these would be calculated
            metrics = {
                'Metric': ['Water Use Efficiency', 'Fertilizer Efficiency', 'Yield per Resource Unit', 'Resource Cost per Hectare'],
                'Score': [78, 65, 82, 70],
                'Trend': ['↑', '↑', '→', '↓'],
                'Industry Avg': [65, 60, 75, 75]
            }
            
            metrics_df = pd.DataFrame(metrics)
            st.dataframe(metrics_df, use_container_width=True)
        
        with col2:
            st.markdown("### Resource Optimization Potential")
            
            # Example optimization potential data
            optimization = {
                'Resource': ['Water', 'Fertilizer', 'Labor', 'Energy'],
                'Potential Savings': [25, 15, 10, 20]
            }
            
            opt_df = pd.DataFrame(optimization)
            
            fig = px.bar(
                opt_df,
                x='Resource',
                y='Potential Savings',
                color='Potential Savings',
                labels={'Potential Savings': 'Potential Savings (%)'},
                text='Potential Savings'
            )
            
            fig.update_traces(texttemplate='%{text}%', textposition='outside')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost analysis
        st.subheader("Resource Cost Analysis")
        
        # Example cost data - in production this would come from user inputs
        costs = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
            'Water': [120, 110, 100, 90, 110, 130, 150, 140, 120, 100],
            'Fertilizer': [80, 0, 150, 0, 90, 0, 160, 0, 100, 0],
            'Labor': [200, 180, 210, 190, 220, 200, 230, 210, 220, 190],
            'Other': [50, 40, 60, 45, 55, 50, 65, 55, 60, 50]
        }
        
        costs_df = pd.DataFrame(costs)
        costs_df['Total'] = costs_df['Water'] + costs_df['Fertilizer'] + costs_df['Labor'] + costs_df['Other']
        
        # Create stacked bar chart for costs
        fig = px.bar(
            costs_df,
            x='Month',
            y=['Water', 'Fertilizer', 'Labor', 'Other'],
            title='Monthly Resource Costs Breakdown',
            labels={'value': 'Cost', 'variable': 'Resource Type'},
            color_discrete_map={
                'Water': 'blue',
                'Fertilizer': 'green',
                'Labor': 'orange',
                'Other': 'gray'
            }
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Resource planning tool
        st.subheader("Resource Planning Tool")
        
        # Simple planning calculator
        with st.expander("Seasonal Resource Calculator"):
            st.markdown("Estimate resources needed for the upcoming season")
            
            col1, col2 = st.columns(2)
            
            with col1:
                crop = st.selectbox("Crop Type", ["Maize", "Tomatoes", "Beans", "Cassava", "Sweet Potato"], key="plan_crop")
                area = st.number_input("Area (hectares)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
                season = st.selectbox("Growing Season", ["Rainy Season", "Dry Season", "Short Rains", "Long Rains"])
            
            with col2:
                soil_type = st.selectbox("Soil Type", ["Clay", "Sandy", "Loam", "Silt", "Mixed"])
                irrigation = st.selectbox("Irrigation Type", ["None", "Drip", "Sprinkler", "Flood", "Manual"])
                target_yield = st.number_input("Target Yield (tons/ha)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)
            
            if st.button("Calculate Resource Needs"):
                # In production, this would run actual calculations based on models
                st.success("Resource Calculation Complete!")
                
                # Example calculation results
                results = {
                    'Resource': ['Water (liters)', 'NPK Fertilizer (kg)', 'Seeds (kg)', 'Labor (person-days)'],
                    'Estimated Amount': [45000, 250, 25, 45],
                    'Estimated Cost': ['$450', '$125', '$75', '$225']
                }
                
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
                
                st.info("These estimates are based on regional averages and may vary based on specific conditions.")
