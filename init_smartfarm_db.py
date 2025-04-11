#!/usr/bin/env python
"""
SmartFarm Database Initialization Script
This script initializes the SmartFarm database with the proper schema and demo data.
"""
import os
import sys
import logging
from database import init_db
from init_database import populate_demo_data, reset_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_smartfarm_db():
    """Initialize the SmartFarm database with schema and demo data"""
    logger.info("Initializing SmartFarm database...")
    init_db()
    
    # Populate with demo data
    logger.info("Populating SmartFarm database with demo data...")
    populate_demo_data()
    
    logger.info("SmartFarm database initialization complete!")

def main():
    """Main entry point with command-line argument handling"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--reset':
            logger.warning("Resetting SmartFarm database (all data will be lost)...")
            reset_database()
        elif sys.argv[1] == '--help':
            print("Usage: python init_smartfarm_db.py [--reset | --help]")
            print("")
            print("Options:")
            print("  --reset    Reset the SmartFarm database (drops all tables and recreates them)")
            print("  --help     Show this help message")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help to see available options")
    else:
        initialize_smartfarm_db()

if __name__ == "__main__":
    main()