import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_water_requirements(crop_type, growth_stage, area_size, soil_type, temperature, rainfall):
    """
    Calculate estimated water requirements for a crop
    
    Args:
        crop_type: Type of crop
        growth_stage: Current growth stage of the crop
        area_size: Size of the area in hectares
        soil_type: Type of soil
        temperature: Current temperature in Celsius
        rainfall: Recent rainfall in mm
        
    Returns:
        Water requirement in liters
    """
    # Base water requirements per hectare per day (in liters)
    base_requirements = {
        "Maize": 50000,
        "Tomatoes": 55000,
        "Beans": 40000,
        "Cassava": 35000,
        "Sweet Potato": 30000,
        "Rice": 80000,
        "Wheat": 45000,
        "Sorghum": 40000,
        "Millet": 35000,
        "Groundnuts": 45000
    }
    
    # Adjustment factors for growth stages
    stage_factors = {
        "Seedling": 0.5,
        "Vegetative": 0.8,
        "Flowering": 1.2,
        "Fruiting": 1.0,
        "Maturity": 0.6
    }
    
    # Soil type adjustment factors
    soil_factors = {
        "Sandy": 1.2,  # Drains quickly, needs more water
        "Clay": 0.8,   # Retains water, needs less
        "Loam": 1.0,   # Balanced soil type
        "Silt": 0.9,   # Good water retention
        "Clay Loam": 0.85,
        "Sandy Loam": 1.1
    }
    
    # Temperature adjustment - more water needed at higher temperatures
    temp_factor = 1.0
    if temperature > 30:
        temp_factor = 1.3
    elif temperature > 25:
        temp_factor = 1.15
    elif temperature < 15:
        temp_factor = 0.8
    
    # Rainfall adjustment - reduce water needs based on recent rainfall
    rainfall_factor = max(0.5, 1.0 - (rainfall / 50))  # Minimum 50% reduction even with heavy rain
    
    # Get base requirement with fallback
    base_req = base_requirements.get(crop_type, 45000)  # Default if crop not in list
    
    # Calculate adjusted water requirement
    daily_req = base_req * stage_factors.get(growth_stage, 1.0) * soil_factors.get(soil_type, 1.0) * temp_factor * rainfall_factor
    
    # Multiply by area size
    total_req = daily_req * area_size
    
    return round(total_req)

def get_fertilizer_requirements(crop_type, growth_stage, area_size, soil_nutrients):
    """
    Calculate fertilizer requirements based on crop needs and soil conditions
    
    Args:
        crop_type: Type of crop
        growth_stage: Current growth stage
        area_size: Area size in hectares
        soil_nutrients: Dictionary with current soil nutrient levels
        
    Returns:
        Dictionary with fertilizer recommendations
    """
    # Base NPK requirements per hectare (in kg)
    base_requirements = {
        "Maize": {"N": 120, "P": 60, "K": 60},
        "Tomatoes": {"N": 150, "P": 100, "K": 150},
        "Beans": {"N": 80, "P": 80, "K": 80},
        "Cassava": {"N": 100, "P": 50, "K": 100},
        "Sweet Potato": {"N": 80, "P": 80, "K": 120},
        "Rice": {"N": 150, "P": 60, "K": 80},
        "Wheat": {"N": 120, "P": 60, "K": 50},
        "Sorghum": {"N": 100, "P": 50, "K": 50},
        "Millet": {"N": 80, "P": 40, "K": 40},
        "Groundnuts": {"N": 60, "P": 80, "K": 60}
    }
    
    # Get requirements with fallback
    crop_req = base_requirements.get(crop_type, {"N": 100, "P": 60, "K": 60})
    
    # Adjust based on growth stage
    stage_factors = {
        "Seedling": {"N": 0.3, "P": 0.5, "K": 0.2},
        "Vegetative": {"N": 0.6, "P": 0.3, "K": 0.4},
        "Flowering": {"N": 0.3, "P": 0.4, "K": 0.6},
        "Fruiting": {"N": 0.2, "P": 0.3, "K": 0.8},
        "Maturity": {"N": 0.1, "P": 0.2, "K": 0.4}
    }
    
    stage_factor = stage_factors.get(growth_stage, {"N": 0.4, "P": 0.4, "K": 0.4})
    
    # Adjust based on current soil nutrient levels
    soil_n = soil_nutrients.get("nitrogen", 50)
    soil_p = soil_nutrients.get("phosphorus", 40)
    soil_k = soil_nutrients.get("potassium", 50)
    
    # Calculate required nutrients (reduced if soil levels are high)
    n_req = max(0, crop_req["N"] * stage_factor["N"] * (1 - soil_n/150))
    p_req = max(0, crop_req["P"] * stage_factor["P"] * (1 - soil_p/150))
    k_req = max(0, crop_req["K"] * stage_factor["K"] * (1 - soil_k/200))
    
    # Multiply by area
    n_req = n_req * area_size
    p_req = p_req * area_size
    k_req = k_req * area_size
    
    # Formulate recommendations
    recommendations = {
        "NPK": {
            "amount": round(max(n_req, p_req, k_req) * 2),  # Rough estimate for balanced fertilizer
            "timing": "Apply before expected rain or irrigate after application",
            "method": "Side-dressing" if growth_stage in ["Vegetative", "Flowering"] else "Broadcast"
        },
        "Nitrogen": {
            "amount": round(n_req),
            "timing": "Apply during vegetative growth phase",
            "method": "Side-dressing or foliar spray"
        },
        "Phosphorus": {
            "amount": round(p_req),
            "timing": "Apply at planting and early growth stages",
            "method": "Incorporate into soil before planting"
        },
        "Potassium": {
            "amount": round(k_req),
            "timing": "Apply before flowering and fruiting stages",
            "method": "Side-dressing"
        }
    }
    
    return recommendations

def calculate_water_efficiency(water_usage, crop_yield, crop_type, area_size):
    """
    Calculate water use efficiency
    
    Args:
        water_usage: Total water used in liters
        crop_yield: Crop yield in kg
        crop_type: Type of crop
        area_size: Area size in hectares
        
    Returns:
        Water efficiency score (0-100)
    """
    # Benchmark water productivity (kg yield per cubic meter of water)
    benchmarks = {
        "Maize": 2.0,
        "Tomatoes": 12.0,
        "Beans": 1.5,
        "Cassava": 5.0,
        "Sweet Potato": 4.0,
        "Rice": 0.7,
        "Wheat": 1.0,
        "Sorghum": 1.2,
        "Millet": 1.0,
        "Groundnuts": 0.8
    }
    
    benchmark = benchmarks.get(crop_type, 2.0)  # Default if crop not in list
    
    # Calculate water productivity (kg/m³)
    water_cubic_meters = water_usage / 1000  # Convert liters to cubic meters
    actual_productivity = crop_yield / water_cubic_meters if water_cubic_meters > 0 else 0
    
    # Calculate efficiency score (0-100)
    efficiency_ratio = actual_productivity / benchmark if benchmark > 0 else 0
    efficiency_score = min(100, max(0, efficiency_ratio * 100))
    
    return round(efficiency_score)

def get_water_saving_tips():
    """
    Get random water saving tips for farming
    
    Returns:
        A water saving tip
    """
    tips = [
        "Apply mulch around plants to reduce water evaporation from soil.",
        "Install drip irrigation systems to minimize water waste.",
        "Water early in the morning to reduce evaporation loss.",
        "Use soil moisture sensors to optimize irrigation timing.",
        "Harvest rainwater for irrigation during dry periods.",
        "Plant drought-resistant crop varieties when possible.",
        "Create windbreaks to reduce evaporation caused by wind.",
        "Maintain irrigation systems to prevent leaks and ensure efficiency.",
        "Practice deficit irrigation - providing less water during drought-tolerant growth stages.",
        "Group plants with similar water needs together for efficient irrigation."
    ]
    
    return random.choice(tips)

def get_fertilizer_application_tips():
    """
    Get random fertilizer application tips
    
    Returns:
        A fertilizer application tip
    """
    tips = [
        "Apply fertilizers in the early morning or late afternoon to reduce nutrient loss.",
        "Split fertilizer applications throughout the growing season for better uptake.",
        "Incorporate organic matter to improve soil structure and nutrient retention.",
        "Use precision application methods to place fertilizers near plant roots.",
        "Avoid applying fertilizers before heavy rain to prevent runoff and leaching.",
        "Test soil regularly to avoid over-application of nutrients.",
        "Use slow-release fertilizers for more efficient nutrient usage.",
        "Apply foliar fertilizers during critical growth stages for immediate uptake.",
        "Rotate legume crops to naturally add nitrogen to soil.",
        "Consider using organic fertilizers to improve soil health long-term."
    ]
    
    return random.choice(tips)

def generate_resource_usage_report(crop_data, water_usage, fertilizer_usage, start_date, end_date):
    """
    Generate a resource usage report for a given time period
    
    Args:
        crop_data: Dictionary with crop information
        water_usage: List of water usage records
        fertilizer_usage: List of fertilizer usage records
        start_date: Start date of the report period
        end_date: End date of the report period
        
    Returns:
        Dictionary with resource usage analysis
    """
    # Calculate total water usage
    total_water = sum(record['amount'] for record in water_usage)
    
    # Calculate total fertilizer usage
    total_fertilizer = sum(record['amount'] for record in fertilizer_usage)
    
    # Calculate averages per hectare
    area_size = crop_data.get('area_size', 1.0)
    water_per_hectare = total_water / area_size if area_size > 0 else 0
    fertilizer_per_hectare = total_fertilizer / area_size if area_size > 0 else 0
    
    # Generate benchmarks based on crop type (simplified)
    crop_type = crop_data.get('crop_type', 'Unknown')
    
    water_benchmark = {
        "Maize": 5000000,  # 5000 cubic meters per hectare per season
        "Tomatoes": 7000000,
        "Beans": 4000000,
        "Cassava": 6000000,
        "Sweet Potato": 5000000
    }.get(crop_type, 5000000)
    
    fertilizer_benchmark = {
        "Maize": 300,  # 300 kg per hectare per season
        "Tomatoes": 500,
        "Beans": 200,
        "Cassava": 250,
        "Sweet Potato": 200
    }.get(crop_type, 300)
    
    # Calculate efficiency percentages
    water_efficiency = min(100, max(0, (water_benchmark / water_per_hectare) * 100)) if water_per_hectare > 0 else 0
    fertilizer_efficiency = min(100, max(0, (fertilizer_benchmark / fertilizer_per_hectare) * 100)) if fertilizer_per_hectare > 0 else 0
    
    # Generate recommendations
    recommendations = []
    
    if water_efficiency < 60:
        recommendations.append({
            "resource": "Water",
            "action": "Consider implementing water conservation techniques such as mulching and drip irrigation.",
            "potential_saving": f"{round((1 - water_efficiency/100) * 100)}%"
        })
    
    if fertilizer_efficiency < 60:
        recommendations.append({
            "resource": "Fertilizer",
            "action": "Consider soil testing and precision application to reduce fertilizer usage.",
            "potential_saving": f"{round((1 - fertilizer_efficiency/100) * 100)}%"
        })
    
    # Compile report
    report = {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "total_usage": {
            "water": total_water,
            "water_per_hectare": water_per_hectare,
            "fertilizer": total_fertilizer,
            "fertilizer_per_hectare": fertilizer_per_hectare
        },
        "efficiency": {
            "water": round(water_efficiency),
            "fertilizer": round(fertilizer_efficiency),
            "overall": round((water_efficiency + fertilizer_efficiency) / 2)
        },
        "benchmarks": {
            "water": water_benchmark,
            "fertilizer": fertilizer_benchmark
        },
        "recommendations": recommendations
    }
    
    return report
