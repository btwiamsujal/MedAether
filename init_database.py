#!/usr/bin/env python3
"""
Database initialization script for MedAether
Creates collections, indexes, and sample data
"""

import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config import get_config, DEFAULT_HEALTH_PROBLEMS, DEFAULT_HEALTH_PLANS

def create_indexes(db):
    """Create database indexes for better performance"""
    print("Creating database indexes...")
    
    # Users collection indexes
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("created_at", DESCENDING)])
    db.users.create_index([("health_status", ASCENDING)])
    
    # Chat history indexes
    db.chat_history.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
    db.chat_history.create_index([("timestamp", DESCENDING)])
    
    # Community reports indexes
    db.reports.create_index([("user_id", ASCENDING), ("submitted_at", DESCENDING)])
    db.reports.create_index([("location", TEXT)])
    db.reports.create_index([("severity", ASCENDING)])
    db.reports.create_index([("status", ASCENDING)])
    db.reports.create_index([("submitted_at", DESCENDING)])
    
    # Telegram users indexes
    db.telegram_users.create_index([("telegram_id", ASCENDING)], unique=True)
    db.telegram_users.create_index([("last_interaction", DESCENDING)])
    
    # Telegram consultations indexes
    db.telegram_consultations.create_index([("telegram_id", ASCENDING), ("timestamp", DESCENDING)])
    db.telegram_consultations.create_index([("timestamp", DESCENDING)])
    
    print("✓ Database indexes created successfully")

def create_sample_data(db):
    """Create sample data for development and testing"""
    print("Creating sample data...")
    
    # Create sample admin user
    admin_user = {
        "name": "Admin User",
        "email": "admin@medaether.com",
        "password": generate_password_hash("admin123"),
        "age": 30,
        "gender": "other",
        "created_at": datetime.utcnow(),
        "health_status": "green",
        "medical_history": [],
        "is_admin": True,
        "profile_completed": True
    }
    
    try:
        db.users.insert_one(admin_user)
        print("✓ Admin user created (email: admin@medaether.com, password: admin123)")
    except Exception as e:
        if "duplicate key error" in str(e):
            print("ℹ Admin user already exists")
        else:
            print(f"✗ Error creating admin user: {e}")
    
    # Create sample regular user
    sample_user = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": generate_password_hash("password123"),
        "age": 28,
        "gender": "male",
        "created_at": datetime.utcnow() - timedelta(days=30),
        "health_status": "green",
        "medical_history": ["allergies"],
        "profile_completed": True,
        "current_weight": 75,
        "height": 180,
        "blood_pressure": "120/80",
        "emergency_contact": "+1234567890"
    }
    
    try:
        result = db.users.insert_one(sample_user)
        sample_user_id = str(result.inserted_id)
        print("✓ Sample user created (email: john.doe@example.com, password: password123)")
        
        # Create sample chat history for the user
        sample_chat = [
            {
                "user_id": sample_user_id,
                "user_message": "I have a headache, what should I do?",
                "ai_response": "For headaches, I recommend: 1. Rest in a quiet, dark room 2. Apply a cold compress to your forehead 3. Stay hydrated 4. Consider over-the-counter pain relievers like acetaminophen or ibuprofen if needed. If headaches persist or worsen, please consult a healthcare professional.",
                "language": "en",
                "timestamp": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "user_id": sample_user_id,
                "user_message": "What are some good exercises for beginners?",
                "ai_response": "Great question! For beginners, I recommend starting with: 1. Walking 20-30 minutes daily 2. Basic bodyweight exercises (push-ups, squats, planks) 3. Stretching or yoga 4. Swimming if available. Start slowly and gradually increase intensity. Always consult with a healthcare provider before starting any new exercise program.",
                "language": "en",
                "timestamp": datetime.utcnow() - timedelta(hours=1)
            }
        ]
        
        db.chat_history.insert_many(sample_chat)
        print("✓ Sample chat history created")
        
        # Create sample community report
        sample_report = {
            "user_id": sample_user_id,
            "issue_title": "Water Quality Concern",
            "description": "Residents in downtown area reporting unusual taste and odor in tap water. Multiple families experiencing minor digestive issues.",
            "location": "Downtown District, Main Street area",
            "severity": "medium",
            "submitted_at": datetime.utcnow() - timedelta(days=1),
            "status": "pending"
        }
        
        db.reports.insert_one(sample_report)
        print("✓ Sample community report created")
        
    except Exception as e:
        if "duplicate key error" in str(e):
            print("ℹ Sample user already exists")
        else:
            print(f"✗ Error creating sample user: {e}")
    
    # Create health problems collection
    try:
        if db.health_problems.count_documents({}) == 0:
            db.health_problems.insert_many(DEFAULT_HEALTH_PROBLEMS)
            print("✓ Default health problems added")
        else:
            print("ℹ Health problems already exist")
    except Exception as e:
        print(f"✗ Error adding health problems: {e}")
    
    # Create health plans collection
    try:
        if db.health_plans.count_documents({}) == 0:
            db.health_plans.insert_many(DEFAULT_HEALTH_PLANS)
            print("✓ Default health plans added")
        else:
            print("ℹ Health plans already exist")
    except Exception as e:
        print(f"✗ Error adding health plans: {e}")

def create_collections(db):
    """Create collections with validation rules"""
    print("Setting up database collections...")
    
    # Create collections if they don't exist
    collections = [
        'users', 'chat_history', 'reports', 'health_problems', 'health_plans',
        'telegram_users', 'telegram_consultations', 'health_metrics'
    ]
    
    existing_collections = db.list_collection_names()
    
    for collection_name in collections:
        if collection_name not in existing_collections:
            db.create_collection(collection_name)
            print(f"✓ Created collection: {collection_name}")
        else:
            print(f"ℹ Collection already exists: {collection_name}")
    
    # Add validation for users collection
    try:
        db.command("collMod", "users", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "email", "password", "age", "gender", "created_at"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "email": {"bsonType": "string", "pattern": "^.+@.+$"},
                    "password": {"bsonType": "string"},
                    "age": {"bsonType": "int", "minimum": 1, "maximum": 150},
                    "gender": {"bsonType": "string", "enum": ["male", "female", "other"]},
                    "health_status": {"bsonType": "string", "enum": ["green", "yellow", "red"]},
                    "medical_history": {"bsonType": "array"}
                }
            }
        })
        print("✓ User collection validation rules added")
    except Exception as e:
        print(f"ℹ User validation rules already exist or error: {e}")

def initialize_database():
    """Main function to initialize the database"""
    print("=" * 50)
    print("MedAether Database Initialization")
    print("=" * 50)
    
    # Get configuration
    config = get_config()
    
    # Connect to MongoDB
    try:
        client = MongoClient(config.MONGODB_URI)
        db = client[config.MONGODB_DB_NAME]
        
        # Test connection
        client.admin.command('ismaster')
        print(f"✓ Connected to MongoDB: {config.MONGODB_DB_NAME}")
        
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    try:
        # Create collections
        create_collections(db)
        
        # Create indexes
        create_indexes(db)
        
        # Create sample data (only for development)
        if os.environ.get('FLASK_ENV') == 'development':
            create_sample_data(db)
        else:
            print("ℹ Skipping sample data creation (not in development mode)")
        
        print("\n" + "=" * 50)
        print("Database initialization completed successfully!")
        print("=" * 50)
        
        # Print database statistics
        print("\nDatabase Statistics:")
        print(f"• Users: {db.users.count_documents({})}")
        print(f"• Chat History: {db.chat_history.count_documents({})}")
        print(f"• Community Reports: {db.reports.count_documents({})}")
        print(f"• Health Problems: {db.health_problems.count_documents({})}")
        print(f"• Health Plans: {db.health_plans.count_documents({})}")
        print(f"• Telegram Users: {db.telegram_users.count_documents({})}")
        
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        sys.exit(1)
    
    finally:
        client.close()

def drop_database():
    """Drop the entire database (use with caution!)"""
    response = input("Are you sure you want to drop the entire database? This cannot be undone. (yes/no): ")
    if response.lower() != 'yes':
        print("Database drop cancelled.")
        return
    
    config = get_config()
    try:
        client = MongoClient(config.MONGODB_URI)
        client.drop_database(config.MONGODB_DB_NAME)
        print(f"✓ Database '{config.MONGODB_DB_NAME}' dropped successfully")
    except Exception as e:
        print(f"✗ Failed to drop database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MedAether Database Initialization")
    parser.add_argument("--drop", action="store_true", help="Drop the entire database")
    parser.add_argument("--reset", action="store_true", help="Drop and reinitialize the database")
    
    args = parser.parse_args()
    
    if args.drop or args.reset:
        drop_database()
    
    if not args.drop:
        initialize_database()
    
    print("\nInitialization complete!")
