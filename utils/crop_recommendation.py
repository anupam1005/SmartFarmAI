import numpy as np
import pandas as pd
import random
from datetime import datetime

def get_crop_recommendations(params):
    """
    Generate crop recommendations based on input parameters
    
    Args:
        params: Dictionary containing soil and climate parameters
        
    Returns:
        List of dictionaries with crop recommendations
    """
    # Extract parameters
    soil_type = params.get('soil_type', 'Loam')
    soil_ph = params.get('soil_ph', 6.5)
    nitrogen = params.get('nitrogen', 50)
    phosphorus = params.get('phosphorus', 40)
    potassium = params.get('potassium', 50)
    organic_matter = params.get('organic_matter', 2.5)
    annual_rainfall = params.get('annual_rainfall', 1200)
    temperature = params.get('temperature', 25)
    irrigation = params.get('irrigation', 'Adequate')
    market_access = params.get('market_access', 'Good')
    region = params.get('region', '')
    
    # Define crop requirements and characteristics
    crops = [
        {
            "crop": "Maize",
            "soil_preference": ["Loam", "Sandy Loam", "Clay Loam"],
            "ph_range": (5.5, 7.5),
            "temp_range": (18, 35),
            "rainfall_range": (500, 1800),
            "growing_season": "3-5 months",
            "time_to_harvest": "90-120 days",
            "water_requirements": "Medium",
            "fertilizer_needs": "High in Nitrogen",
            "market_demand": "High",
            "estimated_yield": "4-8 tons/hectare",
            "price_trend": "Stable to Increasing",
            "investment_level": "Medium",
            "nutrients": {"N": 80, "P": 40, "K": 30}
        },
        {
            "crop": "Beans",
            "soil_preference": ["Loam", "Sandy Loam", "Silt"],
            "ph_range": (6.0, 7.5),
            "temp_range": (16, 30),
            "rainfall_range": (400, 1500),
            "growing_season": "2-3 months",
            "time_to_harvest": "60-90 days",
            "water_requirements": "Low to Medium",
            "fertilizer_needs": "Low (Nitrogen fixing)",
            "market_demand": "Medium to High",
            "estimated_yield": "1.5-3 tons/hectare",
            "price_trend": "Increasing",
            "investment_level": "Low",
            "nutrients": {"N": 30, "P": 50, "K": 30}
        },
        {
            "crop": "Tomatoes",
            "soil_preference": ["Loam", "Sandy Loam", "Clay Loam"],
            "ph_range": (5.5, 7.0),
            "temp_range": (20, 35),
            "rainfall_range": (600, 1300),
            "growing_season": "3-4 months",
            "time_to_harvest": "70-100 days",
            "water_requirements": "Medium to High",
            "fertilizer_needs": "Medium (Balanced NPK)",
            "market_demand": "High",
            "estimated_yield": "15-40 tons/hectare",
            "price_trend": "Fluctuating",
            "investment_level": "Medium to High",
            "nutrients": {"N": 60, "P": 60, "K": 60}
        },
        {
            "crop": "Cassava",
            "soil_preference": ["Sandy", "Sandy Loam", "Loam"],
            "ph_range": (5.0, 6.5),
            "temp_range": (22, 32),
            "rainfall_range": (800, 2000),
            "growing_season": "9-12 months",
            "time_to_harvest": "9-12 months",
            "water_requirements": "Low (Drought Resistant)",
            "fertilizer_needs": "Low",
            "market_demand": "Medium",
            "estimated_yield": "10-25 tons/hectare",
            "price_trend": "Stable",
            "investment_level": "Low",
            "nutrients": {"N": 40, "P": 20, "K": 60}
        },
        {
            "crop": "Sweet Potato",
            "soil_preference": ["Sandy", "Sandy Loam", "Loam"],
            "ph_range": (5.5, 6.5),
            "temp_range": (20, 30),
            "rainfall_range": (750, 1500),
            "growing_season": "3-5 months",
            "time_to_harvest": "90-150 days",
            "water_requirements": "Low to Medium",
            "fertilizer_needs": "Low",
            "market_demand": "Medium",
            "estimated_yield": "10-20 tons/hectare",
            "price_trend": "Stable",
            "investment_level": "Low",
            "nutrients": {"N": 30, "P": 30, "K": 60}
        },
        {
            "crop": "Rice",
            "soil_preference": ["Clay", "Clay Loam", "Loam"],
            "ph_range": (5.5, 7.0),
            "temp_range": (20, 35),
            "rainfall_range": (1000, 2500),
            "growing_season": "3-6 months",
            "time_to_harvest": "100-180 days",
            "water_requirements": "High",
            "fertilizer_needs": "Medium to High",
            "market_demand": "High",
            "estimated_yield": "3-6 tons/hectare",
            "price_trend": "Stable to Increasing",
            "investment_level": "Medium to High",
            "nutrients": {"N": 90, "P": 40, "K": 40}
        },
        {
            "crop": "Sorghum",
            "soil_preference": ["Loam", "Clay Loam", "Sandy Loam"],
            "ph_range": (5.5, 7.5),
            "temp_range": (20, 38),
            "rainfall_range": (400, 1000),
            "growing_season": "3-4 months",
            "time_to_harvest": "90-120 days",
            "water_requirements": "Low (Drought Resistant)",
            "fertilizer_needs": "Low to Medium",
            "market_demand": "Medium",
            "estimated_yield": "1.5-4 tons/hectare",
            "price_trend": "Stable",
            "investment_level": "Low",
            "nutrients": {"N": 60, "P": 30, "K": 30}
        },
        {
            "crop": "Groundnuts",
            "soil_preference": ["Sandy", "Sandy Loam", "Loam"],
            "ph_range": (5.5, 7.0),
            "temp_range": (20, 35),
            "rainfall_range": (500, 1200),
            "growing_season": "3-5 months",
            "time_to_harvest": "90-150 days",
            "water_requirements": "Low to Medium",
            "fertilizer_needs": "Low (Nitrogen fixing)",
            "market_demand": "Medium to High",
            "estimated_yield": "1-3 tons/hectare",
            "price_trend": "Increasing",
            "investment_level": "Medium",
            "nutrients": {"N": 20, "P": 60, "K": 30}
        },
        {
            "crop": "Cabbage",
            "soil_preference": ["Loam", "Clay Loam", "Sandy Loam"],
            "ph_range": (6.0, 7.5),
            "temp_range": (15, 25),
            "rainfall_range": (800, 1500),
            "growing_season": "3-4 months",
            "time_to_harvest": "80-120 days",
            "water_requirements": "Medium to High",
            "fertilizer_needs": "Medium (Balanced NPK)",
            "market_demand": "Medium",
            "estimated_yield": "20-50 tons/hectare",
            "price_trend": "Fluctuating",
            "investment_level": "Medium",
            "nutrients": {"N": 60, "P": 30, "K": 30}
        },
        {
            "crop": "Onions",
            "soil_preference": ["Loam", "Sandy Loam", "Silt"],
            "ph_range": (6.0, 7.0),
            "temp_range": (13, 30),
            "rainfall_range": (600, 1200),
            "growing_season": "3-5 months",
            "time_to_harvest": "90-150 days",
            "water_requirements": "Medium",
            "fertilizer_needs": "Medium",
            "market_demand": "High",
            "estimated_yield": "15-40 tons/hectare",
            "price_trend": "Fluctuating",
            "investment_level": "Medium",
            "nutrients": {"N": 40, "P": 60, "K": 40}
        }
    ]
    
    # Calculate suitability scores for each crop
    results = []
    
    for crop in crops:
        # Calculate soil type suitability (0-100)
        soil_score = 100 if soil_type in crop["soil_preference"] else 50
        
        # Calculate pH suitability (0-100)
        min_ph, max_ph = crop["ph_range"]
        if min_ph <= soil_ph <= max_ph:
            ph_score = 100
        else:
            ph_distance = min(abs(soil_ph - min_ph), abs(soil_ph - max_ph))
            ph_score = max(0, 100 - (ph_distance * 25))  # Reduce by 25 points per pH unit
        
        # Calculate temperature suitability (0-100)
        min_temp, max_temp = crop["temp_range"]
        if min_temp <= temperature <= max_temp:
            temp_score = 100
        else:
            temp_distance = min(abs(temperature - min_temp), abs(temperature - max_temp))
            temp_score = max(0, 100 - (temp_distance * 10))  # Reduce by 10 points per degree C
        
        # Calculate rainfall suitability (0-100)
        min_rain, max_rain = crop["rainfall_range"]
        if min_rain <= annual_rainfall <= max_rain:
            rain_score = 100
        else:
            rain_distance = min(abs(annual_rainfall - min_rain), abs(annual_rainfall - max_rain))
            rain_score = max(0, 100 - (rain_distance / 100))  # Reduce by 1 point per 100mm
        
        # Adjust for irrigation availability
        if irrigation == "Abundant":
            rain_score = max(rain_score, 80)  # Irrigation can compensate for low rainfall
        elif irrigation == "Adequate":
            rain_score = max(rain_score, 60)
        elif irrigation == "Limited":
            rain_score = max(rain_score, 40)
        
        # Calculate nutrient suitability (0-100)
        n_requirement = crop["nutrients"]["N"]
        p_requirement = crop["nutrients"]["P"]
        k_requirement = crop["nutrients"]["K"]
        
        n_score = 100 - min(100, abs(nitrogen - n_requirement))
        p_score = 100 - min(100, abs(phosphorus - p_requirement))
        k_score = 100 - min(100, abs(potassium - k_requirement))
        
        nutrient_score = (n_score + p_score + k_score) / 3
        
        # Adjust for market access
        market_factor = {
            "Excellent": 1.2,
            "Good": 1.0,
            "Fair": 0.8,
            "Poor": 0.6
        }.get(market_access, 1.0)
        
        # Calculate overall suitability score
        suitability = (soil_score * 0.15 + 
                       ph_score * 0.10 + 
                       temp_score * 0.20 + 
                       rain_score * 0.20 + 
                       nutrient_score * 0.25) * market_factor
        
        # Calculate overall suitability score
        suitability = min(100, max(0, suitability))  # Ensure score is between 0-100
        
        # Generate rationale based on scores
        rationale_parts = []
        
        if soil_score >= 80:
            rationale_parts.append(f"your {soil_type} soil is ideal for this crop")
        
        if ph_score >= 80:
            rationale_parts.append(f"the soil pH of {soil_ph} is in the optimal range")
        
        if temp_score >= 80:
            rationale_parts.append(f"your average temperature of {temperature}°C is suitable")
        
        if rain_score >= 80:
            rationale_parts.append(f"your annual rainfall of {annual_rainfall}mm is appropriate")
        elif irrigation in ["Adequate", "Abundant"]:
            rationale_parts.append("your irrigation capacity can supplement water needs")
        
        if nutrient_score >= 70:
            rationale_parts.append("your soil nutrient profile matches this crop's requirements")
        
        if market_access in ["Good", "Excellent"]:
            rationale_parts.append(f"you have {market_access.lower()} market access for this crop")
        
        # Join rationale parts with proper grammar
        if rationale_parts:
            rationale = "This crop is recommended because " + ", and ".join(rationale_parts) + "."
        else:
            rationale = "This crop is a reasonable choice for your conditions, though not optimal."
        
        # Generate cultivation tips
        tips = [
            f"Plant {crop['crop']} during the season when temperatures are between {crop['temp_range'][0]}°C and {crop['temp_range'][1]}°C.",
            f"Ensure soil pH is maintained between {crop['ph_range'][0]} and {crop['ph_range'][1]} for optimal growth.",
            f"This crop requires {crop['water_requirements'].lower()} water; adjust irrigation accordingly.",
            f"{crop['crop']} typically takes {crop['time_to_harvest']} to reach harvest maturity."
        ]
        
        # Add specific nutrient tips
        if "High in Nitrogen" in crop["fertilizer_needs"]:
            tips.append("Apply nitrogen-rich fertilizers during the vegetative growth stage.")
        elif "Balanced NPK" in crop["fertilizer_needs"]:
            tips.append("Use a balanced NPK fertilizer throughout the growing season.")
        elif "Nitrogen fixing" in crop["fertilizer_needs"]:
            tips.append("This crop can fix nitrogen from the atmosphere, reducing fertilizer needs.")
        
        # Generate potential risks
        risks = []
        
        if soil_score < 60:
            risks.append(f"Your {soil_type} soil is not ideal for {crop['crop']}; consider soil amendments.")
        
        if ph_score < 60:
            risks.append(f"Soil pH of {soil_ph} is outside the optimal range; lime or sulfur applications may be needed.")
        
        if temp_score < 60:
            risks.append(f"Your average temperature of {temperature}°C may stress this crop during parts of the season.")
        
        if rain_score < 60 and irrigation in ["None", "Limited"]:
            risks.append("Insufficient rainfall and irrigation may lead to water stress.")
        
        if nutrient_score < 60:
            risks.append("Soil nutrients are imbalanced for this crop; consider soil testing and targeted fertilization.")
        
        risks_text = " ".join(risks) if risks else "No significant risks identified with your current conditions."
        
        # Add to results
        results.append({
            "crop": crop["crop"],
            "suitability": round(suitability),
            "growing_season": crop["growing_season"],
            "time_to_harvest": crop["time_to_harvest"],
            "water_requirements": crop["water_requirements"],
            "fertilizer_needs": crop["fertilizer_needs"],
            "market_demand": crop["market_demand"],
            "estimated_yield": crop["estimated_yield"],
            "price_trend": crop["price_trend"],
            "investment_level": crop["investment_level"],
            "rationale": rationale,
            "cultivation_tips": "\n".join(tips),
            "risks": risks_text
        })
    
    # Sort by suitability score (descending)
    results.sort(key=lambda x: x["suitability"], reverse=True)
    
    # Return top results (max 5)
    return results[:5]

def get_rotation_suggestions(current_crops):
    """
    Get crop rotation suggestions based on current crops
    
    Args:
        current_crops: List of current crops
        
    Returns:
        List of rotation suggestions with rationale
    """
    # Define crop families for rotation planning
    crop_families = {
        "Legumes": ["Beans", "Groundnuts", "Peas", "Soybeans"],
        "Grains": ["Maize", "Rice", "Wheat", "Sorghum", "Millet"],
        "Root Crops": ["Cassava", "Sweet Potatoes", "Yams", "Carrots"],
        "Fruit Vegetables": ["Tomatoes", "Peppers", "Eggplant", "Okra"],
        "Leafy Vegetables": ["Cabbage", "Spinach", "Kale", "Lettuce"],
        "Alliums": ["Onions", "Garlic", "Leeks"]
    }
    
    # Create a reverse mapping from crop to family
    crop_to_family = {}
    for family, crops in crop_families.items():
        for crop in crops:
            crop_to_family[crop] = family
    
    # Identify the families of current crops
    current_families = []
    for crop in current_crops:
        family = crop_to_family.get(crop)
        if family and family not in current_families:
            current_families.append(family)
    
    # Define rotation principles
    rotation_principles = [
        {
            "name": "Family Rotation",
            "description": "Rotate crops from different botanical families to reduce pest and disease buildup.",
            "priority": 1
        },
        {
            "name": "Nutrient Cycling",
            "description": "Follow heavy feeders with light feeders or nitrogen fixers.",
            "priority": 2
        },
        {
            "name": "Root Depth Variation",
            "description": "Alternate deep-rooted crops with shallow-rooted crops to use different soil layers.",
            "priority": 3
        },
        {
            "name": "Pest and Disease Management",
            "description": "Avoid planting crops susceptible to the same pests and diseases in succession.",
            "priority": 1
        }
    ]
    
    # Define nutrient usage categories
    nutrient_usage = {
        "Heavy Feeders": ["Maize", "Tomatoes", "Cabbage", "Rice", "Peppers", "Eggplant"],
        "Medium Feeders": ["Carrots", "Okra", "Spinach", "Kale", "Lettuce", "Onions", "Garlic"],
        "Light Feeders": ["Sweet Potatoes", "Cassava", "Sorghum", "Millet"],
        "Nitrogen Fixers": ["Beans", "Groundnuts", "Peas", "Soybeans"]
    }
    
    # Create a reverse mapping from crop to nutrient usage
    crop_to_nutrient = {}
    for category, crops in nutrient_usage.items():
        for crop in crops:
            crop_to_nutrient[crop] = category
    
    # Identify current nutrient usage categories
    current_nutrient_categories = []
    for crop in current_crops:
        category = crop_to_nutrient.get(crop)
        if category and category not in current_nutrient_categories:
            current_nutrient_categories.append(category)
    
    # Determine recommended next crop families and nutrient categories
    recommended_families = []
    for family, crops in crop_families.items():
        if family not in current_families:
            recommended_families.append(family)
    
    recommended_nutrient_categories = []
    if "Heavy Feeders" in current_nutrient_categories:
        recommended_nutrient_categories.append("Nitrogen Fixers")
    elif "Nitrogen Fixers" in current_nutrient_categories:
        recommended_nutrient_categories.append("Heavy Feeders")
    else:
        if "Light Feeders" not in current_nutrient_categories:
            recommended_nutrient_categories.append("Light Feeders")
        if "Medium Feeders" not in current_nutrient_categories:
            recommended_nutrient_categories.append("Medium Feeders")
    
    # Generate rotation suggestions
    rotation_suggestions = []
    
    # If we have both recommended families and nutrient categories, find the intersection
    ideal_rotation_crops = []
    for family in recommended_families:
        for crop in crop_families[family]:
            nutrient_category = crop_to_nutrient.get(crop)
            if nutrient_category in recommended_nutrient_categories:
                ideal_rotation_crops.append({
                    "crop": crop,
                    "family": family,
                    "nutrient_category": nutrient_category,
                    "score": 100
                })
    
    # If we don't have an intersection, prioritize family rotation
    if not ideal_rotation_crops:
        for family in recommended_families:
            for crop in crop_families[family]:
                ideal_rotation_crops.append({
                    "crop": crop,
                    "family": family,
                    "nutrient_category": crop_to_nutrient.get(crop, "Unknown"),
                    "score": 80
                })
    
    # If we still don't have suggestions, use any crop from recommended nutrient categories
    if not ideal_rotation_crops:
        for category in recommended_nutrient_categories:
            for crop in nutrient_usage[category]:
                ideal_rotation_crops.append({
                    "crop": crop,
                    "family": crop_to_family.get(crop, "Unknown"),
                    "nutrient_category": category,
                    "score": 60
                })
    
    # Format the results
    for crop_info in ideal_rotation_crops:
        crop = crop_info["crop"]
        family = crop_info["family"]
        nutrient_category = crop_info["nutrient_category"]
        score = crop_info["score"]
        
        # Skip if this crop is already in current crops
        if crop in current_crops:
            continue
        
        # Generate rationale
        rationale = []
        
        if family not in current_families:
            rationale.append(f"different plant family ({family}) than current crops")
        
        if nutrient_category in recommended_nutrient_categories:
            if nutrient_category == "Nitrogen Fixers":
                rationale.append("helps replenish soil nitrogen")
            elif nutrient_category == "Light Feeders":
                rationale.append("requires fewer nutrients, allowing soil to recover")
            elif nutrient_category == "Heavy Feeders":
                rationale.append("can benefit from nitrogen added by previous legume crops")
        
        rotation_suggestions.append({
            "Current Crops": ", ".join(current_crops),
            "Suggested Crop": crop,
            "Plant Family": family,
            "Nutrient Usage": nutrient_category,
            "Suitability Score": score,
            "Rationale": f"Rotation with {crop} is recommended because it is a {nutrient_category.lower()} from the {family} family, " + 
                         "which " + " and ".join(rationale) + "."
        })
    
    # Sort by suitability score
    rotation_suggestions.sort(key=lambda x: x["Suitability Score"], reverse=True)
    
    # Return top rotation suggestions (max 5)
    return rotation_suggestions[:5]

def get_rotation_benefits(current_crops, rotation_plan):
    """
    Get the benefits of the suggested crop rotation plan
    
    Args:
        current_crops: List of current crops
        rotation_plan: List of rotation suggestions
        
    Returns:
        List of benefit statements
    """
    # Define potential benefits of proper crop rotation
    all_benefits = [
        "Reduces pest pressure by breaking pest lifecycles",
        "Decreases disease incidence by removing host plants",
        "Improves soil structure through different root systems",
        "Enhances soil fertility, particularly when including legumes",
        "Reduces reliance on synthetic fertilizers",
        "Increases microbial diversity in the soil",
        "Minimizes weed pressure through competition",
        "Optimizes use of soil nutrients from different soil depths",
        "Spreads economic risk across multiple crops",
        "Improves yield stability year-over-year",
        "Reduces erosion by maintaining year-round soil cover",
        "Increases overall farm biodiversity"
    ]
    
    # Count the plant families and nutrient categories in rotation plan
    families = set()
    nutrient_categories = set()
    
    for crop in current_crops:
        for suggestion in rotation_plan:
            if suggestion["Suggested Crop"] == crop:
                families.add(suggestion["Plant Family"])
                nutrient_categories.add(suggestion["Nutrient Usage"])
    
    # Select benefits based on the diversity of the rotation plan
    selected_benefits = []
    
    # If we have good family diversity
    if len(families) >= 3:
        selected_benefits.append(all_benefits[0])  # Pest lifecycle
        selected_benefits.append(all_benefits[1])  # Disease
    
    # If we have nitrogen fixers
    if "Nitrogen Fixers" in nutrient_categories:
        selected_benefits.append(all_benefits[3])  # Soil fertility
        selected_benefits.append(all_benefits[4])  # Fertilizer reliance
    
    # If we have mix of root depths (assumed if we have diverse families)
    if len(families) >= 2:
        selected_benefits.append(all_benefits[2])  # Soil structure
        selected_benefits.append(all_benefits[7])  # Nutrient depths
    
    # If we have diverse crops
    if len(rotation_plan) >= 3:
        selected_benefits.append(all_benefits[8])  # Economic risk
        selected_benefits.append(all_benefits[9])  # Yield stability
        selected_benefits.append(all_benefits[11])  # Biodiversity
    
    # Add general benefits if we don't have enough specific ones
    while len(selected_benefits) < 5:
        benefit = random.choice(all_benefits)
        if benefit not in selected_benefits:
            selected_benefits.append(benefit)
    
    return selected_benefits
