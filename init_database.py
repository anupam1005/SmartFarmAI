import logging
from database import init_db
from db_utils import setup_demo_farm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database and set up demo data"""
    try:
        # Initialize database schema
        logger.info("Initializing database...")
        init_db()
        
        # Set up demo farm and sample data
        logger.info("Setting up demo farm data...")
        result = setup_demo_farm()
        
        if result:
            logger.info("Database setup completed successfully")
        else:
            logger.warning("Demo farm setup failed, but database was initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

if __name__ == "__main__":
    main()