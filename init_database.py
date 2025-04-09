import os
import logging
from datetime import datetime, timedelta
import random
from database import init_db, get_session
from db_utils import add_farm, add_field, add_health_record, add_resource, add_activity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default farm data for initialization
DEFAULT_FARMS = [
    {
        "name": "Green Valley Farm",
        "location": "Portland, Oregon",
        "area_size": 25.5,
        "fields": [
            {
                "name": "North Field",
                "area_size": 8.2,
                "soil_type": "Clay Loam",
                "current_crop": "Corn"
            },
            {
                "name": "East Field",
                "area_size": 7.8,
                "soil_type": "Sandy Loam",
                "current_crop": "Wheat"
            },
            {
                "name": "South Field",
                "area_size": 9.5,
                "soil_type": "Loam",
                "current_crop": "Soybeans"
            }
        ],
        "resources": [
            {
                "name": "NPK Fertilizer",
                "type": "Fertilizer - Compound",
                "quantity": 500,
                "unit": "Kilograms"
            },
            {
                "name": "Irrigation Water",
                "type": "Water",
                "quantity": 50000,
                "unit": "Liters"
            },
            {
                "name": "Glyphosate",
                "type": "Pesticide - Herbicide",
                "quantity": 25,
                "unit": "Liters"
            },
            {
                "name": "Corn Seeds",
                "type": "Seeds",
                "quantity": 50,
                "unit": "Kilograms"
            }
        ]
    },
    {
        "name": "Sunny Acres",
        "location": "Sacramento, California",
        "area_size": 18.3,
        "fields": [
            {
                "name": "Orchard Field",
                "area_size": 5.2,
                "soil_type": "Loam",
                "current_crop": "Tomatoes"
            },
            {
                "name": "Valley Field",
                "area_size": 6.8,
                "soil_type": "Sandy Loam",
                "current_crop": "Strawberries"
            },
            {
                "name": "Hill Field",
                "area_size": 6.3,
                "soil_type": "Clay Loam",
                "current_crop": None
            }
        ],
        "resources": [
            {
                "name": "Nitrogen Fertilizer",
                "type": "Fertilizer - Nitrogen",
                "quantity": 300,
                "unit": "Kilograms"
            },
            {
                "name": "Potassium Fertilizer",
                "type": "Fertilizer - Potassium",
                "quantity": 250,
                "unit": "Kilograms"
            },
            {
                "name": "Insecticide",
                "type": "Pesticide - Insecticide",
                "quantity": 15,
                "unit": "Liters"
            },
            {
                "name": "Tomato Seeds",
                "type": "Seeds",
                "quantity": 5,
                "unit": "Kilograms"
            },
            {
                "name": "Irrigation Pipes",
                "type": "Tools",
                "quantity": 20,
                "unit": "Pieces"
            }
        ]
    }
]

# Sample health status data
HEALTH_STATUSES = [
    {
        "health_score": 85,
        "health_status": "Good",
        "green_percentage": 78,
        "yellow_percentage": 15,
        "brown_percentage": 7,
        "nitrogen_status": "Good",
        "phosphorus_status": "Medium",
        "potassium_status": "Good",
        "notes": "Crop shows good health with minimal stress indicators"
    },
    {
        "health_score": 65,
        "health_status": "Fair",
        "green_percentage": 60,
        "yellow_percentage": 30,
        "brown_percentage": 10,
        "nitrogen_status": "Medium",
        "phosphorus_status": "Low",
        "potassium_status": "Medium",
        "notes": "Some yellowing observed, potentially due to phosphorus deficiency"
    },
    {
        "health_score": 92,
        "health_status": "Good",
        "green_percentage": 90,
        "yellow_percentage": 8,
        "brown_percentage": 2,
        "nitrogen_status": "Good",
        "phosphorus_status": "Good",
        "potassium_status": "Good",
        "notes": "Excellent crop health following recent fertilization"
    }
]

# Sample activities
ACTIVITIES = [
    {
        "activity_type": "Planting",
        "description": "Planted corn seeds",
        "status": "Completed"
    },
    {
        "activity_type": "Fertilizing",
        "description": "Applied NPK fertilizer",
        "status": "Completed"
    },
    {
        "activity_type": "Irrigation",
        "description": "Irrigated all fields",
        "status": "Completed"
    },
    {
        "activity_type": "Pest Control",
        "description": "Applied insecticide to tomato crops",
        "status": "Completed"
    },
    {
        "activity_type": "Soil Testing",
        "description": "Collect soil samples for testing",
        "status": "Pending"
    },
    {
        "activity_type": "Harvesting",
        "description": "Prepare for wheat harvest",
        "status": "Pending"
    }
]

def populate_demo_data():
    """Populate database with demo farm data"""
    try:
        # Add farms and their related data
        for farm_data in DEFAULT_FARMS:
            # Add the farm
            farm_id = add_farm(
                name=farm_data["name"],
                location=farm_data["location"],
                area_size=farm_data["area_size"]
            )
            
            if not farm_id:
                logger.error(f"Failed to add farm: {farm_data['name']}")
                continue
                
            logger.info(f"Added farm: {farm_data['name']} with ID: {farm_id}")
            
            # Add fields for this farm
            field_ids = []
            for field_data in farm_data["fields"]:
                field_id = add_field(
                    farm_id=farm_id,
                    name=field_data["name"],
                    area_size=field_data["area_size"],
                    soil_type=field_data["soil_type"],
                    current_crop=field_data["current_crop"]
                )
                
                if field_id:
                    field_ids.append(field_id)
                    logger.info(f"Added field: {field_data['name']} with ID: {field_id}")
                else:
                    logger.error(f"Failed to add field: {field_data['name']}")
            
            # Add resources for this farm
            for resource_data in farm_data["resources"]:
                resource_id = add_resource(
                    farm_id=farm_id,
                    name=resource_data["name"],
                    resource_type=resource_data["type"],
                    quantity=resource_data["quantity"],
                    unit=resource_data["unit"]
                )
                
                if resource_id:
                    logger.info(f"Added resource: {resource_data['name']} with ID: {resource_id}")
                else:
                    logger.error(f"Failed to add resource: {resource_data['name']}")
            
            # Add sample health records
            if field_ids:
                for field_id in field_ids:
                    # Add 1-2 health records per field
                    for _ in range(random.randint(1, 2)):
                        health_data = random.choice(HEALTH_STATUSES)
                        health_record_id = add_health_record(
                            field_id=field_id,
                            health_score=health_data["health_score"],
                            health_status=health_data["health_status"],
                            green_percentage=health_data["green_percentage"],
                            yellow_percentage=health_data["yellow_percentage"],
                            brown_percentage=health_data["brown_percentage"],
                            nitrogen_status=health_data["nitrogen_status"],
                            phosphorus_status=health_data["phosphorus_status"],
                            potassium_status=health_data["potassium_status"],
                            notes=health_data["notes"]
                        )
                        
                        if health_record_id:
                            logger.info(f"Added health record for field ID: {field_id}")
                        else:
                            logger.error(f"Failed to add health record for field ID: {field_id}")
            
            # Add activities
            for _ in range(3):  # Add 3 random activities per farm
                activity_data = random.choice(ACTIVITIES)
                activity_id = add_activity(
                    farm_id=farm_id,
                    activity_type=activity_data["activity_type"],
                    description=activity_data["description"],
                    status=activity_data["status"]
                )
                
                if activity_id:
                    logger.info(f"Added activity: {activity_data['activity_type']} for farm ID: {farm_id}")
                else:
                    logger.error(f"Failed to add activity for farm ID: {farm_id}")
        
        logger.info("Demo data population completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error populating demo data: {e}")
        return False

def initialize_database():
    """Initialize the database with schema and demo data"""
    # Initialize database schema
    init_db()
    
    # Check if farms already exist
    with get_session() as session:
        from database import Farm
        existing_farms = session.query(Farm).count()
    
    # Populate with demo data if empty
    if existing_farms == 0:
        logger.info("No existing farms found. Populating with demo data...")
        populate_demo_data()
    else:
        logger.info(f"Database already contains {existing_farms} farms. Skipping demo data population.")

if __name__ == "__main__":
    initialize_database()