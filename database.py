import os
import logging
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment (using PostgreSQL)
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# If you want to use a custom database connection instead of the environment variable,
# uncomment and modify the following line:
# DATABASE_URL = "postgresql://username:password@host:port/SmartFarm"

# PostgreSQL URLs from Replit sometimes start with postgres:// instead of postgresql://
# SQLAlchemy requires postgresql:// format
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create SQLAlchemy engine and session
if DATABASE_URL:
    logger.info(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    try:
        # Test connection
        with engine.connect() as conn:
            logger.info("Database connection successful!")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise
else:
    logger.error("DATABASE_URL environment variable is not set")
    raise ValueError("DATABASE_URL environment variable is not set")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Database Models
class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String)
    area_size = Column(Float)  # Hectares
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    fields = relationship("Field", back_populates="farm", cascade="all, delete")
    activities = relationship("Activity", back_populates="farm", cascade="all, delete")
    resources = relationship("Resource", back_populates="farm", cascade="all, delete")
    crop_recommendations = relationship("CropRecommendation", back_populates="farm", cascade="all, delete")

class Field(Base):
    __tablename__ = "fields"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"))
    name = Column(String, index=True)
    area_size = Column(Float)  # Hectares
    soil_type = Column(String)
    current_crop = Column(String)
    planting_date = Column(DateTime)
    expected_harvest_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    farm = relationship("Farm", back_populates="fields")
    health_records = relationship("HealthRecord", back_populates="field", cascade="all, delete")
    pest_detections = relationship("PestDetection", back_populates="field", cascade="all, delete")
    resource_usages = relationship("ResourceUsage", back_populates="field", cascade="all, delete")

class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.now)
    health_score = Column(Float)  # 0-100
    health_status = Column(String)  # Good, Fair, Poor
    green_percentage = Column(Float)
    yellow_percentage = Column(Float)
    brown_percentage = Column(Float)
    nitrogen_status = Column(String)  # Good, Medium, Low
    phosphorus_status = Column(String)  # Good, Medium, Low
    potassium_status = Column(String)  # Good, Medium, Low
    notes = Column(Text)
    image_path = Column(String)
    
    # Relationships
    field = relationship("Field", back_populates="health_records")
    recommendations = relationship("Recommendation", back_populates="health_record", cascade="all, delete")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    health_record_id = Column(Integer, ForeignKey("health_records.id", ondelete="CASCADE"))
    text = Column(Text)
    implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime)
    
    # Relationships
    health_record = relationship("HealthRecord", back_populates="recommendations")

class PestDetection(Base):
    __tablename__ = "pest_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.now)
    detected_class = Column(String)
    confidence = Column(Float)  # 0-1
    severity = Column(String)  # Low, Medium, High
    description = Column(Text)
    treatment_recommendation = Column(Text)
    image_path = Column(String)
    
    # Relationships
    field = relationship("Field", back_populates="pest_detections")

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.now)
    activity_type = Column(String)  # Planting, Fertilizing, Harvesting, etc.
    description = Column(Text)
    status = Column(String)  # Pending, In Progress, Completed, Cancelled
    
    # Relationships
    farm = relationship("Farm", back_populates="activities")

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"))
    name = Column(String)
    type = Column(String)  # Fertilizer, Pesticide, Water, Seeds, etc.
    quantity = Column(Float)
    unit = Column(String)  # Kg, L, etc.
    last_updated = Column(DateTime, default=datetime.now)
    
    # Relationships
    farm = relationship("Farm", back_populates="resources")
    usages = relationship("ResourceUsage", back_populates="resource", cascade="all, delete")

class ResourceUsage(Base):
    __tablename__ = "resource_usages"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"))
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"))
    date = Column(DateTime, default=datetime.now)
    quantity = Column(Float)
    application_method = Column(String)  # Spraying, Drip, Broadcast, etc.
    notes = Column(Text)
    
    # Relationships
    resource = relationship("Resource", back_populates="usages")
    field = relationship("Field", back_populates="resource_usages")

class WeatherRecord(Base):
    __tablename__ = "weather_records"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    location = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    condition = Column(String)  # Clear, Cloudy, Rain, etc.

class CropRecommendation(Base):
    __tablename__ = "crop_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"))
    crop = Column(String)
    suitability = Column(Float)  # 0-100
    growing_season = Column(String)
    time_to_harvest = Column(String)
    water_requirements = Column(String)
    fertilizer_needs = Column(String)
    market_demand = Column(String)
    estimated_yield = Column(String)
    price_trend = Column(String)
    investment_level = Column(String)
    rationale = Column(Text)
    cultivation_tips = Column(Text)
    risks = Column(Text)
    implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime)
    
    # Relationships
    farm = relationship("Farm", back_populates="crop_recommendations")

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def init_db():
    """Initialize the database"""
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Initialize database if this script is run directly
if __name__ == "__main__":
    init_db()