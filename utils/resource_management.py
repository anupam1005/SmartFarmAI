import random
import math
from datetime import datetime, timedelta

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
    # Base water requirements in mm per day for different crops
    # These are simplified values for demonstration
    base_requirements = {
        "Maize": 6.0,
        "Rice": 10.0,
        "Wheat": 5.0,
        "Soybeans": 6.5,
        "Tomatoes": 7.0,
        "Potatoes": 5.5,
        "Beans": 4.5,
        "Cotton": 7.0,
        "Sunflower": 5.5,
        "Cassava": 4.0,
        "Default": 6.0  # Default value for crops not in the list
    }
    
    # Growth stage factors
    # Different growth stages have different water requirements
    stage_factors = {
        "Germination": 0.5,
        "Vegetative": 0.8,
        "Flowering": 1.2,
        "Yield Formation": 1.0,
        "Ripening": 0.6,
        "Default": 0.8  # Default value
    }
    
    # Soil type factors
    # Different soils retain water differently
    soil_factors = {
        "Clay": 0.8,  # Clay retains water well
        "Clay Loam": 0.85,
        "Loam": 1.0,  # Baseline
        "Sandy Loam": 1.2,
        "Sandy": 1.5,  # Sandy soils require more water
        "Silt Loam": 0.9,
        "Default": 1.0  # Default value
    }
    
    # Get base requirement for the crop or use default
    base_req = base_requirements.get(crop_type, base_requirements["Default"])
    
    # Get factor for growth stage or use default
    stage_factor = stage_factors.get(growth_stage, stage_factors["Default"])
    
    # Get factor for soil type or use default
    soil_factor = soil_factors.get(soil_type, soil_factors["Default"])
    
    # Temperature adjustment (higher temperatures increase water needs)
    temp_factor = 1.0
    if temperature > 30:
        temp_factor = 1.3
    elif temperature > 25:
        temp_factor = 1.2
    elif temperature > 20:
        temp_factor = 1.1
    elif temperature < 10:
        temp_factor = 0.8
    
    # Calculate daily water requirement in mm
    daily_req_mm = base_req * stage_factor * soil_factor * temp_factor
    
    # Adjust for recent rainfall
    effective_rainfall = min(rainfall, daily_req_mm)  # Only count rainfall up to the daily requirement
    adjusted_req_mm = max(0, daily_req_mm - effective_rainfall)
    
    # Convert to liters per hectare per day
    # 1 mm of water on 1 hectare = 10,000 liters
    liters_per_ha = adjusted_req_mm * 10000
    
    # Calculate total requirement for the area
    total_liters = liters_per_ha * area_size
    
    return round(total_liters)

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
    # Base nutrient requirements in kg/ha for different crops
    # Format: (N, P, K) - Nitrogen, Phosphorus, Potassium
    base_requirements = {
        "Maize": {"N": 180, "P": 80, "K": 100},
        "Rice": {"N": 150, "P": 60, "K": 80},
        "Wheat": {"N": 120, "P": 60, "K": 60},
        "Soybeans": {"N": 20, "P": 60, "K": 80},  # Soybeans fix their own nitrogen
        "Tomatoes": {"N": 200, "P": 150, "K": 250},
        "Potatoes": {"N": 180, "P": 100, "K": 220},
        "Beans": {"N": 50, "P": 100, "K": 100},
        "Cotton": {"N": 120, "P": 80, "K": 80},
        "Sunflower": {"N": 100, "P": 50, "K": 100},
        "Cassava": {"N": 80, "P": 40, "K": 120},
        "Default": {"N": 120, "P": 60, "K": 80}
    }
    
    # Growth stage nutrient importance factors
    # Different growth stages need different nutrient ratios
    stage_importance = {
        "Germination": {"N": 0.2, "P": 1.0, "K": 0.3},
        "Vegetative": {"N": 1.0, "P": 0.6, "K": 0.6},
        "Flowering": {"N": 0.7, "P": 0.8, "K": 1.0},
        "Yield Formation": {"N": 0.5, "P": 0.4, "K": 0.8},
        "Ripening": {"N": 0.2, "P": 0.3, "K": 0.5},
        "Default": {"N": 0.7, "P": 0.7, "K": 0.7}
    }
    
    # Get base requirements for the crop
    crop_req = base_requirements.get(crop_type, base_requirements["Default"])
    
    # Get importance factors for the growth stage
    importance = stage_importance.get(growth_stage, stage_importance["Default"])
    
    # Calculate adjusted requirements based on growth stage
    adjusted_req = {
        "N": crop_req["N"] * importance["N"],
        "P": crop_req["P"] * importance["P"],
        "K": crop_req["K"] * importance["K"]
    }
    
    # Adjust for current soil nutrient levels (if provided)
    # Soil nutrients should be in the same units (e.g., kg/ha)
    recommended_application = {}
    
    for nutrient in ["N", "P", "K"]:
        if soil_nutrients and nutrient.lower() in soil_nutrients:
            # Calculate deficiency
            deficiency = max(0, adjusted_req[nutrient] - soil_nutrients[nutrient.lower()])
            recommended_application[nutrient] = deficiency
        else:
            # If no soil test data, use adjusted requirement
            recommended_application[nutrient] = adjusted_req[nutrient]
    
    # Calculate total quantities needed for the given area
    for nutrient in recommended_application:
        recommended_application[nutrient] *= area_size
        recommended_application[nutrient] = round(recommended_application[nutrient], 1)
    
    # Add fertilizer type recommendations
    fertilizer_types = []
    
    if recommended_application["N"] > 0:
        fertilizer_types.append("Nitrogen fertilizer (e.g., Urea or Ammonium Nitrate)")
    
    if recommended_application["P"] > 0:
        fertilizer_types.append("Phosphate fertilizer (e.g., Triple Superphosphate)")
    
    if recommended_application["K"] > 0:
        fertilizer_types.append("Potassium fertilizer (e.g., Potassium Chloride)")
    
    if len(fertilizer_types) > 1:
        fertilizer_types.append("Complete NPK fertilizer (for balanced application)")
    
    # Create the final recommendation
    recommendation = {
        "nutrient_requirements": recommended_application,
        "fertilizer_types": fertilizer_types,
        "application_timing": get_application_timing(growth_stage),
        "notes": get_application_notes(crop_type, growth_stage)
    }
    
    return recommendation

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
    # Convert liters to cubic meters for standard calculations
    water_usage_m3 = water_usage / 1000
    
    # Convert to water usage per hectare
    water_usage_per_ha = water_usage_m3 / area_size if area_size > 0 else water_usage_m3
    
    # Crop yield per hectare
    yield_per_ha = crop_yield / area_size if area_size > 0 else crop_yield
    
    # Calculate water productivity (kg crop per cubic meter of water)
    water_productivity = yield_per_ha / water_usage_per_ha if water_usage_per_ha > 0 else 0
    
    # Benchmark water productivity values for different crops (kg/m³)
    # These are simplified and would be more precise in a real system
    benchmarks = {
        "Maize": 1.8,
        "Rice": 0.7,  # Rice typically has lower water productivity
        "Wheat": 1.2,
        "Soybeans": 1.5,
        "Tomatoes": 12.0,  # Vegetable crops typically have higher values
        "Potatoes": 5.0,
        "Beans": 1.2,
        "Cotton": 0.3,  # Cotton typically has lower water productivity
        "Sunflower": 0.9,
        "Cassava": 3.0,
        "Default": 1.5
    }
    
    # Get benchmark for the crop
    benchmark = benchmarks.get(crop_type, benchmarks["Default"])
    
    # Calculate efficiency ratio (actual/benchmark)
    efficiency_ratio = water_productivity / benchmark if benchmark > 0 else 0
    
    # Convert to a 0-100 score
    # A ratio of 1.0 (meeting benchmark) gives a score of 70
    # A ratio of 1.5 (exceeding benchmark by 50%) gives a score of 100
    # A ratio of 0.5 (50% of benchmark) gives a score of 35
    efficiency_score = min(100, max(0, efficiency_ratio * 70))
    
    return round(efficiency_score)

def get_water_saving_tips():
    """
    Get random water saving tips for farming
    
    Returns:
        A water saving tip
    """
    tips = [
        "Install drip irrigation systems to reduce water usage by up to 60% compared to sprinkler systems.",
        "Water crops during early morning or evening to minimize evaporation losses.",
        "Use soil moisture sensors to optimize irrigation timing and avoid overwatering.",
        "Apply mulch around plants to reduce soil evaporation and weed growth.",
        "Maintain irrigation systems regularly to prevent leaks and ensure uniform water distribution.",
        "Consider deficit irrigation techniques for drought-tolerant crops during non-critical growth stages.",
        "Implement rainwater harvesting systems to collect and store water during rainy seasons.",
        "Plant windbreaks to reduce evaporation caused by wind.",
        "Level fields properly to ensure uniform water distribution and prevent runoff.",
        "Use conservation tillage practices to improve soil structure and water retention.",
        "Choose drought-resistant crop varieties when appropriate for your climate.",
        "Apply compost or organic matter to improve soil water-holding capacity.",
        "Consider precision irrigation technologies that deliver water directly to plant roots.",
        "Monitor weather forecasts to avoid irrigation before expected rainfall.",
        "Recycle water when possible, such as using treated wastewater for appropriate crops."
    ]
    
    return random.choice(tips)

def get_fertilizer_application_tips():
    """
    Get random fertilizer application tips
    
    Returns:
        A fertilizer application tip
    """
    tips = [
        "Apply fertilizers based on soil test results to avoid over or under-application.",
        "Use split application techniques for nitrogen fertilizers to reduce leaching losses.",
        "Apply phosphorus and potassium fertilizers before planting for better utilization.",
        "Consider precision application techniques to target fertilizers directly to plant roots.",
        "Incorporate slow-release fertilizers to provide nutrients over a longer period.",
        "Apply foliar fertilizers during critical growth stages for rapid nutrient uptake.",
        "Maintain proper soil pH for optimal nutrient availability and fertilizer efficiency.",
        "Avoid applying fertilizers before heavy rainfall to prevent runoff and leaching.",
        "Calibrate fertilizer equipment regularly to ensure accurate application rates.",
        "Consider using organic fertilizers to improve soil health and structure.",
        "Apply micronutrients when deficiency symptoms appear or based on soil tests.",
        "Implement crop rotation with legumes to reduce nitrogen fertilizer requirements.",
        "Use fertigation (applying fertilizers through irrigation systems) for efficient nutrient delivery.",
        "Consider variable rate application based on field productivity zones.",
        "Avoid fertilizer applications near waterways to prevent water pollution."
    ]
    
    return random.choice(tips)

def get_application_timing(growth_stage):
    """
    Get fertilizer application timing recommendations based on growth stage
    
    Args:
        growth_stage: Current growth stage of the crop
        
    Returns:
        Timing recommendation
    """
    timing_recommendations = {
        "Germination": "Apply phosphorus (P) fertilizer at or before planting. Limit nitrogen (N) application to starter levels only.",
        "Vegetative": "Apply main nitrogen (N) fertilizers during this stage for maximum vegetative growth. Split into 2-3 applications for better efficiency.",
        "Flowering": "Apply potassium (K) fertilizers to support flowering and early fruit development. Reduce nitrogen to prevent excessive vegetative growth.",
        "Yield Formation": "Apply balanced fertilizers with emphasis on potassium (K) to support yield development. Consider foliar applications for quick nutrient uptake.",
        "Ripening": "Limit fertilizer applications during ripening stage. Focus on micronutrients if deficiencies are observed.",
        "Default": "Apply balanced fertilizers according to soil test results. Split nitrogen applications throughout the growing season."
    }
    
    return timing_recommendations.get(growth_stage, timing_recommendations["Default"])

def get_application_notes(crop_type, growth_stage):
    """
    Get specific fertilizer application notes for a crop at a specific growth stage
    
    Args:
        crop_type: Type of crop
        growth_stage: Current growth stage
        
    Returns:
        Application notes
    """
    # Define notes for specific crop-stage combinations
    specific_notes = {
        ("Maize", "Vegetative"): "Maize has high nitrogen needs during vegetative growth. Consider side-dressing when plants are 30-45 cm tall.",
        ("Rice", "Flowering"): "Apply potassium before panicle initiation for improved grain filling and quality.",
        ("Wheat", "Yield Formation"): "Late nitrogen application can increase protein content in wheat grain for quality improvement.",
        ("Tomatoes", "Flowering"): "Reduce nitrogen and increase potassium and phosphorus during flowering to promote fruit set.",
        ("Potatoes", "Tuber Initiation"): "Apply additional potassium at tuber initiation for improved tuber size and quality.",
        ("Soybeans", "Vegetative"): "Soybeans fix their own nitrogen, focus on phosphorus and potassium applications."
    }
    
    # General notes by crop type
    general_crop_notes = {
        "Maize": "Maize is a heavy nitrogen feeder. Monitor closely for nitrogen deficiency symptoms.",
        "Rice": "Apply nitrogen in multiple splits to improve efficiency in flooded rice systems.",
        "Wheat": "Spring wheat typically requires more nitrogen than winter wheat varieties.",
        "Soybeans": "Inoculate soybean seeds with Rhizobium bacteria for effective nitrogen fixation.",
        "Tomatoes": "Excessive nitrogen can reduce fruit quality and increase foliar diseases.",
        "Potatoes": "Avoid chloride-containing fertilizers which can reduce potato quality.",
        "Beans": "Beans benefit from starter nitrogen despite being a legume crop.",
        "Cotton": "Cotton requires balanced nutrition throughout the growing season.",
        "Sunflower": "Sunflowers are deep-rooted and can utilize nutrients from lower soil profiles.",
        "Cassava": "Cassava can perform well in low-fertility soils but responds to balanced fertilization."
    }
    
    # Get specific note if available
    note = specific_notes.get((crop_type, growth_stage), "")
    
    # Add general crop note if available
    if crop_type in general_crop_notes:
        if note:
            note += " " + general_crop_notes[crop_type]
        else:
            note = general_crop_notes[crop_type]
    
    # Default note if nothing specific is available
    if not note:
        note = "Apply fertilizers according to soil test results and crop requirements. Monitor crop for deficiency symptoms."
    
    return note

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
    # Filter usage records to the report period
    filtered_water = [record for record in water_usage 
                     if start_date <= record['date'] <= end_date]
    
    filtered_fertilizer = [record for record in fertilizer_usage 
                          if start_date <= record['date'] <= end_date]
    
    # Calculate total usage
    total_water = sum(record['quantity'] for record in filtered_water)
    total_fertilizer = sum(record['quantity'] for record in filtered_fertilizer)
    
    # Calculate usage per hectare
    area_size = crop_data.get('area_size', 1)  # Default to 1 ha if not provided
    water_per_ha = total_water / area_size if area_size > 0 else 0
    fertilizer_per_ha = total_fertilizer / area_size if area_size > 0 else 0
    
    # Calculate efficiency metrics if yield data is available
    efficiency_metrics = {}
    if 'yield' in crop_data and crop_data['yield'] > 0:
        # Water productivity (kg crop per cubic meter of water)
        water_productivity = (crop_data['yield'] / (total_water / 1000)) if total_water > 0 else 0
        efficiency_metrics['water_productivity'] = round(water_productivity, 2)
        
        # Fertilizer productivity (kg crop per kg fertilizer)
        fertilizer_productivity = crop_data['yield'] / total_fertilizer if total_fertilizer > 0 else 0
        efficiency_metrics['fertilizer_productivity'] = round(fertilizer_productivity, 2)
    
    # Generate usage patterns (simplified)
    usage_patterns = {
        'water_usage_pattern': analyze_usage_pattern(filtered_water),
        'fertilizer_usage_pattern': analyze_usage_pattern(filtered_fertilizer)
    }
    
    # Generate recommendations
    recommendations = []
    
    # Water recommendations
    if 'water_usage_pattern' in usage_patterns:
        pattern = usage_patterns['water_usage_pattern']
        if pattern == 'Irregular':
            recommendations.append("Water application is irregular. Consider implementing a more consistent irrigation schedule.")
        elif pattern == 'Increasing':
            recommendations.append("Water usage is increasing. Check for system inefficiencies or leaks.")
    
    # Add general recommendations
    recommendations.append(get_water_saving_tips())
    recommendations.append(get_fertilizer_application_tips())
    
    # Compile report
    report = {
        'period': {
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': (end_date - start_date).days + 1
        },
        'total_usage': {
            'water': total_water,
            'fertilizer': total_fertilizer
        },
        'usage_per_hectare': {
            'water': round(water_per_ha, 2),
            'fertilizer': round(fertilizer_per_ha, 2)
        },
        'efficiency_metrics': efficiency_metrics,
        'usage_patterns': usage_patterns,
        'recommendations': recommendations
    }
    
    return report

def analyze_usage_pattern(usage_records):
    """
    Analyze the pattern of resource usage over time
    
    Args:
        usage_records: List of usage records with date and quantity
        
    Returns:
        String describing the usage pattern
    """
    if not usage_records or len(usage_records) < 3:
        return "Insufficient data"
    
    # Sort records by date
    sorted_records = sorted(usage_records, key=lambda x: x['date'])
    
    # Calculate trend
    quantities = [record['quantity'] for record in sorted_records]
    n = len(quantities)
    
    # Simple linear regression to detect trend
    # x values are just the indices (0, 1, 2, ...)
    x_values = list(range(n))
    x_mean = sum(x_values) / n
    y_mean = sum(quantities) / n
    
    # Calculate slope of the trend line
    numerator = sum((x_values[i] - x_mean) * (quantities[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator
    
    # Calculate coefficient of determination (R²) to measure consistency
    ss_total = sum((y - y_mean) ** 2 for y in quantities)
    
    if ss_total == 0:
        r_squared = 1
    else:
        y_pred = [x_mean + slope * (x - x_mean) for x in x_values]
        ss_residual = sum((quantities[i] - y_pred[i]) ** 2 for i in range(n))
        r_squared = 1 - (ss_residual / ss_total)
    
    # Determine pattern based on slope and R²
    if r_squared < 0.3:
        return "Irregular"
    elif abs(slope) < 0.05 * y_mean:
        return "Stable"
    elif slope > 0:
        return "Increasing"
    else:
        return "Decreasing"