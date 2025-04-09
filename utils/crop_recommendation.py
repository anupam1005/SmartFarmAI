import random
import logging
import math
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crop database with growing requirements and characteristics
# This is a simplified database for demonstration - in a real app, this would come from a more robust source
CROP_DATABASE = {
    "Corn": {
        "soil_types": ["Loam", "Sandy Loam", "Clay Loam"],
        "ph_range": [5.8, 7.0],
        "temperature_range": [20, 32],
        "rainfall_range": [500, 800],  # mm per growing season
        "growing_days": [80, 120],
        "nitrogen_need": "High",
        "phosphorus_need": "Medium",
        "potassium_need": "Medium",
        "water_need": "Medium",
        "investment_level": "Medium",
        "difficulty": "Low",
        "yield_potential": "High",
        "market_demand": "High",
        "price_volatility": "Medium",
        "cultivation_tips": "Plant when soil temperatures reach 16°C. Space rows 75-90cm apart and keep soil consistently moist during tasseling.",
        "common_issues": "Susceptible to corn borer, rootworm, and fungal diseases in wet conditions."
    },
    "Wheat": {
        "soil_types": ["Loam", "Clay Loam", "Silt Loam"],
        "ph_range": [6.0, 7.5],
        "temperature_range": [15, 24],
        "rainfall_range": [375, 875],
        "growing_days": [100, 130],
        "nitrogen_need": "Medium",
        "phosphorus_need": "Medium",
        "potassium_need": "Low",
        "water_need": "Low",
        "investment_level": "Low",
        "difficulty": "Low",
        "yield_potential": "Medium",
        "market_demand": "High",
        "price_volatility": "Medium",
        "cultivation_tips": "Plant at a depth of 3-5cm. Optimal seeding rate depends on variety and conditions, typically 150-210 kg/ha.",
        "common_issues": "Susceptible to rust, powdery mildew, and Fusarium head blight. Watch for aphids and wheat stem sawfly."
    },
    "Soybeans": {
        "soil_types": ["Loam", "Clay Loam", "Silt Loam"],
        "ph_range": [6.0, 7.0],
        "temperature_range": [20, 30],
        "rainfall_range": [450, 700],
        "growing_days": [90, 120],
        "nitrogen_need": "Low",  # Fixes its own nitrogen
        "phosphorus_need": "Medium",
        "potassium_need": "High",
        "water_need": "Medium",
        "investment_level": "Medium",
        "difficulty": "Low",
        "yield_potential": "Medium",
        "market_demand": "High",
        "price_volatility": "Medium",
        "cultivation_tips": "Plant after all danger of frost. Inoculate seeds with rhizobium bacteria if soybeans haven't been grown in the field recently.",
        "common_issues": "Susceptible to soybean cyst nematode, sudden death syndrome, and various fungal diseases."
    },
    "Rice": {
        "soil_types": ["Clay", "Clay Loam", "Silty Clay"],
        "ph_range": [5.5, 6.5],
        "temperature_range": [20, 35],
        "rainfall_range": [1000, 2000],
        "growing_days": [110, 150],
        "nitrogen_need": "High",
        "phosphorus_need": "Medium",
        "potassium_need": "Medium",
        "water_need": "Very High",
        "investment_level": "High",
        "difficulty": "High",
        "yield_potential": "High",
        "market_demand": "High",
        "price_volatility": "Low",
        "cultivation_tips": "Maintain consistent water levels, especially during early growth stages. Flood fields to 5-10cm depth.",
        "common_issues": "Prone to rice blast, bacterial leaf blight, and stem borers. Requires careful water management."
    },
    "Potatoes": {
        "soil_types": ["Sandy Loam", "Loam", "Silt Loam"],
        "ph_range": [5.0, 6.5],
        "temperature_range": [15, 20],
        "rainfall_range": [500, 700],
        "growing_days": [70, 120],
        "nitrogen_need": "Medium",
        "phosphorus_need": "High",
        "potassium_need": "High",
        "water_need": "Medium",
        "investment_level": "Medium",
        "difficulty": "Medium",
        "yield_potential": "High",
        "market_demand": "High",
        "price_volatility": "Medium",
        "cultivation_tips": "Plant seed potatoes 10-15cm deep and 30cm apart. Hill soil around plants as they grow to prevent greening of tubers.",
        "common_issues": "Susceptible to late blight, early blight, and Colorado potato beetle. Requires consistent moisture."
    },
    "Tomatoes": {
        "soil_types": ["Sandy Loam", "Loam", "Clay Loam"],
        "ph_range": [6.0, 6.8],
        "temperature_range": [20, 30],
        "rainfall_range": [400, 600],
        "growing_days": [60, 100],
        "nitrogen_need": "Medium",
        "phosphorus_need": "High",
        "potassium_need": "High",
        "water_need": "Medium",
        "investment_level": "High",
        "difficulty": "Medium",
        "yield_potential": "High",
        "market_demand": "High",
        "price_volatility": "High",
        "cultivation_tips": "Stake or cage plants for support. Prune suckers for indeterminate varieties. Maintain consistent soil moisture.",
        "common_issues": "Susceptible to blight, blossom end rot (calcium deficiency), and various insect pests."
    },
    "Cotton": {
        "soil_types": ["Loam", "Sandy Loam", "Clay Loam"],
        "ph_range": [5.8, 8.0],
        "temperature_range": [20, 35],
        "rainfall_range": [500, 1500],
        "growing_days": [150, 180],
        "nitrogen_need": "High",
        "phosphorus_need": "Medium",
        "potassium_need": "Medium",
        "water_need": "Medium",
        "investment_level": "High",
        "difficulty": "High",
        "yield_potential": "Medium",
        "market_demand": "Medium",
        "price_volatility": "High",
        "cultivation_tips": "Plant when soil temperatures reach at least 18°C. Space rows 75-100cm apart. Maintain adequate moisture until boll formation.",
        "common_issues": "Susceptible to boll weevil, bollworm, and various fungal diseases. Requires careful pest management."
    },
    "Sunflower": {
        "soil_types": ["Loam", "Sandy Loam", "Clay Loam"],
        "ph_range": [6.0, 7.5],
        "temperature_range": [18, 35],
        "rainfall_range": [400, 750],
        "growing_days": [80, 120],
        "nitrogen_need": "Medium",
        "phosphorus_need": "Low",
        "potassium_need": "Medium",
        "water_need": "Low",
        "investment_level": "Low",
        "difficulty": "Low",
        "yield_potential": "Medium",
        "market_demand": "Medium",
        "price_volatility": "Medium",
        "cultivation_tips": "Plant when soil temperature reaches 10°C. Space plants 30-45cm apart in rows 75-90cm apart. Drought tolerant once established.",
        "common_issues": "Susceptible to sunflower rust, downy mildew, and stem weevils. Birds can damage mature seed heads."
    },
    "Barley": {
        "soil_types": ["Loam", "Clay Loam", "Sandy Loam"],
        "ph_range": [6.0, 8.0],
        "temperature_range": [15, 30],
        "rainfall_range": [450, 650],
        "growing_days": [60, 100],
        "nitrogen_need": "Medium",
        "phosphorus_need": "Low",
        "potassium_need": "Low",
        "water_need": "Low",
        "investment_level": "Low",
        "difficulty": "Low",
        "yield_potential": "Medium",
        "market_demand": "Medium",
        "price_volatility": "Low",
        "cultivation_tips": "Plant early in the season. Barley is more salt-tolerant than other small grains and can thrive in various soil conditions.",
        "common_issues": "Susceptible to powdery mildew, leaf rust, and barley yellow dwarf virus. Watch for aphids which transmit viral diseases."
    },
    "Carrots": {
        "soil_types": ["Sandy Loam", "Loam", "Silt Loam"],
        "ph_range": [6.0, 7.0],
        "temperature_range": [16, 21],
        "rainfall_range": [400, 500],
        "growing_days": [70, 120],
        "nitrogen_need": "Low",
        "phosphorus_need": "Medium",
        "potassium_need": "High",
        "water_need": "Medium",
        "investment_level": "Medium",
        "difficulty": "Medium",
        "yield_potential": "High",
        "market_demand": "High",
        "price_volatility": "Medium",
        "cultivation_tips": "Sow seeds in fine, loose soil free of stones. Thin seedlings to 5-7cm apart. Keep soil consistently moist.",
        "common_issues": "Susceptible to carrot fly, cavity spot, and various fungal diseases. Requires well-drained soil to prevent forking."
    },
    "Onions": {
        "soil_types": ["Sandy Loam", "Loam", "Muck"],
        "ph_range": [6.0, 7.0],
        "temperature_range": [13, 24],
        "rainfall_range": [350, 550],
        "growing_days": [90, 150],
        "nitrogen_need": "Medium",
        "phosphorus_need": "Medium",
        "potassium_need": "Medium",
        "water_need": "Medium",
        "investment_level": "Medium",
        "difficulty": "Medium",
        "yield_potential": "High",
        "market_demand": "High",
        "price_volatility": "High",
        "cultivation_tips": "Plant sets or seedlings in early spring. Space plants 10-15cm apart. Stop watering when tops begin to fall over to promote curing.",
        "common_issues": "Susceptible to onion white rot, downy mildew, and thrips. Requires consistent moisture until bulb formation."
    },
    "Strawberries": {
        "soil_types": ["Sandy Loam", "Loam"],
        "ph_range": [5.5, 6.5],
        "temperature_range": [15, 26],
        "rainfall_range": [500, 700],
        "growing_days": [90, 150],
        "nitrogen_need": "Medium",
        "phosphorus_need": "Medium",
        "potassium_need": "High",
        "water_need": "High",
        "investment_level": "High",
        "difficulty": "High",
        "yield_potential": "High",
        "market_demand": "High",
        "price_volatility": "High",
        "cultivation_tips": "Plant crowns with roots spread out and growing point at soil level. Space plants 30-45cm apart. Mulch to prevent fruit contact with soil.",
        "common_issues": "Susceptible to gray mold, powdery mildew, and various insect pests. Birds and rodents can damage fruit."
    }
}

def get_crop_recommendations(input_data):
    """
    Generate crop recommendations based on input data
    
    Args:
        input_data: Dictionary of farm and field data
        
    Returns:
        List of recommendation dictionaries
    """
    try:
        # Extract input parameters
        soil_type = input_data.get('soil_type', 'Unknown')
        rainfall = input_data.get('rainfall', 150)  # mm/month
        temperature = input_data.get('temperature', 22)  # °C
        nitrogen_status = input_data.get('nitrogen_status', 'Medium')
        phosphorus_status = input_data.get('phosphorus_status', 'Medium')
        potassium_status = input_data.get('potassium_status', 'Medium')
        investment_level = input_data.get('investment_level', 'Medium')
        prioritize = input_data.get('priority', 'Profit')
        time_horizon = input_data.get('time_horizon', 'Medium (5-8 months)')
        market_access = input_data.get('market_access', 'Good')
        current_crop = input_data.get('current_crop')
        
        # Calculate growing season based on current date
        current_month = datetime.now().month
        if 3 <= current_month <= 5:
            growing_season = "Spring/Summer"
        elif 6 <= current_month <= 8:
            growing_season = "Summer/Fall"
        elif 9 <= current_month <= 11:
            growing_season = "Fall/Winter"
        else:
            growing_season = "Winter/Spring"
        
        # Convert time horizon to days
        if time_horizon.startswith("Short"):
            max_growing_days = 120
        elif time_horizon.startswith("Medium"):
            max_growing_days = 240
        else:
            max_growing_days = 365
        
        # Calculate annual rainfall from monthly
        annual_rainfall = rainfall * 12
        
        # Filter crops by basic compatibility
        compatible_crops = []
        
        for crop_name, crop_data in CROP_DATABASE.items():
            # Skip current crop for rotation
            if crop_name == current_crop:
                continue
                
            # Check soil compatibility
            soil_compatible = soil_type in crop_data["soil_types"] or soil_type == "Unknown"
            
            # Check temperature compatibility
            temp_min, temp_max = crop_data["temperature_range"]
            temp_compatible = temp_min <= temperature <= temp_max
            
            # Check rainfall compatibility (convert to annual)
            rain_min, rain_max = crop_data["rainfall_range"]
            rain_compatible = rain_min <= annual_rainfall <= rain_max
            
            # Check growing season compatibility
            growing_days_min, growing_days_max = crop_data["growing_days"]
            season_compatible = growing_days_max <= max_growing_days
            
            # Check investment level compatibility
            if investment_level == "Low":
                investment_compatible = crop_data["investment_level"] in ["Low", "Medium"]
            elif investment_level == "Medium":
                investment_compatible = crop_data["investment_level"] in ["Low", "Medium", "High"]
            else:
                investment_compatible = True
                
            # Combined compatibility
            # Allow some flexibility - require soil, investment, and season match, but be flexible on climate
            if soil_compatible and investment_compatible and season_compatible:
                # Calculate overall suitability score (0-100)
                suitability = calculate_crop_suitability(
                    crop_data, 
                    soil_type,
                    temperature,
                    annual_rainfall,
                    nitrogen_status,
                    phosphorus_status,
                    potassium_status,
                    growing_season,
                    investment_level,
                    prioritize,
                    market_access
                )
                
                if suitability >= 30:  # Minimum threshold for recommendation
                    compatible_crops.append({
                        "crop": crop_name,
                        "suitability": suitability,
                        "data": crop_data
                    })
        
        # Sort by suitability
        compatible_crops.sort(key=lambda x: x["suitability"], reverse=True)
        
        # Take top 3 recommendations
        top_recommendations = compatible_crops[:3]
        
        # Format recommendations
        recommendations = []
        
        for rec in top_recommendations:
            crop_name = rec["crop"]
            crop_data = rec["data"]
            suitability = rec["suitability"]
            
            # Format growing season
            if growing_season == "Spring/Summer":
                formatted_season = "Spring through Summer"
            elif growing_season == "Summer/Fall":
                formatted_season = "Summer through Fall"
            elif growing_season == "Fall/Winter":
                formatted_season = "Fall through Winter"
            else:
                formatted_season = "Winter through Spring"
                
            # Format water requirements
            water_need = crop_data["water_need"]
            if water_need == "Very High":
                water_req = "Very High (irrigation required)"
            elif water_need == "High":
                water_req = "High (regular irrigation needed)"
            elif water_need == "Medium":
                water_req = "Medium (occasional irrigation)"
            else:
                water_req = "Low (minimal irrigation needed)"
                
            # Format fertilizer needs based on crop requirements and soil status
            fertilizer_needs = []
            if crop_data["nitrogen_need"] == "High" and nitrogen_status != "Good":
                fertilizer_needs.append("high nitrogen")
            if crop_data["phosphorus_need"] == "High" and phosphorus_status != "Good":
                fertilizer_needs.append("high phosphorus")
            if crop_data["potassium_need"] == "High" and potassium_status != "Good":
                fertilizer_needs.append("high potassium")
                
            if fertilizer_needs:
                fert_req = f"Requires {', '.join(fertilizer_needs)}"
            else:
                fert_req = "Standard NPK fertilization"
                
            # Get market information
            market_info = get_crop_demand(crop_name, market_access)
            price_trend = get_crop_price_trend(crop_name)
            
            # Generate harvest time estimate
            growing_days_min, growing_days_max = crop_data["growing_days"]
            avg_days = (growing_days_min + growing_days_max) // 2
            
            # Calculate harvest date
            plant_date = datetime.now()
            harvest_date = plant_date + timedelta(days=avg_days)
            time_to_harvest = f"{avg_days} days ({harvest_date.strftime('%B %Y')})"
            
            # Generate estimated yield
            area_size = input_data.get('area_size', 1)  # hectares
            yield_potential = crop_data["yield_potential"]
            
            if yield_potential == "High":
                yield_factor = random.uniform(0.8, 1.2)
            elif yield_potential == "Medium":
                yield_factor = random.uniform(0.6, 0.9)
            else:
                yield_factor = random.uniform(0.4, 0.7)
                
            # Estimate yield based on crop type
            if crop_name in ["Corn", "Wheat", "Rice", "Barley"]:
                base_yield = 5  # tons per hectare
                unit = "tons"
            elif crop_name in ["Soybeans", "Sunflower"]:
                base_yield = 3  # tons per hectare
                unit = "tons"
            elif crop_name in ["Potatoes", "Onions", "Carrots"]:
                base_yield = 25  # tons per hectare
                unit = "tons"
            elif crop_name == "Cotton":
                base_yield = 1.2  # tons per hectare
                unit = "tons"
            elif crop_name == "Tomatoes":
                base_yield = 40  # tons per hectare
                unit = "tons"
            elif crop_name == "Strawberries":
                base_yield = 15  # tons per hectare
                unit = "tons"
            else:
                base_yield = 4  # tons per hectare
                unit = "tons"
                
            estimated_yield = f"{base_yield * yield_factor:.1f} {unit}/hectare"
            if area_size > 0:
                total_yield = base_yield * yield_factor * area_size
                estimated_yield += f" (total: {total_yield:.1f} {unit})"
            
            # Generate rationale
            rationale = generate_recommendation_rationale(
                crop_name, 
                suitability, 
                soil_type, 
                growing_season, 
                prioritize,
                nitrogen_status,
                phosphorus_status,
                potassium_status
            )
            
            # Format recommendation
            recommendation = {
                "crop": crop_name,
                "suitability": suitability,
                "growing_season": formatted_season,
                "time_to_harvest": time_to_harvest,
                "water_requirements": water_req,
                "fertilizer_needs": fert_req,
                "market_demand": market_info,
                "estimated_yield": estimated_yield,
                "price_trend": price_trend,
                "investment_level": crop_data["investment_level"],
                "rationale": rationale,
                "cultivation_tips": crop_data["cultivation_tips"],
                "risks": crop_data["common_issues"]
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    except Exception as e:
        logger.error(f"Error generating crop recommendations: {e}")
        return []

def calculate_crop_suitability(crop_data, soil_type, temperature, annual_rainfall, 
                            nitrogen_status, phosphorus_status, potassium_status,
                            growing_season, investment_level, priority, market_access):
    """
    Calculate crop suitability score based on input parameters
    
    Args:
        crop_data: Crop data dictionary
        soil_type, temperature, etc.: Environmental and management parameters
        
    Returns:
        Suitability score (0-100)
    """
    # Initialize suitability score
    score = 60  # Start at 60 to allow both positive and negative adjustments
    
    # Soil type compatibility
    if soil_type in crop_data["soil_types"]:
        score += 10
    elif soil_type == "Unknown":
        pass  # No adjustment
    else:
        score -= 15
    
    # Temperature compatibility
    temp_min, temp_max = crop_data["temperature_range"]
    temp_mid = (temp_min + temp_max) / 2
    
    if temp_min <= temperature <= temp_max:
        # Optimal is in the middle of the range
        temp_distance = abs(temperature - temp_mid) / ((temp_max - temp_min) / 2)
        score += 10 * (1 - temp_distance * 0.5)  # Full points at exact middle, decreasing toward edges
    else:
        # Outside optimal range
        distance = min(abs(temperature - temp_min), abs(temperature - temp_max))
        score -= min(15, distance * 3)  # Penalty increases with distance from range
    
    # Rainfall compatibility
    rain_min, rain_max = crop_data["rainfall_range"]
    if rain_min <= annual_rainfall <= rain_max:
        score += 10
    else:
        # Check if irrigation can compensate
        if annual_rainfall < rain_min and crop_data["water_need"] in ["Medium", "High", "Very High"]:
            score -= 5  # Some penalty, but not as much since irrigation can help
        else:
            score -= 10
    
    # Nutrient requirements vs. soil status
    if crop_data["nitrogen_need"] == "High":
        if nitrogen_status == "Good":
            score += 5
        elif nitrogen_status == "Low":
            score -= 8
    
    if crop_data["phosphorus_need"] == "High":
        if phosphorus_status == "Good":
            score += 5
        elif phosphorus_status == "Low":
            score -= 8
            
    if crop_data["potassium_need"] == "High":
        if potassium_status == "Good":
            score += 5
        elif potassium_status == "Low":
            score -= 8
    
    # Investment level match
    investment_map = {"Low": 0, "Medium": 1, "High": 2}
    investment_diff = investment_map[crop_data["investment_level"]] - investment_map[investment_level]
    
    if investment_diff <= 0:  # Crop requires less or equal investment
        score += 5
    else:  # Crop requires more investment than desired
        score -= 10
    
    # Market access and demand adjustment
    demand_level = crop_data["market_demand"]
    market_access_map = {"Poor": 0, "Moderate": 1, "Good": 2, "Excellent": 3}
    
    if demand_level == "High":
        score += market_access_map[market_access] * 2  # More benefit for in-demand crops
    elif demand_level == "Medium":
        score += market_access_map[market_access]
    
    # Priority adjustments
    if priority == "Profit":
        # Favor high yield and high demand
        if crop_data["yield_potential"] == "High" and crop_data["market_demand"] == "High":
            score += 15
        elif crop_data["yield_potential"] == "High" or crop_data["market_demand"] == "High":
            score += 8
            
    elif priority == "Sustainability":
        # Favor low water and nutrient needs
        if crop_data["water_need"] == "Low":
            score += 10
        if crop_data["nitrogen_need"] == "Low":
            score += 5
            
    elif priority == "Risk Minimization":
        # Favor stable prices and lower difficulty
        if crop_data["price_volatility"] == "Low":
            score += 8
        if crop_data["difficulty"] == "Low":
            score += 7
            
    elif priority == "Water Efficiency":
        # Strongly favor low water needs
        if crop_data["water_need"] == "Low":
            score += 15
        elif crop_data["water_need"] == "Medium":
            score += 5
        else:
            score -= 10
    
    # Cap score between 0 and 100
    return max(0, min(100, score))

def generate_recommendation_rationale(crop_name, suitability, soil_type, growing_season, 
                                     priority, nitrogen_status, phosphorus_status, potassium_status):
    """
    Generate human-readable rationale for a crop recommendation
    
    Args:
        Various crop and farm parameters
        
    Returns:
        Rationale text
    """
    crop_data = CROP_DATABASE[crop_name]
    
    # Start with suitability assessment
    if suitability >= 80:
        intro = f"{crop_name} is an excellent match for your farm conditions"
    elif suitability >= 60:
        intro = f"{crop_name} is a good match for your farm conditions"
    else:
        intro = f"{crop_name} is a potential match for your farm conditions"
    
    # Add soil compatibility
    if soil_type in crop_data["soil_types"]:
        soil_text = f"Your {soil_type.lower()} soil is ideal for growing {crop_name.lower()}"
    elif soil_type == "Unknown":
        soil_text = f"{crop_name} grows best in {', '.join(crop_data['soil_types']).lower()} soils"
    else:
        soil_text = f"While {crop_name.lower()} prefers {', '.join(crop_data['soil_types']).lower()} soils, it can adapt to your conditions with proper management"
    
    # Add nutrient considerations
    nutrient_factors = []
    
    if crop_data["nitrogen_need"] == "High" and nitrogen_status != "Good":
        nutrient_factors.append("additional nitrogen fertilization")
    if crop_data["phosphorus_need"] == "High" and phosphorus_status != "Good":
        nutrient_factors.append("phosphorus supplementation")
    if crop_data["potassium_need"] == "High" and potassium_status != "Good":
        nutrient_factors.append("potassium application")
        
    if nutrient_factors:
        nutrient_text = f"For optimal yields, your soil would benefit from {' and '.join(nutrient_factors)}"
    else:
        nutrient_text = f"Your soil nutrient profile appears suitable for {crop_name.lower()} cultivation"
    
    # Add market and economic considerations
    market_demand = crop_data["market_demand"]
    price_volatility = crop_data["price_volatility"]
    
    if market_demand == "High" and price_volatility == "Low":
        market_text = f"{crop_name} currently enjoys high market demand with stable pricing"
    elif market_demand == "High":
        market_text = f"{crop_name} has strong market demand, though prices can fluctuate"
    elif price_volatility == "Low":
        market_text = f"While market demand varies, {crop_name} typically maintains relatively stable prices"
    else:
        market_text = f"{crop_name} provides diversification opportunities for your crop portfolio"
    
    # Add priority-specific text
    if priority == "Profit":
        if crop_data["yield_potential"] == "High" and crop_data["market_demand"] == "High":
            priority_text = f"With high yield potential and strong market demand, {crop_name.lower()} aligns well with your profit focus"
        else:
            priority_text = f"For your profit-focused strategy, {crop_name.lower()} offers a balance of yield potential and market opportunities"
    elif priority == "Sustainability":
        water_need = crop_data["water_need"]
        if water_need == "Low":
            priority_text = f"As a relatively water-efficient crop, {crop_name.lower()} supports your sustainability goals"
        else:
            priority_text = f"{crop_name} can be part of a sustainable rotation system in your farm plan"
    elif priority == "Risk Minimization":
        if crop_data["difficulty"] == "Low":
            priority_text = f"{crop_name} is generally easy to cultivate, supporting your risk management approach"
        else:
            priority_text = f"While {crop_name.lower()} requires careful management, its established growing practices help minimize risks"
    elif priority == "Water Efficiency":
        if crop_data["water_need"] == "Low":
            priority_text = f"{crop_name} has relatively low water requirements, making it suitable for water-conscious farming"
        else:
            priority_text = f"With proper water management practices, {crop_name.lower()} can be grown efficiently even with your water conservation focus"
    
    # Combine all elements
    rationale = f"{intro}. {soil_text}. {nutrient_text}. {market_text}. {priority_text}."
    
    return rationale

def get_crop_info(crop_name):
    """
    Get detailed information about a specific crop
    
    Args:
        crop_name: Name of the crop
        
    Returns:
        Crop data dictionary or None if not found
    """
    return CROP_DATABASE.get(crop_name)

def get_crop_price_trend(crop_name):
    """
    Get current price trend for a crop
    
    Args:
        crop_name: Name of the crop
        
    Returns:
        Price trend string
    """
    # In a real application, this would query a market API
    # Using simulated data for demonstration
    trends = {
        "Corn": "Stable",
        "Wheat": "Slight increase",
        "Soybeans": "Moderate increase",
        "Rice": "Stable",
        "Potatoes": "Stable",
        "Tomatoes": "Fluctuating",
        "Cotton": "Moderate decrease",
        "Sunflower": "Slight increase",
        "Barley": "Stable",
        "Carrots": "Stable",
        "Onions": "Moderate increase",
        "Strawberries": "Fluctuating"
    }
    
    return trends.get(crop_name, "Unknown")

def get_crop_demand(crop_name, market_access):
    """
    Get market demand assessment for a crop
    
    Args:
        crop_name: Name of the crop
        market_access: Level of market access
        
    Returns:
        Market demand assessment string
    """
    # Base demand from crop database
    base_demand = CROP_DATABASE.get(crop_name, {}).get("market_demand", "Medium")
    
    # Adjust based on market access
    if base_demand == "High":
        if market_access in ["Good", "Excellent"]:
            return "Strong"
        else:
            return "Moderate to Strong"
    elif base_demand == "Medium":
        if market_access == "Excellent":
            return "Moderate to Strong"
        elif market_access == "Poor":
            return "Limited"
        else:
            return "Moderate"
    else:  # Low demand
        if market_access == "Poor":
            return "Very Limited"
        else:
            return "Limited"