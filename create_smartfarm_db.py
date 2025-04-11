#!/usr/bin/env python
"""
SmartFarm Database Creation Script
This script creates the SmartFarm database in the PostgreSQL server.
"""
import os
import sys
import re
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database():
    """Create the SmartFarm database in PostgreSQL server"""
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL', '')
    
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set")
        return False
    
    # Parse the URL to get connection details
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Extract parts from the URL
    pattern = r'postgresql://([^:]+):([^@]+)@([^/]+)/([^?]+)(\?.*)?'
    match = re.match(pattern, database_url)
    
    if not match:
        logger.error(f"Failed to parse DATABASE_URL: {database_url}")
        # Try an alternate parsing method
        try:
            # Split by protocol
            parts = database_url.split('://', 1)
            if len(parts) != 2:
                logger.error("Invalid URL format (no protocol)")
                return False
                
            # Split by @ to separate credentials and host info
            cred_host = parts[1].split('@', 1)
            if len(cred_host) != 2:
                logger.error("Invalid URL format (no @ separator)")
                return False
                
            # Get username and password from credentials
            creds = cred_host[0].split(':', 1)
            if len(creds) != 2:
                logger.error("Invalid URL format (no credentials separator)")
                return False
                
            username = creds[0]
            password = creds[1]
            
            # Get host and database info
            host_db = cred_host[1].split('/', 1)
            if len(host_db) != 2:
                logger.error("Invalid URL format (no path)")
                return False
                
            # Host might include port
            host_parts = host_db[0].split(':', 1)
            host = host_parts[0]
            port = host_parts[1] if len(host_parts) > 1 else "5432"
            
            # Database might include query params
            db_parts = host_db[1].split('?', 1)
            dbname = db_parts[0]
            params = db_parts[1] if len(db_parts) > 1 else None
            
            logger.info(f"Parsed DATABASE_URL manually: host={host}, port={port}, dbname={dbname}")
        except Exception as e:
            logger.error(f"Failed to manually parse DATABASE_URL: {e}")
            return False
    else:
        # Use the regex match result
        username, password, host, dbname, params = match.groups()
        # Check if host contains port
        if ':' in host:
            host, port = host.split(':', 1)
        else:
            port = "5432"
    
    # Connect to default database to create the new database
    try:
        logger.info(f"Connecting to default database '{dbname}' to create SmartFarm database...")
        conn = psycopg2.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=dbname
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor and check if SmartFarm database exists
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'smartfarm'")
        exists = cursor.fetchone()
        
        if not exists:
            logger.info("Creating SmartFarm database...")
            cursor.execute("CREATE DATABASE smartfarm")
            logger.info("SmartFarm database created successfully!")
        else:
            logger.info("SmartFarm database already exists")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Error creating SmartFarm database: {e}")
        return False

if __name__ == "__main__":
    if create_database():
        logger.info("Database creation completed successfully")
        sys.exit(0)
    else:
        logger.error("Database creation failed")
        sys.exit(1)