import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_resource_usage_projections(current_resources, usage_history, days_to_project=30):
    """
    Calculate resource usage projections based on historical usage patterns
    
    Args:
        current_resources: Dictionary of {resource_id: {name, type, quantity, unit}}
        usage_history: DataFrame with columns [resource_id, date, quantity]
        days_to_project: Number of days to project into the future
        
    Returns:
        Dictionary with projection results
    """
    if usage_history.empty:
        return {
            "projections": {},
            "depletion_alerts": [],
            "stats": {}
        }
    
    # Group by resource_id and calculate stats
    stats = {}
    projections = {}
    depletion_alerts = []
    
    for resource_id, resource_data in current_resources.items():
        # Filter history for this resource
        resource_history = usage_history[usage_history['resource_id'] == resource_id]
        
        if resource_history.empty:
            continue
        
        # Calculate daily average usage (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_usage = resource_history[resource_history['date'] >= cutoff_date]
        
        if not recent_usage.empty:
            # Calculate average daily usage
            total_usage = recent_usage['quantity'].sum()
            days_span = max((datetime.now() - recent_usage['date'].min()).days, 1)
            daily_avg = total_usage / days_span
            
            # Calculate variability (standard deviation)
            if len(recent_usage) > 1:
                # Group by date to handle multiple usages on the same day
                daily_usage = recent_usage.groupby(recent_usage['date'].dt.date)['quantity'].sum()
                variability = daily_usage.std() if len(daily_usage) > 1 else 0
            else:
                variability = 0
            
            # Project future usage
            current_quantity = resource_data['quantity']
            days_until_depletion = current_quantity / daily_avg if daily_avg > 0 else float('inf')
            projected_quantity = max(0, current_quantity - (daily_avg * days_to_project))
            
            # Create projection data
            projections[resource_id] = {
                'name': resource_data['name'],
                'type': resource_data['type'],
                'current_quantity': current_quantity,
                'unit': resource_data['unit'],
                'daily_usage': daily_avg,
                'projected_quantity': projected_quantity,
                'days_until_depletion': days_until_depletion
            }
            
            # Add depletion alerts
            if 0 < days_until_depletion < 14:  # Alert if depletion within 2 weeks
                depletion_alerts.append({
                    'resource_id': resource_id,
                    'name': resource_data['name'],
                    'days_remaining': days_until_depletion,
                    'current_quantity': current_quantity,
                    'unit': resource_data['unit'],
                    'severity': 'high' if days_until_depletion < 7 else 'medium'
                })
            
            # Store stats
            stats[resource_id] = {
                'daily_avg': daily_avg,
                'variability': variability,
                'total_usage_30d': total_usage,
                'usage_trend': _calculate_usage_trend(resource_history)
            }
    
    return {
        "projections": projections,
        "depletion_alerts": sorted(depletion_alerts, key=lambda x: x['days_remaining']),
        "stats": stats
    }

def _calculate_usage_trend(usage_data, days=30):
    """
    Calculate the trend in resource usage over time
    
    Args:
        usage_data: DataFrame with columns [date, quantity]
        days: Number of days to analyze
        
    Returns:
        Trend value (positive = increasing usage, negative = decreasing usage)
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_data = usage_data[usage_data['date'] >= cutoff_date]
    
    if len(recent_data) < 5:  # Need at least 5 data points for meaningful trend
        return 0
    
    # Group by date
    daily_usage = recent_data.groupby(recent_data['date'].dt.date)['quantity'].sum().reset_index()
    
    if len(daily_usage) < 3:  # Need at least 3 days
        return 0
    
    # Convert dates to numeric (days since first date)
    first_date = daily_usage['date'].min()
    daily_usage['day_num'] = [(d - first_date).days for d in daily_usage['date']]
    
    # Simple linear regression
    x = daily_usage['day_num'].values
    y = daily_usage['quantity'].values
    
    if len(x) < 2 or len(y) < 2:
        return 0
    
    try:
        # Calculate slope using numpy's polyfit
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize slope by average daily usage
        avg_usage = np.mean(y)
        if avg_usage > 0:
            normalized_slope = slope / avg_usage
        else:
            normalized_slope = 0
            
        return normalized_slope
    except Exception as e:
        logger.error(f"Error calculating usage trend: {e}")
        return 0

def calculate_resource_efficiency(resource_usage, yields, field_data):
    """
    Calculate resource utilization efficiency
    
    Args:
        resource_usage: DataFrame with [resource_id, field_id, date, quantity, resource_type]
        yields: DataFrame with [field_id, harvest_date, yield_amount]
        field_data: Dictionary of {field_id: {area_size, crop}}
        
    Returns:
        Dictionary with efficiency metrics
    """
    if resource_usage.empty or yields.empty:
        return {
            "efficiency_metrics": {},
            "field_metrics": {},
            "benchmark_comparison": {}
        }
    
    # Group resource usage by field and type
    field_resource_usage = resource_usage.groupby(['field_id', 'resource_type'])['quantity'].sum().reset_index()
    
    # Calculate metrics for each field
    field_metrics = {}
    overall_metrics = {
        'water_per_hectare': [],
        'fertilizer_per_hectare': [],
        'yield_per_hectare': [],
        'water_per_yield': [],
        'fertilizer_per_yield': []
    }
    
    for field_id, field_info in field_data.items():
        # Extract field area and crop
        area = field_info['area_size']
        crop = field_info['crop']
        
        # Get resource usage for this field
        field_usage = field_resource_usage[field_resource_usage['field_id'] == field_id]
        
        # Get yield for this field
        field_yield = yields[yields['field_id'] == field_id]
        
        if field_usage.empty or field_yield.empty or area <= 0:
            continue
        
        total_yield = field_yield['yield_amount'].sum()
        
        # Initialize metrics for this field
        metrics = {
            'field_id': field_id,
            'crop': crop,
            'area': area,
            'total_yield': total_yield,
            'yield_per_hectare': total_yield / area
        }
        
        # Calculate resource usage per hectare and per yield unit
        for _, row in field_usage.iterrows():
            resource_type = row['resource_type']
            quantity = row['quantity']
            
            usage_per_hectare = quantity / area
            usage_per_yield = quantity / total_yield if total_yield > 0 else float('inf')
            
            metrics[f'{resource_type}_usage'] = quantity
            metrics[f'{resource_type}_per_hectare'] = usage_per_hectare
            metrics[f'{resource_type}_per_yield'] = usage_per_yield
            
            # Add to overall metrics for benchmarking
            if resource_type == 'Water':
                overall_metrics['water_per_hectare'].append(usage_per_hectare)
                overall_metrics['water_per_yield'].append(usage_per_yield)
            elif 'Fertilizer' in resource_type:
                overall_metrics['fertilizer_per_hectare'].append(usage_per_hectare)
                overall_metrics['fertilizer_per_yield'].append(usage_per_yield)
        
        overall_metrics['yield_per_hectare'].append(metrics['yield_per_hectare'])
        field_metrics[field_id] = metrics
    
    # Calculate benchmarks (averages across fields)
    benchmarks = {}
    for metric, values in overall_metrics.items():
        if values:
            benchmarks[metric] = {
                'average': np.mean(values),
                'min': np.min(values),
                'max': np.max(values)
            }
    
    # Compare each field to benchmarks
    benchmark_comparison = {}
    for field_id, metrics in field_metrics.items():
        comparison = {'field_id': field_id}
        
        if 'water_per_hectare' in metrics and 'water_per_hectare' in benchmarks:
            comparison['water_efficiency'] = _calculate_efficiency_score(
                metrics['water_per_hectare'], 
                benchmarks['water_per_hectare']['average'],
                lower_is_better=True
            )
            
        if 'fertilizer_per_hectare' in metrics and 'fertilizer_per_hectare' in benchmarks:
            comparison['fertilizer_efficiency'] = _calculate_efficiency_score(
                metrics['fertilizer_per_hectare'], 
                benchmarks['fertilizer_per_hectare']['average'],
                lower_is_better=True
            )
            
        if 'yield_per_hectare' in metrics and 'yield_per_hectare' in benchmarks:
            comparison['yield_efficiency'] = _calculate_efficiency_score(
                metrics['yield_per_hectare'], 
                benchmarks['yield_per_hectare']['average'],
                lower_is_better=False
            )
            
        benchmark_comparison[field_id] = comparison
    
    return {
        "efficiency_metrics": overall_metrics,
        "field_metrics": field_metrics,
        "benchmark_comparison": benchmark_comparison,
        "benchmarks": benchmarks
    }

def _calculate_efficiency_score(value, benchmark, lower_is_better=True):
    """
    Calculate an efficiency score comparing a value to a benchmark
    
    Args:
        value: The value to evaluate
        benchmark: The benchmark value to compare against
        lower_is_better: Whether a lower value indicates better efficiency
        
    Returns:
        Efficiency score (0-100)
    """
    if benchmark == 0:
        return 50  # Default if benchmark is zero
    
    if lower_is_better:
        # For resources like water or fertilizer, using less is better
        ratio = benchmark / value if value > 0 else 2  # Avoid division by zero
        # Cap at 2x better than benchmark
        ratio = min(ratio, 2)
    else:
        # For yields, higher is better
        ratio = value / benchmark if benchmark > 0 else 2  # Avoid division by zero
        # Cap at 2x better than benchmark
        ratio = min(ratio, 2)
    
    # Convert to 0-100 scale
    # 1.0 (equal to benchmark) = 50
    # 0.5 (half as good) = 25
    # 2.0 (twice as good) = 100
    score = int(50 * ratio)
    
    # Cap between 0 and 100
    return max(0, min(100, score))

def generate_resource_optimization_recommendations(efficiency_data, current_resources, crops_data):
    """
    Generate recommendations for resource optimization
    
    Args:
        efficiency_data: Output from calculate_resource_efficiency
        current_resources: Dictionary of current resource levels
        crops_data: Dictionary with crop requirements
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Extract metrics
    field_metrics = efficiency_data.get('field_metrics', {})
    benchmark_comparison = efficiency_data.get('benchmark_comparison', {})
    
    # Check fields with poor water efficiency
    for field_id, comparison in benchmark_comparison.items():
        metrics = field_metrics.get(field_id, {})
        crop = metrics.get('crop', 'Unknown')
        
        # Water efficiency recommendations
        water_efficiency = comparison.get('water_efficiency', 50)
        if water_efficiency < 40:
            recommendations.append({
                'field_id': field_id,
                'resource_type': 'Water',
                'efficiency_score': water_efficiency,
                'priority': 'High' if water_efficiency < 30 else 'Medium',
                'issue': f"Water usage for {crop} in Field {field_id} is {100-water_efficiency}% higher than average",
                'recommendation': _get_water_optimization_recommendation(crop, crops_data)
            })
        
        # Fertilizer efficiency recommendations
        fertilizer_efficiency = comparison.get('fertilizer_efficiency', 50)
        if fertilizer_efficiency < 40:
            recommendations.append({
                'field_id': field_id,
                'resource_type': 'Fertilizer',
                'efficiency_score': fertilizer_efficiency,
                'priority': 'High' if fertilizer_efficiency < 30 else 'Medium',
                'issue': f"Fertilizer usage for {crop} in Field {field_id} is {100-fertilizer_efficiency}% higher than average",
                'recommendation': _get_fertilizer_optimization_recommendation(crop, crops_data)
            })
        
        # Yield efficiency recommendations
        yield_efficiency = comparison.get('yield_efficiency', 50)
        if yield_efficiency < 40:
            recommendations.append({
                'field_id': field_id,
                'resource_type': 'Yield',
                'efficiency_score': yield_efficiency,
                'priority': 'High' if yield_efficiency < 30 else 'Medium',
                'issue': f"Yield for {crop} in Field {field_id} is {100-yield_efficiency}% lower than average",
                'recommendation': _get_yield_optimization_recommendation(crop, crops_data)
            })
    
    # Check for low resources
    for resource_id, resource in current_resources.items():
        if resource['quantity'] < resource.get('threshold', 0):
            recommendations.append({
                'resource_id': resource_id,
                'resource_type': resource['type'],
                'priority': 'High',
                'issue': f"Low {resource['name']} inventory ({resource['quantity']} {resource['unit']} remaining)",
                'recommendation': f"Restock {resource['name']} soon to prevent shortages that could impact farm operations."
            })
    
    # Sort recommendations by priority
    priority_map = {'High': 0, 'Medium': 1, 'Low': 2}
    recommendations.sort(key=lambda x: priority_map.get(x['priority'], 3))
    
    return recommendations

def _get_water_optimization_recommendation(crop, crops_data):
    """Get water optimization recommendation for a specific crop"""
    crop_info = crops_data.get(crop, {})
    general_tips = [
        "Implement drip irrigation to reduce water usage by 30-50% compared to overhead sprinklers.",
        "Use soil moisture sensors to water only when necessary.",
        "Schedule irrigation during early morning or evening to reduce evaporation.",
        "Apply mulch to reduce soil evaporation and water requirements.",
        "Fix any leaks in irrigation systems promptly."
    ]
    
    specific_tips = crop_info.get('water_optimization_tips', [])
    
    # Combine general and specific tips, prioritizing specific ones
    if specific_tips:
        return specific_tips[0]
    else:
        return general_tips[0]

def _get_fertilizer_optimization_recommendation(crop, crops_data):
    """Get fertilizer optimization recommendation for a specific crop"""
    crop_info = crops_data.get(crop, {})
    general_tips = [
        "Conduct soil tests to determine exact nutrient needs before applying fertilizer.",
        "Use precision application techniques to apply fertilizer only where needed.",
        "Consider split applications of fertilizer throughout the growing season.",
        "Incorporate organic matter to improve soil fertility naturally.",
        "Use slow-release fertilizers to reduce leaching and improve efficiency."
    ]
    
    specific_tips = crop_info.get('fertilizer_optimization_tips', [])
    
    # Combine general and specific tips, prioritizing specific ones
    if specific_tips:
        return specific_tips[0]
    else:
        return general_tips[0]

def _get_yield_optimization_recommendation(crop, crops_data):
    """Get yield optimization recommendation for a specific crop"""
    crop_info = crops_data.get(crop, {})
    general_tips = [
        "Ensure optimal plant spacing to reduce competition and maximize yields.",
        "Implement integrated pest management to minimize crop damage.",
        "Monitor and maintain optimal soil pH for nutrient availability.",
        "Consider foliar feeding to address nutrient deficiencies during critical growth stages.",
        "Improve pollination through management of flowering timing and pollinator habitat."
    ]
    
    specific_tips = crop_info.get('yield_optimization_tips', [])
    
    # Combine general and specific tips, prioritizing specific ones
    if specific_tips:
        return specific_tips[0]
    else:
        return general_tips[0]

def calculate_optimal_resource_allocation(available_resources, field_requirements, priorities=None):
    """
    Calculate optimal allocation of limited resources across fields
    
    Args:
        available_resources: Dictionary of {resource_type: quantity}
        field_requirements: Dictionary of {field_id: {resource_type: ideal_quantity}}
        priorities: Optional dictionary of {field_id: priority_score}
        
    Returns:
        Dictionary with allocation plan
    """
    if not available_resources or not field_requirements:
        return {
            "allocation": {},
            "shortages": {}
        }
    
    # Initialize allocation and shortage tracking
    allocation = {field_id: {} for field_id in field_requirements}
    shortages = {resource_type: 0 for resource_type in available_resources}
    
    # Set default priorities if not provided
    if priorities is None:
        priorities = {field_id: 1 for field_id in field_requirements}
    
    # First pass: Calculate total requirements and identify shortages
    total_requirements = {resource_type: 0 for resource_type in available_resources}
    
    for field_id, requirements in field_requirements.items():
        for resource_type, quantity in requirements.items():
            if resource_type in total_requirements:
                total_requirements[resource_type] += quantity
    
    # Identify resources with shortages
    resource_shortage_pct = {}
    for resource_type, total_required in total_requirements.items():
        available = available_resources.get(resource_type, 0)
        
        if total_required > available and total_required > 0:
            # Calculate shortage percentage
            shortage_pct = 1 - (available / total_required)
            resource_shortage_pct[resource_type] = shortage_pct
            shortages[resource_type] = total_required - available
    
    # Second pass: Allocate resources based on priorities and shortages
    for field_id, requirements in field_requirements.items():
        priority = priorities.get(field_id, 1)
        
        for resource_type, ideal_quantity in requirements.items():
            if resource_type not in available_resources:
                continue
                
            if resource_type in resource_shortage_pct:
                # There's a shortage - allocate proportionally based on priority
                shortage_pct = resource_shortage_pct[resource_type]
                
                # Calculate reduction factor based on priority (higher priority = less reduction)
                # This is a simplified approach - in a real system, this would be more sophisticated
                reduction_factor = shortage_pct * (1 - (priority / max(priorities.values())))
                
                # Ensure reduction is applied but capped
                reduction_factor = min(reduction_factor, 0.9)  # Don't reduce by more than 90%
                
                # Calculate allocated amount
                allocated = ideal_quantity * (1 - reduction_factor)
            else:
                # No shortage - allocate full amount
                allocated = ideal_quantity
            
            allocation[field_id][resource_type] = allocated
    
    # Verify allocations don't exceed available resources
    allocated_totals = {resource_type: 0 for resource_type in available_resources}
    
    for field_allocations in allocation.values():
        for resource_type, quantity in field_allocations.items():
            allocated_totals[resource_type] = allocated_totals.get(resource_type, 0) + quantity
    
    # Adjust if allocations exceed available (shouldn't happen with correct calculations)
    for resource_type, total_allocated in allocated_totals.items():
        available = available_resources.get(resource_type, 0)
        
        if total_allocated > available and total_allocated > 0:
            # Scale down all allocations proportionally
            scale_factor = available / total_allocated
            
            for field_id in allocation:
                if resource_type in allocation[field_id]:
                    allocation[field_id][resource_type] *= scale_factor
    
    return {
        "allocation": allocation,
        "shortages": shortages,
        "total_requirements": total_requirements,
        "allocated_totals": allocated_totals
    }

def calculate_resource_return_on_investment(resource_costs, yield_value, resource_usage, field_data):
    """
    Calculate return on investment for different resources
    
    Args:
        resource_costs: Dictionary of {resource_type: cost_per_unit}
        yield_value: Dictionary of {crop: value_per_unit}
        resource_usage: DataFrame with [field_id, resource_type, quantity]
        field_data: Dictionary of {field_id: {crop, yield_amount, area_size}}
        
    Returns:
        Dictionary with ROI metrics
    """
    if not resource_costs or not yield_value or resource_usage.empty:
        return {
            "field_roi": {},
            "resource_roi": {},
            "overall_roi": 0
        }
    
    # Calculate costs and returns for each field
    field_metrics = {}
    resource_metrics = {resource_type: {'cost': 0, 'contribution': 0} for resource_type in resource_costs}
    total_cost = 0
    total_return = 0
    
    for field_id, field_info in field_data.items():
        # Get crop and yield information
        crop = field_info.get('crop')
        yield_amount = field_info.get('yield_amount', 0)
        
        if not crop or crop not in yield_value or yield_amount <= 0:
            continue
        
        # Calculate return
        crop_return = yield_amount * yield_value[crop]
        
        # Calculate resource costs for this field
        field_usage = resource_usage[resource_usage['field_id'] == field_id]
        field_cost = 0
        resource_costs_by_type = {}
        
        for _, usage_row in field_usage.iterrows():
            resource_type = usage_row['resource_type']
            quantity = usage_row['quantity']
            
            if resource_type in resource_costs:
                cost = quantity * resource_costs[resource_type]
                field_cost += cost
                
                # Store by resource type
                resource_costs_by_type[resource_type] = cost
                
                # Update resource metrics
                resource_metrics[resource_type]['cost'] += cost
        
        # Calculate ROI for this field
        if field_cost > 0:
            field_roi = (crop_return - field_cost) / field_cost
        else:
            field_roi = 0  # No cost, can't calculate ROI
        
        # Store field metrics
        field_metrics[field_id] = {
            'crop': crop,
            'yield_amount': yield_amount,
            'return': crop_return,
            'total_cost': field_cost,
            'resource_costs': resource_costs_by_type,
            'roi': field_roi
        }
        
        # Update totals
        total_cost += field_cost
        total_return += crop_return
        
        # Calculate contribution to return by resource type
        for resource_type, cost in resource_costs_by_type.items():
            # Simple allocation based on cost proportion
            if field_cost > 0:
                contribution_pct = cost / field_cost
                resource_contribution = crop_return * contribution_pct
                resource_metrics[resource_type]['contribution'] += resource_contribution
    
    # Calculate overall ROI
    overall_roi = (total_return - total_cost) / total_cost if total_cost > 0 else 0
    
    # Calculate ROI by resource type
    for resource_type, metrics in resource_metrics.items():
        metrics['roi'] = (metrics['contribution'] - metrics['cost']) / metrics['cost'] if metrics['cost'] > 0 else 0
    
    return {
        "field_roi": field_metrics,
        "resource_roi": resource_metrics,
        "overall_roi": overall_roi,
        "total_cost": total_cost,
        "total_return": total_return
    }

def generate_resource_cost_breakdown(resource_usage, resource_costs, field_data):
    """
    Generate a detailed breakdown of resource costs by field and crop
    
    Args:
        resource_usage: DataFrame with [field_id, resource_type, quantity, date]
        resource_costs: Dictionary of {resource_type: cost_per_unit}
        field_data: Dictionary of {field_id: {crop, area_size}}
        
    Returns:
        Dictionary with cost breakdown
    """
    if resource_usage.empty or not resource_costs:
        return {
            "total_costs": {},
            "cost_by_field": {},
            "cost_by_crop": {},
            "cost_by_month": {}
        }
    
    # Initialize results structure
    total_costs = {resource_type: 0 for resource_type in resource_costs}
    cost_by_field = {}
    cost_by_crop = {}
    cost_by_month = {}
    
    # Process resource usage data
    for _, row in resource_usage.iterrows():
        field_id = row['field_id']
        resource_type = row['resource_type']
        quantity = row['quantity']
        date = row['date']
        
        # Skip if cost data not available
        if resource_type not in resource_costs:
            continue
        
        # Calculate cost
        cost = quantity * resource_costs[resource_type]
        
        # Update total costs
        total_costs[resource_type] += cost
        
        # Update cost by field
        if field_id not in cost_by_field:
            cost_by_field[field_id] = {resource_type: 0 for resource_type in resource_costs}
        cost_by_field[field_id][resource_type] = cost_by_field[field_id].get(resource_type, 0) + cost
        
        # Update cost by crop using field data
        if field_id in field_data:
            crop = field_data[field_id].get('crop')
            if crop:
                if crop not in cost_by_crop:
                    cost_by_crop[crop] = {resource_type: 0 for resource_type in resource_costs}
                cost_by_crop[crop][resource_type] = cost_by_crop[crop].get(resource_type, 0) + cost
        
        # Update cost by month
        month_key = date.strftime('%Y-%m')
        if month_key not in cost_by_month:
            cost_by_month[month_key] = {resource_type: 0 for resource_type in resource_costs}
        cost_by_month[month_key][resource_type] = cost_by_month[month_key].get(resource_type, 0) + cost
    
    # Calculate totals for each breakdown
    for field_id, costs in cost_by_field.items():
        costs['total'] = sum(cost for resource_type, cost in costs.items() if resource_type != 'total')
        
        # Calculate cost per hectare
        if field_id in field_data and field_data[field_id].get('area_size', 0) > 0:
            area = field_data[field_id]['area_size']
            costs['cost_per_hectare'] = costs['total'] / area
    
    for crop, costs in cost_by_crop.items():
        costs['total'] = sum(cost for resource_type, cost in costs.items() if resource_type != 'total')
    
    for month, costs in cost_by_month.items():
        costs['total'] = sum(cost for resource_type, cost in costs.items() if resource_type != 'total')
    
    # Calculate grand total
    grand_total = sum(cost for resource_type, cost in total_costs.items())
    total_costs['total'] = grand_total
    
    return {
        "total_costs": total_costs,
        "cost_by_field": cost_by_field,
        "cost_by_crop": cost_by_crop,
        "cost_by_month": cost_by_month
    }

def analyze_resource_seasonality(resource_usage, years=2):
    """
    Analyze seasonality patterns in resource usage
    
    Args:
        resource_usage: DataFrame with [resource_type, date, quantity]
        years: Number of years of data to analyze
        
    Returns:
        Dictionary with seasonality analysis
    """
    if resource_usage.empty:
        return {
            "seasonal_patterns": {},
            "monthly_averages": {},
            "peak_months": {}
        }
    
    # Filter data for analysis period
    cutoff_date = datetime.now() - timedelta(days=365 * years)
    recent_data = resource_usage[resource_usage['date'] >= cutoff_date]
    
    if recent_data.empty:
        return {
            "seasonal_patterns": {},
            "monthly_averages": {},
            "peak_months": {}
        }
    
    # Group by resource type and month
    recent_data['month'] = recent_data['date'].dt.month
    monthly_usage = recent_data.groupby(['resource_type', 'month'])['quantity'].sum().reset_index()
    
    # Calculate monthly averages
    monthly_averages = {}
    peak_months = {}
    seasonal_patterns = {}
    
    for resource_type in monthly_usage['resource_type'].unique():
        # Filter for this resource type
        resource_data = monthly_usage[monthly_usage['resource_type'] == resource_type]
        
        # Skip if insufficient data
        if len(resource_data) < 6:  # Need at least 6 months for meaningful analysis
            continue
        
        # Calculate monthly averages
        monthly_avg = {}
        for _, row in resource_data.iterrows():
            month = row['month']
            quantity = row['quantity']
            monthly_avg[month] = quantity / years  # Average per year
        
        # Find peak and low usage months
        if monthly_avg:
            max_month = max(monthly_avg, key=monthly_avg.get)
            min_month = min(monthly_avg, key=monthly_avg.get)
            
            monthly_averages[resource_type] = monthly_avg
            peak_months[resource_type] = {'peak': max_month, 'low': min_month}
            
            # Identify seasonal pattern
            pattern = _identify_seasonal_pattern(monthly_avg)
            seasonal_patterns[resource_type] = pattern
    
    return {
        "seasonal_patterns": seasonal_patterns,
        "monthly_averages": monthly_averages,
        "peak_months": peak_months
    }

def _identify_seasonal_pattern(monthly_data):
    """
    Identify the seasonal pattern from monthly data
    
    Args:
        monthly_data: Dictionary of {month: quantity}
        
    Returns:
        Dictionary with pattern description
    """
    if not monthly_data or len(monthly_data) < 6:
        return {"pattern": "Insufficient data"}
    
    # Calculate average
    avg = sum(monthly_data.values()) / len(monthly_data)
    if avg == 0:
        return {"pattern": "No usage"}
    
    # Calculate variation
    variations = {month: (value - avg) / avg for month, value in monthly_data.items()}
    
    # Check for spring peak (months: 3, 4, 5)
    spring_avg = sum(monthly_data.get(m, 0) for m in [3, 4, 5]) / 3
    
    # Check for summer peak (months: 6, 7, 8)
    summer_avg = sum(monthly_data.get(m, 0) for m in [6, 7, 8]) / 3
    
    # Check for fall peak (months: 9, 10, 11)
    fall_avg = sum(monthly_data.get(m, 0) for m in [9, 10, 11]) / 3
    
    # Check for winter peak (months: 12, 1, 2)
    winter_avg = sum(monthly_data.get(m, 0) for m in [12, 1, 2]) / 3
    
    # Determine pattern
    seasonal_avgs = {
        "Spring": spring_avg,
        "Summer": summer_avg,
        "Fall": fall_avg,
        "Winter": winter_avg
    }
    
    peak_season = max(seasonal_avgs, key=seasonal_avgs.get)
    low_season = min(seasonal_avgs, key=seasonal_avgs.get)
    
    # Calculate highest and lowest month
    high_month = max(monthly_data, key=monthly_data.get)
    low_month = min(monthly_data, key=monthly_data.get)
    
    # Calculate peak ratio (high vs average)
    high_value = monthly_data[high_month]
    peak_ratio = high_value / avg
    
    # Calculate seasonal intensity
    if peak_ratio > 2:
        intensity = "Strong"
    elif peak_ratio > 1.5:
        intensity = "Moderate"
    else:
        intensity = "Mild"
    
    return {
        "pattern": f"{intensity} {peak_season} Peak",
        "peak_season": peak_season,
        "low_season": low_season,
        "peak_month": high_month,
        "low_month": low_month,
        "peak_ratio": peak_ratio,
        "variations": variations
    }