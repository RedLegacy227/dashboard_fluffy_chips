from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variables
MONGO_URI = os.getenv("mongo.env")

# Connect to MongoDB Atlas
def get_database():
    if not MONGO_URI:
        raise ValueError("❌ MONGO_URI is not set in environment variables.")
    
    client = MongoClient(MONGO_URI)
    return client["Fluffy_Chips_Web_Analyser"]  # Replace with your actual database name

# Get the users collection
def get_users_collection():
    db = get_database()
    return db["users"]  # Replace with your actual collection name

