import os
from pymongo import MongoClient

# Get MongoDB connection string from environment variables (recommended for security)
MONGO_URI = 'mongodb+srv://redlegacy:<db_password>@cluster0.hvec7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

# Connect to MongoDB Atlas
def get_database():
    client = MongoClient(MONGO_URI)
    return client["myDatabase"]  # Replace with your actual database name

# Get the users collection
def get_users_collection():
    db = get_database()
    return db["users"]  # Replace with your actual collection name
