import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc

from database import (
    get_session, 
    Farm, 
    Field, 
    HealthRecord, 
    Recommendation, 
    PestDetection, 
    Activity, 
    Resource, 
    ResourceUsage, 
    WeatherRecord,
    CropRecommendation
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================================
# Farm Operations
# ==================================

def get_all_farms():
    """Get all farms from the database"""
    try:
        with get_session() as session:
            farms = session.query(Farm).order_by(Farm.name).all()
            return farms
    except Exception as e:
        logger.error(f"Error getting all farms: {e}")
        return []

def get_farm_by_id(farm_id):
    """Get a farm by its ID"""
    try:
        with get_session() as session:
            farm = session.query(Farm).filter(Farm.id == farm_id).first()
            return farm
    except Exception as e:
        logger.error(f"Error getting farm by ID: {e}")
        return None

def add_farm(name, location=None, area_size=None):
    """Add a new farm"""
    try:
        with get_session() as session:
            farm = Farm(
                name=name, 
                location=location, 
                area_size=area_size
            )
            session.add(farm)
            session.commit()
            logger.info(f"Added new farm: {name}")
            return farm.id
    except Exception as e:
        logger.error(f"Error adding farm: {e}")
        return None

def update_farm(farm_id, name=None, location=None, area_size=None):
    """Update farm details"""
    try:
        with get_session() as session:
            farm = session.query(Farm).filter(Farm.id == farm_id).first()
            if not farm:
                return False
            
            if name:
                farm.name = name
            if location is not None:
                farm.location = location
            if area_size is not None:
                farm.area_size = area_size
                
            farm.updated_at = datetime.now()
            session.commit()
            logger.info(f"Updated farm: {farm.name}")
            return True
    except Exception as e:
        logger.error(f"Error updating farm: {e}")
        return False

def delete_farm(farm_id):
    """Delete a farm and all its related data"""
    try:
        with get_session() as session:
            farm = session.query(Farm).filter(Farm.id == farm_id).first()
            if not farm:
                return False
            
            session.delete(farm)
            session.commit()
            logger.info(f"Deleted farm: {farm.name}")
            return True
    except Exception as e:
        logger.error(f"Error deleting farm: {e}")
        return False

# ==================================
# Field Operations
# ==================================

def get_fields_by_farm(farm_id):
    """Get all fields for a farm"""
    try:
        with get_session() as session:
            fields = session.query(Field).filter(Field.farm_id == farm_id).order_by(Field.name).all()
            return fields
    except Exception as e:
        logger.error(f"Error getting fields for farm: {e}")
        return []

def get_field_by_id(field_id):
    """Get a field by its ID"""
    try:
        with get_session() as session:
            field = session.query(Field).filter(Field.id == field_id).first()
            return field
    except Exception as e:
        logger.error(f"Error getting field by ID: {e}")
        return None

def add_field(farm_id, name, area_size=None, soil_type=None, current_crop=None, 
             planting_date=None, expected_harvest_date=None):
    """Add a new field to a farm"""
    try:
        with get_session() as session:
            field = Field(
                farm_id=farm_id,
                name=name,
                area_size=area_size,
                soil_type=soil_type,
                current_crop=current_crop,
                planting_date=planting_date,
                expected_harvest_date=expected_harvest_date
            )
            session.add(field)
            session.commit()
            logger.info(f"Added new field: {name} to farm ID: {farm_id}")
            return field.id
    except Exception as e:
        logger.error(f"Error adding field: {e}")
        return None

def update_field(field_id, name=None, area_size=None, soil_type=None, 
                current_crop=None, planting_date=None, expected_harvest_date=None):
    """Update field details"""
    try:
        with get_session() as session:
            field = session.query(Field).filter(Field.id == field_id).first()
            if not field:
                return False
            
            if name:
                field.name = name
            if area_size is not None:
                field.area_size = area_size
            if soil_type is not None:
                field.soil_type = soil_type
            if current_crop is not None:
                field.current_crop = current_crop
            if planting_date is not None:
                field.planting_date = planting_date
            if expected_harvest_date is not None:
                field.expected_harvest_date = expected_harvest_date
                
            field.updated_at = datetime.now()
            session.commit()
            logger.info(f"Updated field: {field.name}")
            return True
    except Exception as e:
        logger.error(f"Error updating field: {e}")
        return False

def delete_field(field_id):
    """Delete a field and its related data"""
    try:
        with get_session() as session:
            field = session.query(Field).filter(Field.id == field_id).first()
            if not field:
                return False
            
            session.delete(field)
            session.commit()
            logger.info(f"Deleted field: {field.name}")
            return True
    except Exception as e:
        logger.error(f"Error deleting field: {e}")
        return False

def get_fields_count():
    """Get total count of fields"""
    try:
        with get_session() as session:
            count = session.query(func.count(Field.id)).scalar()
            return count
    except Exception as e:
        logger.error(f"Error getting fields count: {e}")
        return 0

# ==================================
# Health Record Operations
# ==================================

def get_health_records_by_field(field_id, limit=None):
    """Get health records for a field, optionally limited to a certain number"""
    try:
        with get_session() as session:
            query = session.query(HealthRecord).filter(HealthRecord.field_id == field_id).order_by(desc(HealthRecord.date))
            
            if limit:
                query = query.limit(limit)
                
            records = query.all()
            return records
    except Exception as e:
        logger.error(f"Error getting health records for field: {e}")
        return []

def add_health_record(field_id, health_score, health_status, green_percentage=None, 
                     yellow_percentage=None, brown_percentage=None, nitrogen_status=None, 
                     phosphorus_status=None, potassium_status=None, notes=None, image_path=None):
    """Add a new health record for a field"""
    try:
        with get_session() as session:
            record = HealthRecord(
                field_id=field_id,
                date=datetime.now(),
                health_score=health_score,
                health_status=health_status,
                green_percentage=green_percentage,
                yellow_percentage=yellow_percentage,
                brown_percentage=brown_percentage,
                nitrogen_status=nitrogen_status,
                phosphorus_status=phosphorus_status,
                potassium_status=potassium_status,
                notes=notes,
                image_path=image_path
            )
            session.add(record)
            session.commit()
            logger.info(f"Added health record for field ID: {field_id}")
            return record.id
    except Exception as e:
        logger.error(f"Error adding health record: {e}")
        return None

def add_recommendation(health_record_id, text):
    """Add a recommendation based on a health record"""
    try:
        with get_session() as session:
            recommendation = Recommendation(
                health_record_id=health_record_id,
                text=text,
                implemented=False
            )
            session.add(recommendation)
            session.commit()
            logger.info(f"Added recommendation for health record ID: {health_record_id}")
            return recommendation.id
    except Exception as e:
        logger.error(f"Error adding recommendation: {e}")
        return None

def mark_recommendation_implemented(recommendation_id):
    """Mark a recommendation as implemented"""
    try:
        with get_session() as session:
            recommendation = session.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
            if not recommendation:
                return False
            
            recommendation.implemented = True
            recommendation.implementation_date = datetime.now()
            session.commit()
            logger.info(f"Marked recommendation ID: {recommendation_id} as implemented")
            return True
    except Exception as e:
        logger.error(f"Error marking recommendation as implemented: {e}")
        return False

def get_health_records_count():
    """Get total count of health records"""
    try:
        with get_session() as session:
            count = session.query(func.count(HealthRecord.id)).scalar()
            return count
    except Exception as e:
        logger.error(f"Error getting health records count: {e}")
        return 0

# ==================================
# Pest Detection Operations
# ==================================

def get_pest_detections_by_field(field_id, limit=None):
    """Get pest detections for a field, optionally limited to a certain number"""
    try:
        with get_session() as session:
            query = session.query(PestDetection).filter(PestDetection.field_id == field_id).order_by(desc(PestDetection.date))
            
            if limit:
                query = query.limit(limit)
                
            detections = query.all()
            return detections
    except Exception as e:
        logger.error(f"Error getting pest detections for field: {e}")
        return []

def save_pest_detection(field_id, detected_class, confidence, severity, description, 
                      treatment_recommendation, image_path=None):
    """Save a pest detection result for a field"""
    try:
        with get_session() as session:
            detection = PestDetection(
                field_id=field_id,
                date=datetime.now(),
                detected_class=detected_class,
                confidence=confidence,
                severity=severity,
                description=description,
                treatment_recommendation=treatment_recommendation,
                image_path=image_path
            )
            session.add(detection)
            session.commit()
            logger.info(f"Saved pest detection for field ID: {field_id}, class: {detected_class}")
            return detection.id
    except Exception as e:
        logger.error(f"Error saving pest detection: {e}")
        return None

def get_detection_history(field_id=None, days=30):
    """Get pest detection history, optionally filtered by field and time period"""
    try:
        with get_session() as session:
            start_date = datetime.now() - timedelta(days=days)
            query = session.query(PestDetection).filter(PestDetection.date >= start_date)
            
            if field_id:
                query = query.filter(PestDetection.field_id == field_id)
                
            query = query.order_by(desc(PestDetection.date))
            detections = query.all()
            return detections
    except Exception as e:
        logger.error(f"Error getting pest detection history: {e}")
        return []

def get_pest_detections_count():
    """Get total count of pest detections"""
    try:
        with get_session() as session:
            count = session.query(func.count(PestDetection.id)).scalar()
            return count
    except Exception as e:
        logger.error(f"Error getting pest detections count: {e}")
        return 0

# ==================================
# Activity Operations
# ==================================

def get_recent_activities(farm_id, limit=10):
    """Get recent activities for a farm"""
    try:
        with get_session() as session:
            activities = session.query(Activity) \
                .filter(Activity.farm_id == farm_id) \
                .order_by(desc(Activity.date)) \
                .limit(limit) \
                .all()
            return activities
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        return []

def add_activity(farm_id, activity_type, description=None, status="Pending"):
    """Add a new activity for a farm"""
    try:
        with get_session() as session:
            activity = Activity(
                farm_id=farm_id,
                date=datetime.now(),
                activity_type=activity_type,
                description=description,
                status=status
            )
            session.add(activity)
            session.commit()
            logger.info(f"Added activity for farm ID: {farm_id}, type: {activity_type}")
            return activity.id
    except Exception as e:
        logger.error(f"Error adding activity: {e}")
        return None

def update_activity_status(activity_id, status):
    """Update the status of an activity"""
    try:
        with get_session() as session:
            activity = session.query(Activity).filter(Activity.id == activity_id).first()
            if not activity:
                return False
            
            activity.status = status
            session.commit()
            logger.info(f"Updated activity ID: {activity_id} status to: {status}")
            return True
    except Exception as e:
        logger.error(f"Error updating activity status: {e}")
        return False

# ==================================
# Resource Operations
# ==================================

def get_resources_by_farm(farm_id):
    """Get all resources for a farm"""
    try:
        with get_session() as session:
            resources = session.query(Resource).filter(Resource.farm_id == farm_id).all()
            return resources
    except Exception as e:
        logger.error(f"Error getting resources for farm: {e}")
        return []

def get_resources_by_type(farm_id, resource_type):
    """Get resources of a specific type for a farm"""
    try:
        with get_session() as session:
            resources = session.query(Resource) \
                .filter(Resource.farm_id == farm_id, Resource.type == resource_type) \
                .all()
            return resources
    except Exception as e:
        logger.error(f"Error getting resources by type: {e}")
        return []

def add_resource(farm_id, name, resource_type, quantity, unit):
    """Add a new resource to a farm"""
    try:
        with get_session() as session:
            resource = Resource(
                farm_id=farm_id,
                name=name,
                type=resource_type,
                quantity=quantity,
                unit=unit,
                last_updated=datetime.now()
            )
            session.add(resource)
            session.commit()
            logger.info(f"Added resource: {name} to farm ID: {farm_id}")
            return resource.id
    except Exception as e:
        logger.error(f"Error adding resource: {e}")
        return None

def update_resource_quantity(resource_id, new_quantity):
    """Update the quantity of a resource"""
    try:
        with get_session() as session:
            resource = session.query(Resource).filter(Resource.id == resource_id).first()
            if not resource:
                return False
            
            resource.quantity = new_quantity
            resource.last_updated = datetime.now()
            session.commit()
            logger.info(f"Updated resource ID: {resource_id} quantity to: {new_quantity}")
            return True
    except Exception as e:
        logger.error(f"Error updating resource quantity: {e}")
        return False

def record_resource_usage(resource_id, field_id, quantity, application_method=None, notes=None):
    """Record usage of a resource on a field"""
    try:
        with get_session() as session:
            usage = ResourceUsage(
                resource_id=resource_id,
                field_id=field_id,
                date=datetime.now(),
                quantity=quantity,
                application_method=application_method,
                notes=notes
            )
            session.add(usage)
            session.commit()
            logger.info(f"Recorded usage of resource ID: {resource_id} on field ID: {field_id}")
            return usage.id
    except Exception as e:
        logger.error(f"Error recording resource usage: {e}")
        return None

def get_resource_usage_by_field(field_id, start_date=None, end_date=None):
    """Get resource usage for a field within a date range"""
    try:
        with get_session() as session:
            query = session.query(ResourceUsage).filter(ResourceUsage.field_id == field_id)
            
            if start_date:
                query = query.filter(ResourceUsage.date >= start_date)
            if end_date:
                query = query.filter(ResourceUsage.date <= end_date)
                
            query = query.order_by(desc(ResourceUsage.date))
            usages = query.all()
            return usages
    except Exception as e:
        logger.error(f"Error getting resource usage by field: {e}")
        return []

def get_resource_usage_stats(farm_id, resource_type=None, days=30):
    """Get resource usage statistics for a farm"""
    # This would typically be a complex query with aggregates
    # Simplified implementation for demonstration
    try:
        stats = {
            'total_usage': 0,
            'daily_avg': 0,
            'usage_change': 0,
            'trend': 0,
            'usage_by_day': [],
            'usage_by_field': [],
            'efficiency': {},
            'recommendations': []
        }
        
        # Get all fields for this farm
        fields = get_fields_by_farm(farm_id)
        if not fields:
            return stats
        
        field_ids = [field.id for field in fields]
        
        # Calculate date ranges
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Previous period for comparison
        prev_start_date = start_date - timedelta(days=days)
        
        with get_session() as session:
            # Base query for resource usages
            usage_query = session.query(
                ResourceUsage, Resource
            ).join(
                Resource, ResourceUsage.resource_id == Resource.id
            ).filter(
                ResourceUsage.field_id.in_(field_ids),
                ResourceUsage.date >= start_date,
                ResourceUsage.date <= end_date
            )
            
            # Filter by resource type if specified
            if resource_type and resource_type != "All":
                usage_query = usage_query.filter(Resource.type == resource_type)
            
            # Get all usages in current period
            usages = usage_query.all()
            
            # Calculate total usage
            total_usage = sum(usage[0].quantity for usage in usages)
            stats['total_usage'] = total_usage
            
            # Calculate daily average
            if days > 0:
                stats['daily_avg'] = total_usage / days
            
            # Get usage by day
            usage_by_day = {}
            for usage, resource in usages:
                day = usage.date.date()
                if day not in usage_by_day:
                    usage_by_day[day] = 0
                usage_by_day[day] += usage.quantity
            
            # Format for chart
            stats['usage_by_day'] = [
                {'date': str(day), 'quantity': quantity}
                for day, quantity in sorted(usage_by_day.items())
            ]
            
            # Calculate trend (linear regression would be better)
            if len(stats['usage_by_day']) > 1:
                first_day = stats['usage_by_day'][0]['quantity']
                last_day = stats['usage_by_day'][-1]['quantity']
                if first_day > 0:
                    stats['trend'] = (last_day - first_day) / first_day
            
            # Get usage by field
            usage_by_field = {}
            for field in fields:
                usage_by_field[field.id] = {
                    'field_name': field.name,
                    'quantity': 0
                }
            
            for usage, resource in usages:
                if usage.field_id in usage_by_field:
                    usage_by_field[usage.field_id]['quantity'] += usage.quantity
            
            # Format for chart
            stats['usage_by_field'] = [
                {
                    'field_name': data['field_name'],
                    'quantity': data['quantity']
                }
                for field_id, data in usage_by_field.items()
                if data['quantity'] > 0
            ]
            
            # Get previous period for comparison
            prev_usage_query = session.query(
                func.sum(ResourceUsage.quantity)
            ).join(
                Resource, ResourceUsage.resource_id == Resource.id
            ).filter(
                ResourceUsage.field_id.in_(field_ids),
                ResourceUsage.date >= prev_start_date,
                ResourceUsage.date < start_date
            )
            
            if resource_type and resource_type != "All":
                prev_usage_query = prev_usage_query.filter(Resource.type == resource_type)
            
            prev_total_usage = prev_usage_query.scalar() or 0
            
            # Calculate change
            if prev_total_usage > 0:
                stats['usage_change'] = ((total_usage - prev_total_usage) / prev_total_usage) * 100
            
            # Calculate efficiency metrics (simplified)
            for field in fields:
                field_usage = sum(
                    usage[0].quantity for usage in usages 
                    if usage[0].field_id == field.id
                )
                
                if field_usage > 0 and field.area_size and field.area_size > 0:
                    # Usage per hectare
                    usage_per_ha = field_usage / field.area_size
                    
                    # Simplified efficiency score based on usage per hectare
                    # In a real system, this would incorporate yields, soil quality, etc.
                    efficiency_score = 100 - min(100, usage_per_ha * 2)  # Lower usage per ha = higher score
                    
                    stats['efficiency'][field.id] = {
                        'score': efficiency_score,
                        'usage_per_ha': usage_per_ha
                    }
            
            # Generate recommendations (simplified)
            # In a real system, these would be based on much more sophisticated analysis
            if stats['efficiency']:
                # Find fields with low efficiency
                low_efficiency_fields = [
                    (field_id, data) for field_id, data in stats['efficiency'].items()
                    if data['score'] < 60
                ]
                
                # Find fields with high usage per ha
                high_usage_fields = [
                    (field_id, data) for field_id, data in stats['efficiency'].items()
                    if data['usage_per_ha'] > 50  # Threshold depends on resource type
                ]
                
                # Find usage trends
                increasing_trend = stats['trend'] > 0.1
                
                # Generate recommendations
                if low_efficiency_fields:
                    field = get_field_by_id(low_efficiency_fields[0][0])
                    if field:
                        stats['recommendations'].append({
                            'priority': 'High',
                            'issue': f'Low resource efficiency in {field.name}',
                            'recommendation': 'Consider precision application methods to improve resource utilization.'
                        })
                
                if high_usage_fields:
                    field = get_field_by_id(high_usage_fields[0][0])
                    if field:
                        stats['recommendations'].append({
                            'priority': 'Medium',
                            'issue': f'High resource usage in {field.name}',
                            'recommendation': 'Evaluate if usage can be reduced without impacting crop health.'
                        })
                
                if increasing_trend:
                    stats['recommendations'].append({
                        'priority': 'Medium',
                        'issue': 'Increasing resource usage trend',
                        'recommendation': 'Review recent application practices for potential optimization.'
                    })
        
        return stats
    except Exception as e:
        logger.error(f"Error getting resource usage stats: {e}")
        return {
            'total_usage': 0,
            'daily_avg': 0,
            'usage_change': 0,
            'trend': 0
        }

# ==================================
# Weather Operations
# ==================================

def get_latest_weather(location):
    """Get the latest weather record for a location"""
    try:
        with get_session() as session:
            record = session.query(WeatherRecord) \
                .filter(WeatherRecord.location == location) \
                .order_by(desc(WeatherRecord.date)) \
                .first()
            return record
    except Exception as e:
        logger.error(f"Error getting latest weather for location: {e}")
        return None

def get_weather_history(location, days=7):
    """Get weather history for a location"""
    try:
        with get_session() as session:
            start_date = datetime.now() - timedelta(days=days)
            records = session.query(WeatherRecord) \
                .filter(WeatherRecord.location == location, 
                        WeatherRecord.date >= start_date) \
                .order_by(desc(WeatherRecord.date)) \
                .all()
            return records
    except Exception as e:
        logger.error(f"Error getting weather history: {e}")
        return []

def save_weather_record(location, temperature, humidity, precipitation, 
                       wind_speed, wind_direction, condition):
    """Save a weather record"""
    try:
        with get_session() as session:
            record = WeatherRecord(
                date=datetime.now(),
                location=location,
                temperature=temperature,
                humidity=humidity,
                precipitation=precipitation,
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                condition=condition
            )
            session.add(record)
            session.commit()
            logger.info(f"Saved weather record for location: {location}")
            return record.id
    except Exception as e:
        logger.error(f"Error saving weather record: {e}")
        return None

# ==================================
# Crop Recommendation Operations
# ==================================

def get_crop_recommendations_by_farm(farm_id, limit=None):
    """Get crop recommendations for a farm"""
    try:
        with get_session() as session:
            query = session.query(CropRecommendation) \
                .filter(CropRecommendation.farm_id == farm_id) \
                .order_by(desc(CropRecommendation.date))
            
            if limit:
                query = query.limit(limit)
                
            recommendations = query.all()
            return recommendations
    except Exception as e:
        logger.error(f"Error getting crop recommendations: {e}")
        return []

def save_crop_recommendation(farm_id, crop, suitability, growing_season, time_to_harvest,
                           water_requirements, fertilizer_needs, market_demand, estimated_yield,
                           price_trend, investment_level, rationale, cultivation_tips, risks):
    """Save a crop recommendation"""
    try:
        with get_session() as session:
            recommendation = CropRecommendation(
                date=datetime.now(),
                farm_id=farm_id,
                crop=crop,
                suitability=suitability,
                growing_season=growing_season,
                time_to_harvest=time_to_harvest,
                water_requirements=water_requirements,
                fertilizer_needs=fertilizer_needs,
                market_demand=market_demand,
                estimated_yield=estimated_yield,
                price_trend=price_trend,
                investment_level=investment_level,
                rationale=rationale,
                cultivation_tips=cultivation_tips,
                risks=risks,
                implemented=False
            )
            session.add(recommendation)
            session.commit()
            logger.info(f"Saved crop recommendation: {crop} for farm ID: {farm_id}")
            return recommendation.id
    except Exception as e:
        logger.error(f"Error saving crop recommendation: {e}")
        return None

def mark_crop_recommendation_implemented(recommendation_id):
    """Mark a crop recommendation as implemented"""
    try:
        with get_session() as session:
            recommendation = session.query(CropRecommendation) \
                .filter(CropRecommendation.id == recommendation_id) \
                .first()
            
            if not recommendation:
                return False
            
            recommendation.implemented = True
            recommendation.implementation_date = datetime.now()
            session.commit()
            logger.info(f"Marked crop recommendation ID: {recommendation_id} as implemented")
            return True
    except Exception as e:
        logger.error(f"Error marking crop recommendation as implemented: {e}")
        return False