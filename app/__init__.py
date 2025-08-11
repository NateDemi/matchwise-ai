# app/__init__.py
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Create data directories
os.makedirs('data/results', exist_ok=True)

# Initialize Vanna (optional at startup)
# from app.services.vanna_service import get_vanna_instance
# vanna = get_vanna_instance()