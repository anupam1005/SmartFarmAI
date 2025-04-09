import os
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the database
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.warning("DATABASE_URL environment variable not found. Using SQLite database.")
    DATABASE_URL = "sqlite:///smartfarm.db"

# Create engine
try:
    # Modify PostgreSQL URL if necessary (SQLAlchemy 1.4+ requires postgresql:// not postgres://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(DATABASE_URL)
    logger.info(f"Database engine created with {DATABASE_URL.split('://')[0]}")
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    # Fallback to SQLite
    DATABASE_URL = "sqlite:///smartfarm.db"
    engine = create_engine(DATABASE_URL)
    logger.info(f"Fallback to SQLite database")

# Create base class for declarative models
Base = declarative_base()

# Define models
class Farm(Base):
    __tablename__ = 'farms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255))
    area_size = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="farm", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="farm", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Farm(id={self.id}, name='{self.name}', location='{self.location}')>"

class Field(Base):
    __tablename__ = 'fields'
    
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False)
    name = Column(String(100), nullable=False)
    area_size = Column(Float)
    soil_type = Column(String(50))
    current_crop = Column(String(100))
    planting_date = Column(DateTime)
    expected_harvest_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    farm = relationship("Farm", back_populates="fields")
    health_records = relationship("HealthRecord", back_populates="field", cascade="all, delete-orphan")
    resources_used = relationship("ResourceUsage", back_populates="field", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Field(id={self.id}, name='{self.name}', crop='{self.current_crop}')>"

class HealthRecord(Base):
    __tablename__ = 'health_records'
    
    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, ForeignKey('fields.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    health_score = Column(Float)
    health_status = Column(String(50))
    green_percentage = Column(Float)
    yellow_percentage = Column(Float)
    brown_percentage = Column(Float)
    nitrogen_status = Column(String(50))
    phosphorus_status = Column(String(50))
    potassium_status = Column(String(50))
    notes = Column(Text)
    image_path = Column(String(255))
    
    # Relationships
    field = relationship("Field", back_populates="health_records")
    recommendations = relationship("Recommendation", back_populates="health_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HealthRecord(id={self.id}, field_id={self.field_id}, score={self.health_score}, status='{self.health_status}')>"

class Recommendation(Base):
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True)
    health_record_id = Column(Integer, ForeignKey('health_records.id'), nullable=False)
    text = Column(Text, nullable=False)
    implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime)
    
    # Relationships
    health_record = relationship("HealthRecord", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, implemented={self.implemented})>"

class PestDetection(Base):
    __tablename__ = 'pest_detections'
    
    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, ForeignKey('fields.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    detected_class = Column(String(100))
    confidence = Column(Float)
    severity = Column(String(50))
    description = Column(Text)
    treatment_recommendation = Column(Text)
    image_path = Column(String(255))
    
    # Relationships
    field = relationship("Field", backref="pest_detections")
    
    def __repr__(self):
        return f"<PestDetection(id={self.id}, field_id={self.field_id}, detected_class='{self.detected_class}')>"

class Activity(Base):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    activity_type = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="Pending")
    
    # Relationships
    farm = relationship("Farm", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity(id={self.id}, type='{self.activity_type}', status='{self.status}')>"

class Resource(Base):
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., Water, Fertilizer, Seeds
    quantity = Column(Float)
    unit = Column(String(20))  # e.g., liters, kg
    last_updated = Column(DateTime, default=datetime.now)
    
    # Relationships
    farm = relationship("Farm", back_populates="resources")
    usages = relationship("ResourceUsage", back_populates="resource", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resource(id={self.id}, name='{self.name}', type='{self.type}', quantity={self.quantity})>"

class ResourceUsage(Base):
    __tablename__ = 'resource_usages'
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=False)
    field_id = Column(Integer, ForeignKey('fields.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    quantity = Column(Float, nullable=False)
    application_method = Column(String(100))
    notes = Column(Text)
    
    # Relationships
    resource = relationship("Resource", back_populates="usages")
    field = relationship("Field", back_populates="resources_used")
    
    def __repr__(self):
        return f"<ResourceUsage(id={self.id}, resource_id={self.resource_id}, quantity={self.quantity})>"

class WeatherRecord(Base):
    __tablename__ = 'weather_records'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    location = Column(String(255))
    temperature = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(String(10))
    condition = Column(String(50))
    
    def __repr__(self):
        return f"<WeatherRecord(id={self.id}, location='{self.location}', temperature={self.temperature})>"

class CropRecommendation(Base):
    __tablename__ = 'crop_recommendations'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    farm_id = Column(Integer, ForeignKey('farms.id'))
    crop = Column(String(100), nullable=False)
    suitability = Column(Float)
    growing_season = Column(String(100))
    time_to_harvest = Column(String(100))
    water_requirements = Column(String(100))
    fertilizer_needs = Column(String(100))
    market_demand = Column(String(50))
    estimated_yield = Column(String(100))
    price_trend = Column(String(50))
    investment_level = Column(String(50))
    rationale = Column(Text)
    cultivation_tips = Column(Text)
    risks = Column(Text)
    implemented = Column(Boolean, default=False)
    
    # Relationships
    farm = relationship("Farm", backref="crop_recommendations")
    
    def __repr__(self):
        return f"<CropRecommendation(id={self.id}, crop='{self.crop}', suitability={self.suitability})>"

def create_tables():
    """Create all tables defined by the models"""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_session():
    """Get a new database session"""
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Initialize the database"""
    try:
        # Create tables if they don't exist
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise