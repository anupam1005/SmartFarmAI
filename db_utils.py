from datetime import datetime, timedelta
from database import get_session, Farm, Field, HealthRecord, Recommendation, PestDetection, Activity, Resource, ResourceUsage, WeatherRecord, CropRecommendation
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Farm operations
def get_farm_by_id(farm_id):
    """Get a farm by ID"""
    try:
        session = get_session()
        farm = session.query(Farm).filter(Farm.id == farm_id).first()
        session.close()
        return farm
    except Exception as e:
        logger.error(f"Error getting farm by ID {farm_id}: {e}")
        return None

def get_farm_by_name(name):
    """Get a farm by name"""
    try:
        session = get_session()
        farm = session.query(Farm).filter(Farm.name == name).first()
        session.close()
        return farm
    except Exception as e:
        logger.error(f"Error getting farm by name '{name}': {e}")
        return None

def create_farm(name, location=None, area_size=None):
    """Create a new farm"""
    try:
        session = get_session()
        farm = Farm(name=name, location=location, area_size=area_size)
        session.add(farm)
        session.commit()
        farm_id = farm.id
        session.close()
        return farm_id
    except Exception as e:
        logger.error(f"Error creating farm '{name}': {e}")
        return None

def update_farm(farm_id, name=None, location=None, area_size=None):
    """Update farm details"""
    try:
        session = get_session()
        farm = session.query(Farm).filter(Farm.id == farm_id).first()
        
        if farm:
            if name:
                farm.name = name
            if location is not None:
                farm.location = location
            if area_size is not None:
                farm.area_size = area_size
                
            farm.updated_at = datetime.now()
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error updating farm {farm_id}: {e}")
        return False

def delete_farm(farm_id):
    """Delete a farm and all related records"""
    try:
        session = get_session()
        farm = session.query(Farm).filter(Farm.id == farm_id).first()
        
        if farm:
            session.delete(farm)
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error deleting farm {farm_id}: {e}")
        return False

def get_all_farms():
    """Get all farms"""
    try:
        session = get_session()
        farms = session.query(Farm).all()
        session.close()
        return farms
    except Exception as e:
        logger.error(f"Error getting all farms: {e}")
        return []

# Field operations
def get_field_by_id(field_id):
    """Get a field by ID"""
    try:
        session = get_session()
        field = session.query(Field).filter(Field.id == field_id).first()
        session.close()
        return field
    except Exception as e:
        logger.error(f"Error getting field by ID {field_id}: {e}")
        return None

def get_fields_by_farm(farm_id):
    """Get all fields for a farm"""
    try:
        session = get_session()
        fields = session.query(Field).filter(Field.farm_id == farm_id).all()
        session.close()
        return fields
    except Exception as e:
        logger.error(f"Error getting fields for farm {farm_id}: {e}")
        return []

def create_field(farm_id, name, area_size=None, soil_type=None, current_crop=None, 
                 planting_date=None, expected_harvest_date=None):
    """Create a new field"""
    try:
        session = get_session()
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
        field_id = field.id
        session.close()
        return field_id
    except Exception as e:
        logger.error(f"Error creating field '{name}' for farm {farm_id}: {e}")
        return None

def update_field(field_id, name=None, area_size=None, soil_type=None, 
                 current_crop=None, planting_date=None, expected_harvest_date=None):
    """Update field details"""
    try:
        session = get_session()
        field = session.query(Field).filter(Field.id == field_id).first()
        
        if field:
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
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error updating field {field_id}: {e}")
        return False

def delete_field(field_id):
    """Delete a field and all related records"""
    try:
        session = get_session()
        field = session.query(Field).filter(Field.id == field_id).first()
        
        if field:
            session.delete(field)
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error deleting field {field_id}: {e}")
        return False

# Health record operations
def save_health_record(field_id, health_score, health_status, green_percentage, 
                       yellow_percentage, brown_percentage, nitrogen_status,
                       phosphorus_status, potassium_status, notes=None, image_path=None):
    """Save a new health record for a field"""
    try:
        session = get_session()
        health_record = HealthRecord(
            field_id=field_id,
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
        session.add(health_record)
        session.commit()
        health_record_id = health_record.id
        session.close()
        return health_record_id
    except Exception as e:
        logger.error(f"Error saving health record for field {field_id}: {e}")
        return None

def get_health_records_by_field(field_id, limit=10):
    """Get health records for a field"""
    try:
        session = get_session()
        records = session.query(HealthRecord).filter(
            HealthRecord.field_id == field_id
        ).order_by(HealthRecord.date.desc()).limit(limit).all()
        session.close()
        return records
    except Exception as e:
        logger.error(f"Error getting health records for field {field_id}: {e}")
        return []

def get_latest_health_record(field_id):
    """Get the most recent health record for a field"""
    try:
        session = get_session()
        record = session.query(HealthRecord).filter(
            HealthRecord.field_id == field_id
        ).order_by(HealthRecord.date.desc()).first()
        session.close()
        return record
    except Exception as e:
        logger.error(f"Error getting latest health record for field {field_id}: {e}")
        return None

# Recommendation operations
def save_recommendation(health_record_id, text):
    """Save a recommendation for a health record"""
    try:
        session = get_session()
        recommendation = Recommendation(
            health_record_id=health_record_id,
            text=text
        )
        session.add(recommendation)
        session.commit()
        recommendation_id = recommendation.id
        session.close()
        return recommendation_id
    except Exception as e:
        logger.error(f"Error saving recommendation for health record {health_record_id}: {e}")
        return None

def get_recommendations_by_health_record(health_record_id):
    """Get recommendations for a health record"""
    try:
        session = get_session()
        recommendations = session.query(Recommendation).filter(
            Recommendation.health_record_id == health_record_id
        ).all()
        session.close()
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations for health record {health_record_id}: {e}")
        return []

def mark_recommendation_implemented(recommendation_id):
    """Mark a recommendation as implemented"""
    try:
        session = get_session()
        recommendation = session.query(Recommendation).filter(
            Recommendation.id == recommendation_id
        ).first()
        
        if recommendation:
            recommendation.implemented = True
            recommendation.implementation_date = datetime.now()
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error marking recommendation {recommendation_id} as implemented: {e}")
        return False

# Pest detection operations
def save_pest_detection(field_id, detected_class, confidence, severity, 
                        description, treatment_recommendation, image_path=None):
    """Save a pest detection record"""
    try:
        session = get_session()
        detection = PestDetection(
            field_id=field_id,
            detected_class=detected_class,
            confidence=confidence,
            severity=severity,
            description=description,
            treatment_recommendation=treatment_recommendation,
            image_path=image_path
        )
        session.add(detection)
        session.commit()
        detection_id = detection.id
        session.close()
        return detection_id
    except Exception as e:
        logger.error(f"Error saving pest detection for field {field_id}: {e}")
        return None

def get_pest_detections_by_field(field_id, limit=10):
    """Get pest detections for a field"""
    try:
        session = get_session()
        detections = session.query(PestDetection).filter(
            PestDetection.field_id == field_id
        ).order_by(PestDetection.date.desc()).limit(limit).all()
        session.close()
        return detections
    except Exception as e:
        logger.error(f"Error getting pest detections for field {field_id}: {e}")
        return []

def get_detection_history(field_id=None, limit=10):
    """Get pest detection history, optionally filtered by field"""
    try:
        session = get_session()
        query = session.query(PestDetection)
        
        if field_id:
            query = query.filter(PestDetection.field_id == field_id)
            
        detections = query.order_by(PestDetection.date.desc()).limit(limit).all()
        session.close()
        return detections
    except Exception as e:
        field_str = f"field {field_id}" if field_id else "all fields"
        logger.error(f"Error getting pest detection history for {field_str}: {e}")
        return []

# Activity operations
def record_activity(farm_id, activity_type, description=None, status="Pending"):
    """Record a farm activity"""
    try:
        session = get_session()
        activity = Activity(
            farm_id=farm_id,
            activity_type=activity_type,
            description=description,
            status=status
        )
        session.add(activity)
        session.commit()
        activity_id = activity.id
        session.close()
        return activity_id
    except Exception as e:
        logger.error(f"Error recording activity for farm {farm_id}: {e}")
        return None

def get_recent_activities(farm_id, limit=10):
    """Get recent activities for a farm"""
    try:
        session = get_session()
        activities = session.query(Activity).filter(
            Activity.farm_id == farm_id
        ).order_by(Activity.date.desc()).limit(limit).all()
        session.close()
        return activities
    except Exception as e:
        logger.error(f"Error getting recent activities for farm {farm_id}: {e}")
        return []

def update_activity_status(activity_id, new_status):
    """Update the status of an activity"""
    try:
        session = get_session()
        activity = session.query(Activity).filter(Activity.id == activity_id).first()
        
        if activity:
            activity.status = new_status
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error updating status for activity {activity_id}: {e}")
        return False

# Resource operations
def add_resource(farm_id, name, type, quantity, unit):
    """Add a new resource to a farm"""
    try:
        session = get_session()
        resource = Resource(
            farm_id=farm_id,
            name=name,
            type=type,
            quantity=quantity,
            unit=unit
        )
        session.add(resource)
        session.commit()
        resource_id = resource.id
        session.close()
        return resource_id
    except Exception as e:
        logger.error(f"Error adding resource '{name}' to farm {farm_id}: {e}")
        return None

def get_resources_by_farm(farm_id):
    """Get all resources for a farm"""
    try:
        session = get_session()
        resources = session.query(Resource).filter(Resource.farm_id == farm_id).all()
        session.close()
        return resources
    except Exception as e:
        logger.error(f"Error getting resources for farm {farm_id}: {e}")
        return []

def get_resources_by_type(farm_id, resource_type):
    """Get resources of a specific type for a farm"""
    try:
        session = get_session()
        resources = session.query(Resource).filter(
            Resource.farm_id == farm_id,
            Resource.type == resource_type
        ).all()
        session.close()
        return resources
    except Exception as e:
        logger.error(f"Error getting {resource_type} resources for farm {farm_id}: {e}")
        return []

def update_resource_quantity(resource_id, new_quantity):
    """Update the quantity of a resource"""
    try:
        session = get_session()
        resource = session.query(Resource).filter(Resource.id == resource_id).first()
        
        if resource:
            resource.quantity = new_quantity
            resource.last_updated = datetime.now()
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error updating quantity for resource {resource_id}: {e}")
        return False

def record_resource_usage(resource_id, field_id, quantity, application_method=None, notes=None):
    """Record usage of a resource on a field"""
    try:
        session = get_session()
        usage = ResourceUsage(
            resource_id=resource_id,
            field_id=field_id,
            quantity=quantity,
            application_method=application_method,
            notes=notes
        )
        session.add(usage)
        session.commit()
        usage_id = usage.id
        session.close()
        return usage_id
    except Exception as e:
        logger.error(f"Error recording usage of resource {resource_id} on field {field_id}: {e}")
        return None

def get_resource_usage_by_field(field_id, start_date=None, end_date=None):
    """Get resource usage records for a field within a date range"""
    try:
        session = get_session()
        query = session.query(ResourceUsage).filter(ResourceUsage.field_id == field_id)
        
        if start_date:
            query = query.filter(ResourceUsage.date >= start_date)
        if end_date:
            query = query.filter(ResourceUsage.date <= end_date)
            
        usages = query.order_by(ResourceUsage.date.desc()).all()
        session.close()
        return usages
    except Exception as e:
        logger.error(f"Error getting resource usage for field {field_id}: {e}")
        return []

def get_resource_usage_stats(farm_id, resource_type=None, days=30):
    """Get statistics on resource usage for a farm over a period"""
    try:
        session = get_session()
        start_date = datetime.now() - timedelta(days=days)
        
        # Build the query
        query = session.query(ResourceUsage).\
            join(Resource, ResourceUsage.resource_id == Resource.id).\
            filter(Resource.farm_id == farm_id).\
            filter(ResourceUsage.date >= start_date)
        
        if resource_type:
            query = query.filter(Resource.type == resource_type)
            
        usages = query.order_by(ResourceUsage.date.desc()).all()
        session.close()
        return usages
    except Exception as e:
        logger.error(f"Error getting resource usage stats for farm {farm_id}: {e}")
        return []

# Weather operations
def save_weather_record(location, temperature, humidity, precipitation, 
                       wind_speed, wind_direction, condition):
    """Save a weather record"""
    try:
        session = get_session()
        weather = WeatherRecord(
            location=location,
            temperature=temperature,
            humidity=humidity,
            precipitation=precipitation,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            condition=condition
        )
        session.add(weather)
        session.commit()
        weather_id = weather.id
        session.close()
        return weather_id
    except Exception as e:
        logger.error(f"Error saving weather record for {location}: {e}")
        return None

def get_weather_history(location, days=30):
    """Get weather history for a location"""
    try:
        session = get_session()
        start_date = datetime.now() - timedelta(days=days)
        
        records = session.query(WeatherRecord).filter(
            WeatherRecord.location == location,
            WeatherRecord.date >= start_date
        ).order_by(WeatherRecord.date.desc()).all()
        
        session.close()
        return records
    except Exception as e:
        logger.error(f"Error getting weather history for {location}: {e}")
        return []

def get_latest_weather(location):
    """Get the latest weather record for a location"""
    try:
        session = get_session()
        record = session.query(WeatherRecord).filter(
            WeatherRecord.location == location
        ).order_by(WeatherRecord.date.desc()).first()
        
        session.close()
        return record
    except Exception as e:
        logger.error(f"Error getting latest weather for {location}: {e}")
        return None

# Crop recommendation operations
def save_crop_recommendation(farm_id, crop, suitability, growing_season, time_to_harvest, 
                           water_requirements, fertilizer_needs, market_demand, 
                           estimated_yield, price_trend, investment_level, 
                           rationale, cultivation_tips, risks=None):
    """Save a crop recommendation"""
    try:
        session = get_session()
        recommendation = CropRecommendation(
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
            risks=risks
        )
        session.add(recommendation)
        session.commit()
        recommendation_id = recommendation.id
        session.close()
        return recommendation_id
    except Exception as e:
        logger.error(f"Error saving crop recommendation for farm {farm_id}: {e}")
        return None

def get_crop_recommendations_by_farm(farm_id, limit=10):
    """Get crop recommendations for a farm"""
    try:
        session = get_session()
        recommendations = session.query(CropRecommendation).filter(
            CropRecommendation.farm_id == farm_id
        ).order_by(CropRecommendation.date.desc()).limit(limit).all()
        
        session.close()
        return recommendations
    except Exception as e:
        logger.error(f"Error getting crop recommendations for farm {farm_id}: {e}")
        return []

def mark_crop_recommendation_implemented(recommendation_id):
    """Mark a crop recommendation as implemented"""
    try:
        session = get_session()
        recommendation = session.query(CropRecommendation).filter(
            CropRecommendation.id == recommendation_id
        ).first()
        
        if recommendation:
            recommendation.implemented = True
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        logger.error(f"Error marking crop recommendation {recommendation_id} as implemented: {e}")
        return False

# Demo data setup
def setup_demo_farm():
    """Create a demo farm if none exists"""
    try:
        session = get_session()
        
        # Check if any farm exists
        farm_count = session.query(Farm).count()
        
        if farm_count == 0:
            # Create demo farm
            demo_farm = Farm(
                name="Green Valley Farm",
                location="Countryside, CA",
                area_size=25.5
            )
            session.add(demo_farm)
            session.flush()  # Flush to get the farm ID
            
            # Create demo fields
            fields = [
                Field(
                    farm_id=demo_farm.id,
                    name="North Field",
                    area_size=8.2,
                    soil_type="Clay Loam",
                    current_crop="Maize",
                    planting_date=datetime.now() - timedelta(days=45),
                    expected_harvest_date=datetime.now() + timedelta(days=55)
                ),
                Field(
                    farm_id=demo_farm.id,
                    name="South Field",
                    area_size=7.3,
                    soil_type="Sandy Loam",
                    current_crop="Wheat",
                    planting_date=datetime.now() - timedelta(days=65),
                    expected_harvest_date=datetime.now() + timedelta(days=40)
                ),
                Field(
                    farm_id=demo_farm.id,
                    name="East Field",
                    area_size=5.5,
                    soil_type="Loam",
                    current_crop="Soybeans",
                    planting_date=datetime.now() - timedelta(days=30),
                    expected_harvest_date=datetime.now() + timedelta(days=65)
                )
            ]
            
            session.add_all(fields)
            session.flush()
            
            # Create demo resources
            resources = [
                Resource(
                    farm_id=demo_farm.id,
                    name="Water Reservoir",
                    type="Water",
                    quantity=50000,
                    unit="liters"
                ),
                Resource(
                    farm_id=demo_farm.id,
                    name="NPK Fertilizer",
                    type="Fertilizer",
                    quantity=500,
                    unit="kg"
                ),
                Resource(
                    farm_id=demo_farm.id,
                    name="Maize Seeds",
                    type="Seeds",
                    quantity=150,
                    unit="kg"
                ),
                Resource(
                    farm_id=demo_farm.id,
                    name="Wheat Seeds",
                    type="Seeds",
                    quantity=180,
                    unit="kg"
                ),
                Resource(
                    farm_id=demo_farm.id,
                    name="Organic Pesticide",
                    type="Pesticide",
                    quantity=75,
                    unit="liters"
                )
            ]
            
            session.add_all(resources)
            
            # Create some activities
            activities = [
                Activity(
                    farm_id=demo_farm.id,
                    activity_type="Planting",
                    description="Planted maize in North Field",
                    status="Completed",
                    date=datetime.now() - timedelta(days=45)
                ),
                Activity(
                    farm_id=demo_farm.id,
                    activity_type="Fertilization",
                    description="Applied NPK fertilizer to South Field",
                    status="Completed",
                    date=datetime.now() - timedelta(days=30)
                ),
                Activity(
                    farm_id=demo_farm.id,
                    activity_type="Irrigation",
                    description="Irrigated East Field",
                    status="Completed",
                    date=datetime.now() - timedelta(days=15)
                ),
                Activity(
                    farm_id=demo_farm.id,
                    activity_type="Pest Control",
                    description="Check for pests in all fields",
                    status="Pending",
                    date=datetime.now() + timedelta(days=5)
                ),
                Activity(
                    farm_id=demo_farm.id,
                    activity_type="Harvesting",
                    description="Harvest wheat in South Field",
                    status="Pending",
                    date=datetime.now() + timedelta(days=40)
                )
            ]
            
            session.add_all(activities)
            
            # Add health records for fields
            health_records = []
            for field in fields:
                health_score = random.randint(65, 95)
                health_status = "Healthy" if health_score >= 80 else "Moderate Stress"
                
                green_percentage = health_score * 0.8
                yellow_percentage = (100 - green_percentage) * 0.7
                brown_percentage = 100 - green_percentage - yellow_percentage
                
                record = HealthRecord(
                    field_id=field.id,
                    health_score=health_score,
                    health_status=health_status,
                    green_percentage=green_percentage,
                    yellow_percentage=yellow_percentage,
                    brown_percentage=brown_percentage,
                    nitrogen_status="Adequate" if health_score > 75 else "Deficient",
                    phosphorus_status="Adequate",
                    potassium_status="Adequate" if health_score > 70 else "Deficient",
                    notes="Regular monitoring check"
                )
                
                health_records.append(record)
            
            session.add_all(health_records)
            
            # Add weather records
            today = datetime.now()
            weather_records = []
            
            for i in range(10):
                day = today - timedelta(days=i)
                temp_base = 25 if i % 2 == 0 else 23
                temp_variation = random.uniform(-3, 3)
                
                record = WeatherRecord(
                    date=day,
                    location="Countryside, CA",
                    temperature=temp_base + temp_variation,
                    humidity=random.uniform(50, 80),
                    precipitation=random.uniform(0, 15) if i % 3 == 0 else 0,
                    wind_speed=random.uniform(5, 20),
                    wind_direction=random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                    condition=random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Rain"])
                )
                
                weather_records.append(record)
            
            session.add_all(weather_records)
            
            # Commit all demo data
            session.commit()
            logger.info("Demo farm data created successfully")
        
        session.close()
        return True
    except Exception as e:
        logger.error(f"Error setting up demo farm: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

# Missing import at the top
import random