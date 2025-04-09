import numpy as np
from datetime import datetime
import random

def get_crop_recommendations(location, soil_type, climate_data, land_size, 
                            budget_level, previous_crops=None):
    """
    Generate crop recommendations based on location and environmental factors.
    
    Args:
        location: Location string
        soil_type: Type of soil
        climate_data: Dictionary with climate data
        land_size: Size of land in hectares
        budget_level: Level of budget (Low, Medium, High)
        previous_crops: List of previously grown crops
        
    Returns:
        List of crop recommendations with details
    """
    # Define base crop database with characteristics
    crops_database = {
        "Maize": {
            "soil_types": ["Loam", "Sandy Loam", "Clay Loam"],
            "temperature_range": (18, 35),
            "rainfall_range": (500, 1500),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "90-120 days",
            "investment_level": "Medium",
            "water_requirements": "Medium",
            "fertilizer_needs": "Medium-High (N)",
            "market_demand": get_market_forecast("Maize"),
            "typical_yield": "5-10 tons/ha",
            "price_trend": get_price_trend("Maize"),
            "cultivation_tips": [
                "Plant when soil temperature reaches at least 16°C.",
                "Optimal plant spacing is 60-75 cm between rows and 20-25 cm between plants.",
                "Requires good nitrogen fertilization - apply in split doses.",
                "Control weeds during the first 6 weeks.",
                "Monitor for fall armyworm, a common pest in maize."
            ],
            "risks": [
                "Susceptible to drought during flowering stage.",
                "Vulnerable to corn borers and armyworms.",
                "Market prices can be volatile."
            ]
        },
        "Rice": {
            "soil_types": ["Clay", "Clay Loam", "Silty Clay"],
            "temperature_range": (20, 35),
            "rainfall_range": (1000, 2500),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "100-150 days",
            "investment_level": "Medium-High",
            "water_requirements": "High",
            "fertilizer_needs": "Medium (N, P, K)",
            "market_demand": get_market_forecast("Rice"),
            "typical_yield": "4-7 tons/ha",
            "price_trend": get_price_trend("Rice"),
            "cultivation_tips": [
                "Prepare land by puddling to retain water.",
                "Maintain 5-10 cm of standing water during most of the growing period.",
                "Apply fertilizer in split doses - at transplanting, tillering, and heading stages.",
                "Consider direct seeding in regions with labor shortages.",
                "Drain field 10-15 days before harvest."
            ],
            "risks": [
                "Requires abundant water supply.",
                "Susceptible to blast disease and stem borers.",
                "Labor intensive for transplanting and harvesting.",
                "Vulnerable to flooding events."
            ]
        },
        "Wheat": {
            "soil_types": ["Loam", "Clay Loam", "Silt Loam"],
            "temperature_range": (15, 30),
            "rainfall_range": (400, 1200),
            "growing_season": ["Winter", "Spring"],
            "days_to_harvest": "120-150 days",
            "investment_level": "Medium",
            "water_requirements": "Medium",
            "fertilizer_needs": "Medium (N, P)",
            "market_demand": get_market_forecast("Wheat"),
            "typical_yield": "3-6 tons/ha",
            "price_trend": get_price_trend("Wheat"),
            "cultivation_tips": [
                "Optimal sowing depth is 3-5 cm.",
                "Timing of nitrogen application is critical - apply at sowing, tillering, and flowering.",
                "Control weeds early in the growing season.",
                "Winter wheat varieties need a period of cold temperatures for proper development.",
                "Harvest when grain moisture content is below 14%."
            ],
            "risks": [
                "Susceptible to rust diseases.",
                "Frost risk for spring wheat.",
                "Drought during grain filling stage reduces yield significantly.",
                "Global market price fluctuations."
            ]
        },
        "Soybeans": {
            "soil_types": ["Loam", "Clay Loam", "Silt Loam"],
            "temperature_range": (20, 32),
            "rainfall_range": (500, 1500),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "90-120 days",
            "investment_level": "Medium",
            "water_requirements": "Medium",
            "fertilizer_needs": "Low (P, K)",
            "market_demand": get_market_forecast("Soybeans"),
            "typical_yield": "2-4 tons/ha",
            "price_trend": get_price_trend("Soybeans"),
            "cultivation_tips": [
                "Inoculate seeds with Rhizobium bacteria if planting in new fields.",
                "Optimal planting depth is 2.5-5 cm.",
                "Plant when soil temperature is at least 13°C.",
                "Rotate with corn or small grains.",
                "Avoid over-fertilization with nitrogen as soybeans fix their own."
            ],
            "risks": [
                "Susceptible to soybean cyst nematode and various fungal diseases.",
                "Sensitive to drought during flowering and pod filling.",
                "Vulnerable to deer and other wildlife damage.",
                "Global market competition affects prices."
            ]
        },
        "Tomatoes": {
            "soil_types": ["Sandy Loam", "Loam", "Clay Loam"],
            "temperature_range": (20, 35),
            "rainfall_range": (400, 1200),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "60-100 days",
            "investment_level": "High",
            "water_requirements": "Medium-High",
            "fertilizer_needs": "Medium (N, P, K, Ca)",
            "market_demand": get_market_forecast("Tomatoes"),
            "typical_yield": "25-80 tons/ha",
            "price_trend": get_price_trend("Tomatoes"),
            "cultivation_tips": [
                "Start seeds indoors 6-8 weeks before transplanting.",
                "Stake or cage determinate varieties; trellis indeterminate varieties.",
                "Consistent watering prevents blossom end rot.",
                "Prune suckers for indeterminate varieties to improve air circulation.",
                "Avoid overhead watering to prevent disease."
            ],
            "risks": [
                "Vulnerable to numerous diseases including early and late blight.",
                "Requires careful handling during harvest to prevent damage.",
                "Market prices fluctuate considerably with seasonal supply.",
                "Storage and transportation challenges for fresh market."
            ]
        },
        "Potatoes": {
            "soil_types": ["Sandy Loam", "Loam", "Silt Loam"],
            "temperature_range": (15, 25),
            "rainfall_range": (500, 1200),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "70-120 days",
            "investment_level": "Medium-High",
            "water_requirements": "Medium",
            "fertilizer_needs": "Medium-High (N, P, K)",
            "market_demand": get_market_forecast("Potatoes"),
            "typical_yield": "20-50 tons/ha",
            "price_trend": get_price_trend("Potatoes"),
            "cultivation_tips": [
                "Use certified seed potatoes to avoid diseases.",
                "Plant tubers 10-15 cm deep, 25-30 cm apart.",
                "Hill soil around plants as they grow to prevent greening.",
                "Maintain consistent soil moisture, especially during tuber formation.",
                "Stop watering when foliage begins to die back to allow skins to set."
            ],
            "risks": [
                "Susceptible to late blight, scab, and Colorado potato beetle.",
                "Vulnerable to frost damage.",
                "Storage requirements for long-term marketability.",
                "Quality issues affect market value significantly."
            ]
        },
        "Cotton": {
            "soil_types": ["Loam", "Sandy Loam", "Clay Loam"],
            "temperature_range": (20, 38),
            "rainfall_range": (500, 1500),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "150-180 days",
            "investment_level": "High",
            "water_requirements": "Medium-High",
            "fertilizer_needs": "High (N, P, K)",
            "market_demand": get_market_forecast("Cotton"),
            "typical_yield": "0.8-1.5 tons/ha (lint)",
            "price_trend": get_price_trend("Cotton"),
            "cultivation_tips": [
                "Plant when soil temperature exceeds 18°C.",
                "Good seedbed preparation is essential for uniform emergence.",
                "Apply nitrogen in split applications.",
                "Monitor and manage insect pests throughout the season.",
                "Use defoliants before harvest to facilitate mechanical picking."
            ],
            "risks": [
                "Labor intensive or requires specialized harvesting equipment.",
                "Susceptible to bollworms and boll weevils.",
                "Vulnerable to late season rains which can reduce fiber quality.",
                "Price volatility in global markets."
            ]
        },
        "Sunflower": {
            "soil_types": ["Loam", "Sandy Loam", "Clay Loam"],
            "temperature_range": (18, 35),
            "rainfall_range": (400, 1000),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "80-120 days",
            "investment_level": "Medium",
            "water_requirements": "Medium-Low",
            "fertilizer_needs": "Medium (N, P)",
            "market_demand": get_market_forecast("Sunflower"),
            "typical_yield": "1.5-3 tons/ha (seeds)",
            "price_trend": get_price_trend("Sunflower"),
            "cultivation_tips": [
                "Plant when soil temperature reaches 10°C at seeding depth.",
                "Optimal plant spacing is 60-75 cm between rows, 20-30 cm between plants.",
                "Sunflowers have deep roots and can access nutrients and moisture from lower soil profiles.",
                "Rotate with cereal crops to break disease cycles.",
                "Harvest when back of heads turn yellow to brown and seed moisture is below 15%."
            ],
            "risks": [
                "Attractive to birds which can significantly reduce yield.",
                "Susceptible to downy mildew and sclerotinia head rot.",
                "Requires pollinator presence for optimal seed set.",
                "Market susceptible to changes in vegetable oil demand."
            ]
        },
        "Beans": {
            "soil_types": ["Loam", "Sandy Loam", "Clay Loam"],
            "temperature_range": (18, 30),
            "rainfall_range": (400, 1200),
            "growing_season": ["Spring", "Summer"],
            "days_to_harvest": "60-90 days",
            "investment_level": "Medium-Low",
            "water_requirements": "Medium",
            "fertilizer_needs": "Low (P, K)",
            "market_demand": get_market_forecast("Beans"),
            "typical_yield": "1.5-3 tons/ha (dry beans)",
            "price_trend": get_price_trend("Beans"),
            "cultivation_tips": [
                "Inoculate seeds with Rhizobium bacteria for nitrogen fixation.",
                "Plant when soil has warmed to at least 16°C.",
                "Direct sow at 2-3 cm depth, 5-8 cm apart in rows 50-75 cm apart.",
                "Avoid overhead irrigation during flowering.",
                "Harvest when pods are dry but before they shatter."
            ],
            "risks": [
                "Susceptible to bean rust, bacterial blight, and anthracnose.",
                "Sensitive to waterlogging.",
                "Vulnerable to various bean beetles and aphids.",
                "Labor intensive for small-scale harvesting."
            ]
        },
        "Cassava": {
            "soil_types": ["Sandy Loam", "Loam", "Clay Loam"],
            "temperature_range": (20, 35),
            "rainfall_range": (500, 2000),
            "growing_season": ["Spring", "Year-round in tropics"],
            "days_to_harvest": "9-18 months",
            "investment_level": "Low",
            "water_requirements": "Medium-Low",
            "fertilizer_needs": "Low (K)",
            "market_demand": get_market_forecast("Cassava"),
            "typical_yield": "10-30 tons/ha (fresh roots)",
            "price_trend": get_price_trend("Cassava"),
            "cultivation_tips": [
                "Plant stem cuttings horizontally or at an angle in raised beds or ridges.",
                "Optimal cutting length is 20-30 cm with 5-8 nodes.",
                "Space plants 80-100 cm apart in rows 90-120 cm apart.",
                "Weed management is critical in the first 3 months.",
                "Harvest when roots reach desired size, typically after 9-12 months."
            ],
            "risks": [
                "Susceptible to cassava mosaic disease and bacterial blight.",
                "Roots deteriorate rapidly after harvest (1-3 days).",
                "Processing required to remove cyanogenic compounds in some varieties.",
                "Limited export market potential due to perishability."
            ]
        }
    }
    
    # Get current season
    current_month = datetime.now().month
    if 3 <= current_month <= 5:
        current_season = "Spring"
    elif 6 <= current_month <= 8:
        current_season = "Summer"
    elif 9 <= current_month <= 11:
        current_season = "Fall"
    else:
        current_season = "Winter"
    
    # Get climate parameters (simplified)
    avg_temp = climate_data.get('temperature', 25)
    annual_rainfall = climate_data.get('annual_rainfall', 1000)
    
    # Map budget level to investment category
    budget_map = {
        "Low": ["Low", "Medium-Low"],
        "Medium": ["Medium-Low", "Medium", "Medium-High"],
        "High": ["Medium", "Medium-High", "High"]
    }
    allowed_investments = budget_map.get(budget_level, ["Medium"])
    
    # Calculate crop suitability
    recommendations = []
    
    for crop_name, crop_info in crops_database.items():
        # Skip if previously grown (for crop rotation)
        if previous_crops and crop_name in previous_crops:
            continue
        
        # Check soil compatibility
        soil_match = soil_type in crop_info["soil_types"]
        
        # Check temperature suitability
        min_temp, max_temp = crop_info["temperature_range"]
        temp_match = min_temp <= avg_temp <= max_temp
        
        # Check rainfall suitability
        min_rain, max_rain = crop_info["rainfall_range"]
        rain_match = min_rain <= annual_rainfall <= max_rain
        
        # Check season suitability
        season_match = current_season in crop_info["growing_season"]
        
        # Check budget constraints
        budget_match = crop_info["investment_level"] in allowed_investments
        
        # Calculate overall suitability (weighted)
        soil_weight = 0.25
        temp_weight = 0.2
        rain_weight = 0.2
        season_weight = 0.2
        budget_weight = 0.15
        
        suitability = (
            (1 if soil_match else 0.3) * soil_weight +
            (1 if temp_match else 0.5) * temp_weight +
            (1 if rain_match else 0.5) * rain_weight +
            (1 if season_match else 0.3) * season_weight +
            (1 if budget_match else 0.2) * budget_weight
        )
        
        # Format suitability as percentage
        suitability_percentage = suitability * 100
        
        # Add to recommendations if suitability is reasonable
        if suitability >= 0.5:  # At least 50% suitable
            recommendation = {
                "crop": crop_name,
                "suitability": suitability_percentage,
                "growing_season": ", ".join(crop_info["growing_season"]),
                "time_to_harvest": crop_info["days_to_harvest"],
                "water_requirements": crop_info["water_requirements"],
                "fertilizer_needs": crop_info["fertilizer_needs"],
                "market_demand": crop_info["market_demand"],
                "estimated_yield": crop_info["typical_yield"],
                "price_trend": crop_info["price_trend"],
                "investment_level": crop_info["investment_level"],
                "rationale": generate_recommendation_rationale(
                    crop_name, suitability, soil_match, temp_match, 
                    rain_match, season_match, budget_match, land_size
                ),
                "cultivation_tips": crop_info["cultivation_tips"],
                "risks": crop_info["risks"]
            }
            
            recommendations.append(recommendation)
    
    # Sort by suitability (descending)
    recommendations.sort(key=lambda x: x["suitability"], reverse=True)
    
    return recommendations

def get_market_forecast(crop):
    """
    Get market demand forecast for a crop
    
    Args:
        crop: Crop name
        
    Returns:
        Market demand category
    """
    # In a real system, this would query market data APIs or databases
    # For demonstration, we'll use a simplified approach
    
    crop_demand = {
        "Maize": ["Medium", "High"],
        "Rice": ["Medium", "High"],
        "Wheat": ["Medium", "High"],
        "Soybeans": ["Medium", "High"],
        "Tomatoes": ["Medium", "High"],
        "Potatoes": ["Medium"],
        "Cotton": ["Medium", "Low", "High"],
        "Sunflower": ["Medium", "Low"],
        "Beans": ["Medium"],
        "Cassava": ["Medium", "Low"]
    }
    
    # Get possible demand categories for the crop
    possible_demand = crop_demand.get(crop, ["Medium"])
    
    # Select one with higher probability for Medium or High
    weights = {
        "Low": 0.2,
        "Medium": 0.5,
        "High": 0.3
    }
    
    weighted_demand = []
    for demand in possible_demand:
        weighted_demand.extend([demand] * int(weights[demand] * 10))
    
    return random.choice(weighted_demand)

def get_price_trend(crop):
    """
    Get price trend for a crop
    
    Args:
        crop: Crop name
        
    Returns:
        Price trend category
    """
    # In a real system, this would use historical price data and trends
    # For demonstration, we'll use a simplified approach
    
    trends = ["Declining", "Stable", "Rising"]
    weights = [0.2, 0.5, 0.3]  # More likely to be stable
    
    # Special cases for certain crops based on global trends
    if crop in ["Maize", "Wheat", "Rice", "Soybeans"]:
        weights = [0.2, 0.4, 0.4]  # Slightly more likely to rise (food security)
    elif crop in ["Cotton"]:
        weights = [0.3, 0.5, 0.2]  # Slightly more likely to decline (textile competition)
    
    return random.choices(trends, weights=weights)[0]

def generate_recommendation_rationale(crop, suitability, soil_match, temp_match, 
                                     rain_match, season_match, budget_match, land_size):
    """
    Generate a human-readable rationale for the crop recommendation
    
    Args:
        crop: Crop name
        suitability: Overall suitability score
        soil_match, temp_match, rain_match, season_match, budget_match: Boolean match flags
        land_size: Size of land in hectares
        
    Returns:
        Recommendation rationale string
    """
    reasons = []
    
    # Add positive reasons
    if soil_match:
        reasons.append(f"Your soil type is well-suited for {crop} cultivation")
    
    if temp_match:
        reasons.append(f"Current temperature conditions are favorable for {crop}")
    
    if rain_match:
        reasons.append(f"Annual rainfall in your region meets {crop} water requirements")
    
    if season_match:
        reasons.append(f"Current planting season is appropriate for {crop}")
    
    if budget_match:
        reasons.append(f"The investment requirements align with your budget level")
    
    # Add concerns for non-matches
    concerns = []
    
    if not soil_match:
        concerns.append(f"Your soil type may require amendments for optimal {crop} growth")
    
    if not temp_match:
        concerns.append(f"Temperature conditions may not be ideal; consider climate management strategies")
    
    if not rain_match:
        if rain_match < 0.3:
            concerns.append(f"Insufficient rainfall for {crop}; irrigation will be necessary")
        else:
            concerns.append(f"Rainfall patterns may require water management strategies")
    
    if not season_match:
        concerns.append(f"Current season is not optimal; consider adjusting planting schedule")
    
    if not budget_match:
        concerns.append(f"Investment requirements may exceed your specified budget")
    
    # Scale considerations
    if land_size < 1:
        scale_note = f"Your land size ({land_size:.2f} hectares) is suitable for small-scale {crop} production"
    elif land_size < 5:
        scale_note = f"Your land size ({land_size:.2f} hectares) allows for medium-scale {crop} production"
    else:
        scale_note = f"Your land size ({land_size:.2f} hectares) is appropriate for larger-scale {crop} cultivation"
    
    # Compose the rationale
    rationale = f"{crop} is recommended with a {suitability:.1f}% suitability score. "
    rationale += scale_note + ". "
    
    if reasons:
        rationale += "Favorable factors include: " + "; ".join(reasons) + ". "
    
    if concerns:
        rationale += "Considerations: " + "; ".join(concerns) + "."
    
    return rationale

def generate_environmental_impact_assessment(crop, land_size, farming_practices=None):
    """
    Generate an environmental impact assessment for a crop
    
    Args:
        crop: Crop name
        land_size: Size of land in hectares
        farming_practices: Optional dictionary of farming practices
        
    Returns:
        Dictionary with environmental impact assessment
    """
    # Define base environmental factors for each crop
    crop_env_factors = {
        "Maize": {
            "water_consumption": 550,  # mm/season
            "nitrogen_requirement": 150,  # kg/ha
            "pesticide_use": "Medium",
            "soil_erosion_risk": "Medium",
            "biodiversity_impact": "Medium",
            "carbon_footprint": "Medium"
        },
        "Rice": {
            "water_consumption": 1200,  # mm/season
            "nitrogen_requirement": 120,  # kg/ha
            "pesticide_use": "Medium-High",
            "soil_erosion_risk": "Low",
            "biodiversity_impact": "Medium-High",
            "carbon_footprint": "High"  # Due to methane emissions
        },
        "Wheat": {
            "water_consumption": 450,  # mm/season
            "nitrogen_requirement": 100,  # kg/ha
            "pesticide_use": "Medium",
            "soil_erosion_risk": "Medium",
            "biodiversity_impact": "Medium",
            "carbon_footprint": "Medium"
        },
        "Soybeans": {
            "water_consumption": 500,  # mm/season
            "nitrogen_requirement": 0,  # kg/ha - nitrogen fixing
            "pesticide_use": "Medium",
            "soil_erosion_risk": "Medium",
            "biodiversity_impact": "Medium",
            "carbon_footprint": "Low-Medium"
        },
        "Tomatoes": {
            "water_consumption": 600,  # mm/season
            "nitrogen_requirement": 200,  # kg/ha
            "pesticide_use": "High",
            "soil_erosion_risk": "Medium",
            "biodiversity_impact": "Medium",
            "carbon_footprint": "Medium-High"
        },
        "Potatoes": {
            "water_consumption": 500,  # mm/season
            "nitrogen_requirement": 180,  # kg/ha
            "pesticide_use": "High",
            "soil_erosion_risk": "Medium-High",
            "biodiversity_impact": "Medium",
            "carbon_footprint": "Medium"
        },
        "Cotton": {
            "water_consumption": 700,  # mm/season
            "nitrogen_requirement": 180,  # kg/ha
            "pesticide_use": "High",
            "soil_erosion_risk": "Medium-High",
            "biodiversity_impact": "High",
            "carbon_footprint": "High"
        },
        "Sunflower": {
            "water_consumption": 400,  # mm/season
            "nitrogen_requirement": 80,  # kg/ha
            "pesticide_use": "Low-Medium",
            "soil_erosion_risk": "Medium",
            "biodiversity_impact": "Medium-Low",
            "carbon_footprint": "Medium"
        },
        "Beans": {
            "water_consumption": 350,  # mm/season
            "nitrogen_requirement": 40,  # kg/ha (some nitrogen fixing)
            "pesticide_use": "Medium",
            "soil_erosion_risk": "Low-Medium",
            "biodiversity_impact": "Low",
            "carbon_footprint": "Low"
        },
        "Cassava": {
            "water_consumption": 400,  # mm/season
            "nitrogen_requirement": 60,  # kg/ha
            "pesticide_use": "Low",
            "soil_erosion_risk": "Medium",
            "biodiversity_impact": "Medium",
            "carbon_footprint": "Low"
        }
    }
    
    # Get factors for the selected crop or use defaults
    crop_factors = crop_env_factors.get(crop, {
        "water_consumption": 500,
        "nitrogen_requirement": 100,
        "pesticide_use": "Medium",
        "soil_erosion_risk": "Medium",
        "biodiversity_impact": "Medium",
        "carbon_footprint": "Medium"
    })
    
    # Adjust for farming practices if provided
    if farming_practices:
        # Example adjustments
        if farming_practices.get("organic", False):
            crop_factors["pesticide_use"] = "Low"
            crop_factors["biodiversity_impact"] = adjust_category(crop_factors["biodiversity_impact"], -1)
            crop_factors["carbon_footprint"] = adjust_category(crop_factors["carbon_footprint"], -1)
        
        if farming_practices.get("drip_irrigation", False):
            crop_factors["water_consumption"] *= 0.7  # 30% water saving
        
        if farming_practices.get("cover_crops", False):
            crop_factors["soil_erosion_risk"] = adjust_category(crop_factors["soil_erosion_risk"], -1)
            crop_factors["biodiversity_impact"] = adjust_category(crop_factors["biodiversity_impact"], -1)
    
    # Calculate total resource usage
    total_water = crop_factors["water_consumption"] * land_size  # cubic meters
    total_nitrogen = crop_factors["nitrogen_requirement"] * land_size  # kg
    
    # Generate assessment
    assessment = {
        "total_water_usage": {
            "value": total_water,
            "unit": "cubic meters",
            "note": f"Based on {crop_factors['water_consumption']} mm/season water requirement"
        },
        "total_nitrogen_requirement": {
            "value": total_nitrogen,
            "unit": "kg",
            "note": f"Based on {crop_factors['nitrogen_requirement']} kg/ha nitrogen requirement"
        },
        "pesticide_impact": {
            "level": crop_factors["pesticide_use"],
            "recommendation": get_pesticide_recommendation(crop_factors["pesticide_use"])
        },
        "soil_health_impact": {
            "erosion_risk": crop_factors["soil_erosion_risk"],
            "recommendation": get_soil_health_recommendation(crop_factors["soil_erosion_risk"])
        },
        "biodiversity_impact": {
            "level": crop_factors["biodiversity_impact"],
            "recommendation": get_biodiversity_recommendation(crop_factors["biodiversity_impact"])
        },
        "carbon_footprint": {
            "level": crop_factors["carbon_footprint"],
            "recommendation": get_carbon_recommendation(crop_factors["carbon_footprint"])
        },
        "sustainable_practices": get_sustainable_practice_recommendations(crop)
    }
    
    return assessment

def adjust_category(category, adjustment):
    """
    Adjust a category up or down the scale: Low -> Medium -> High
    
    Args:
        category: Current category
        adjustment: Adjustment value (-1 = down, +1 = up)
        
    Returns:
        Adjusted category
    """
    categories = [
        "Low", "Low-Medium", "Medium", "Medium-High", "High"
    ]
    
    if "-" in category:
        current_index = categories.index(category)
    else:
        # Handle single word categories
        simple_categories = ["Low", "Medium", "High"]
        try:
            simple_index = simple_categories.index(category)
            if simple_index == 0:
                current_index = 0
            elif simple_index == 1:
                current_index = 2
            else:
                current_index = 4
        except ValueError:
            current_index = 2  # Default to Medium
    
    new_index = max(0, min(len(categories) - 1, current_index + adjustment))
    return categories[new_index]

def get_pesticide_recommendation(level):
    """Get recommendation for pesticide management based on impact level"""
    recommendations = {
        "Low": "Continue minimal pesticide practices. Consider biological controls and resistant varieties.",
        "Low-Medium": "Monitor pest populations regularly. Use targeted applications only when necessary.",
        "Medium": "Implement Integrated Pest Management (IPM) strategies. Rotate pesticide classes to prevent resistance.",
        "Medium-High": "Carefully time applications to maximize effectiveness while minimizing quantity. Consider beneficial borders and trap crops.",
        "High": "Implement comprehensive IPM program. Consider organic alternatives where possible and use precise application methods."
    }
    return recommendations.get(level, recommendations["Medium"])

def get_soil_health_recommendation(level):
    """Get recommendation for soil health management based on erosion risk"""
    recommendations = {
        "Low": "Maintain current soil conservation practices. Consider cover crops during off-seasons.",
        "Low-Medium": "Implement crop residue management. Minimize tillage where possible.",
        "Medium": "Use contour farming on slopes. Incorporate organic matter to improve soil structure.",
        "Medium-High": "Implement strip cropping or terracing on slopes. Maintain vegetation in drainage areas.",
        "High": "Use no-till or reduced tillage methods. Establish permanent vegetation on highly erodible areas."
    }
    return recommendations.get(level, recommendations["Medium"])

def get_biodiversity_recommendation(level):
    """Get recommendation for biodiversity management based on impact level"""
    recommendations = {
        "Low": "Maintain diverse field margins. Consider expanding habitat areas when possible.",
        "Low-Medium": "Plant flower strips to support pollinators. Preserve nearby natural areas.",
        "Medium": "Establish hedgerows or windbreaks with native species. Minimize night lighting.",
        "Medium-High": "Create wildlife corridors connecting natural areas. Implement diverse crop rotations.",
        "High": "Restore native vegetation in non-productive areas. Establish buffer zones around water features."
    }
    return recommendations.get(level, recommendations["Medium"])

def get_carbon_recommendation(level):
    """Get recommendation for carbon footprint reduction based on impact level"""
    recommendations = {
        "Low": "Maintain current practices. Consider renewable energy for farm operations.",
        "Low-Medium": "Minimize equipment idling. Use cover crops to sequester carbon.",
        "Medium": "Reduce tillage intensity. Optimize fertilizer applications to reduce N2O emissions.",
        "Medium-High": "Implement precision agriculture techniques. Consider composting to reduce waste.",
        "High": "Transition to no-till practices. Use nitrogen inhibitors with fertilizers."
    }
    return recommendations.get(level, recommendations["Medium"])

def get_sustainable_practice_recommendations(crop):
    """Get sustainable practice recommendations specific to the crop"""
    general_practices = [
        "Implement crop rotation to disrupt pest cycles and improve soil health.",
        "Use cover crops during off-seasons to prevent erosion and build soil organic matter.",
        "Establish buffer strips along waterways to prevent nutrient runoff.",
        "Consider precision agriculture technologies to optimize resource use."
    ]
    
    crop_specific = {
        "Maize": [
            "Use strip-tillage or no-till practices to reduce soil disturbance.",
            "Implement split nitrogen applications to match crop uptake patterns.",
            "Consider drought-tolerant varieties in water-limited areas."
        ],
        "Rice": [
            "Implement alternate wetting and drying techniques to reduce water use and methane emissions.",
            "Use direct seeding where appropriate to reduce labor and water requirements.",
            "Incorporate rice straw into soil rather than burning to improve soil health."
        ],
        "Wheat": [
            "Use optimal seeding rates to maximize resource efficiency.",
            "Implement variable rate technology for fertilizer applications.",
            "Consider using soil moisture monitors to optimize irrigation scheduling."
        ],
        "Soybeans": [
            "Inoculate seeds with Rhizobium bacteria to ensure nitrogen fixation.",
            "Use narrow row spacing to achieve canopy closure faster and suppress weeds.",
            "Implement conservation tillage to maintain soil organic matter."
        ],
        "Tomatoes": [
            "Use drip irrigation with mulch to conserve water and reduce disease pressure.",
            "Consider grafted plants for improved disease resistance and vigor.",
            "Implement beneficial insect habitat to support natural pest control."
        ],
        "Potatoes": [
            "Use appropriate seed piece spacing to optimize resource use.",
            "Implement proper hilling practices to prevent greening and erosion.",
            "Use soil testing to precisely match fertilizer applications to crop needs."
        ],
        "Cotton": [
            "Implement precision irrigation to reduce water consumption.",
            "Use targeted spraying for pest management to reduce pesticide use.",
            "Consider conservation tillage to reduce soil erosion."
        ],
        "Sunflower": [
            "Plant pollinator-friendly borders to support seed set.",
            "Optimize plant density to maximize yield while reducing disease pressure.",
            "Use reduced tillage practices to maintain soil moisture."
        ],
        "Beans": [
            "Use appropriate inoculants to support nitrogen fixation.",
            "Implement drip irrigation to reduce foliar disease pressure.",
            "Consider intercropping with compatible species."
        ],
        "Cassava": [
            "Implement mulching to conserve soil moisture and suppress weeds.",
            "Use clean planting material to prevent disease introduction.",
            "Maintain vegetation on field borders to reduce erosion."
        ]
    }
    
    # Combine general and crop-specific practices
    specific_practices = crop_specific.get(crop, [])
    return general_practices + specific_practices