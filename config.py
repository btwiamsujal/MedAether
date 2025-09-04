import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/'
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME') or 'medaether'
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-3.5-turbo'
    HUGGINGFACE_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN')
    RASA_ENDPOINT_URL = os.environ.get('RASA_ENDPOINT_URL') or 'http://localhost:5005'
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_BOT_USERNAME = os.environ.get('TELEGRAM_BOT_USERNAME') or 'medaether_bot'
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS') or 'healthauthorities@example.com'
    
    # Google Translate API
    GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS') or 'jpg,jpeg,png,gif,pdf'
    
    # Security Configuration
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME') or 86400))
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'memory://'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT') or '100 per hour'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'medaether.log'
    
    # Health Authorities
    HEALTH_DEPARTMENT_EMAIL = os.environ.get('HEALTH_DEPARTMENT_EMAIL') or 'health.dept@city.gov'
    EMERGENCY_CONTACT_EMAIL = os.environ.get('EMERGENCY_CONTACT_EMAIL') or 'emergency@health.gov'
    
    # Deployment Configuration
    PORT = int(os.environ.get('PORT') or 5000)
    HOST = os.environ.get('HOST') or '127.0.0.1'
    
    # Extended Features
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Use local MongoDB for development
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/'
    
    # Disable secure cookies for development
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Ensure secure settings for production
    SESSION_COOKIE_SECURE = True
    
    # Use environment variables for all sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    MONGODB_URI = os.environ.get('MONGODB_URI')
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    MONGODB_URI = 'mongodb://localhost:27017/'
    MONGODB_DB_NAME = 'medaether_test'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.environ.get('FLASK_ENV') or 'development'
    return config.get(env, DevelopmentConfig)

# Health Status Configuration
HEALTH_STATUS_CONFIG = {
    'green': {
        'label': 'Healthy / Fit',
        'description': 'No major health concerns identified',
        'color': '#198754',
        'icon': 'check-circle'
    },
    'yellow': {
        'label': 'Moderate Health Issues',
        'description': 'Some health conditions requiring monitoring',
        'color': '#ffc107',
        'icon': 'exclamation-triangle'
    },
    'red': {
        'label': 'Serious Medical Condition',
        'description': 'Requires immediate medical attention',
        'color': '#dc3545',
        'icon': 'exclamation-circle'
    }
}

# Medical Conditions Categorization
MEDICAL_CONDITIONS = {
    'serious': [
        'diabetes', 'heart disease', 'cancer', 'kidney disease', 'liver disease',
        'stroke', 'heart attack', 'coronary artery disease', 'chronic kidney disease',
        'cirrhosis', 'heart failure', 'chronic obstructive pulmonary disease',
        'tuberculosis', 'hiv', 'aids'
    ],
    'moderate': [
        'hypertension', 'asthma', 'arthritis', 'thyroid', 'anxiety', 'depression',
        'high blood pressure', 'high cholesterol', 'osteoporosis', 'fibromyalgia',
        'migraines', 'sleep apnea', 'acid reflux', 'irritable bowel syndrome'
    ],
    'mild': [
        'allergies', 'seasonal allergies', 'mild asthma', 'occasional headaches',
        'minor joint pain', 'occasional insomnia'
    ]
}

# Supported Languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese'
}

# Email Templates
EMAIL_TEMPLATES = {
    'community_report': {
        'subject': 'Community Health Report: {issue_title}',
        'body': """
Dear Health Authorities,

A community health report has been submitted through MedAether platform:

Issue Title: {issue_title}
Location: {location}
Severity: {severity}
Description: {description}
Submitted by: User ID {user_id}
Submission Date: {submitted_at}

Please review and take appropriate action as necessary.

Best regards,
MedAether Team
        """
    },
    'welcome': {
        'subject': 'Welcome to MedAether!',
        'body': """
Welcome to MedAether - Your AI-Driven Health Companion!

Thank you for joining our community. Here's what you can do:

• Get AI-powered health consultations
• Access quick solutions for common health problems
• Create personalized health plans
• Report community health issues
• Maintain your digital health card

Getting started is easy:
1. Complete your health profile
2. Explore our AI chat feature
3. Connect with our Telegram bot: @medaether_bot

Stay healthy!
The MedAether Team
        """
    }
}

# Default Health Data
DEFAULT_HEALTH_PROBLEMS = [
    {
        'name': 'Fever',
        'description': 'Body temperature above normal range, often accompanied by chills',
        'medicine': 'Paracetamol 500mg, Ibuprofen (as prescribed)',
        'home_remedy': 'Rest, plenty of fluids, cool compress on forehead',
        'precautions': 'Monitor temperature, seek medical help if fever persists >3 days'
    },
    {
        'name': 'Common Cold',
        'description': 'Runny nose, sneezing, mild fever, sore throat',
        'medicine': 'Antihistamines, decongestants (as prescribed)',
        'home_remedy': 'Warm saltwater gargling, honey with warm water, steam inhalation',
        'precautions': 'Rest, avoid cold drinks, wear warm clothes'
    },
    {
        'name': 'Headache',
        'description': 'Pain in head or neck region, tension or migraine type',
        'medicine': 'Paracetamol, Aspirin (as prescribed)',
        'home_remedy': 'Head massage, cold/warm compress, adequate sleep',
        'precautions': 'Avoid stress, stay hydrated, limit screen time'
    },
    {
        'name': 'Stomach Ache',
        'description': 'Abdominal pain, cramping, digestive discomfort',
        'medicine': 'Antacids, ORS solution (as prescribed)',
        'home_remedy': 'Ginger tea, BRAT diet (banana, rice, apple, toast)',
        'precautions': 'Avoid spicy/oily food, eat light meals, stay hydrated'
    },
    {
        'name': 'Cough',
        'description': 'Dry or productive cough, throat irritation',
        'medicine': 'Cough syrup, lozenges (as prescribed)',
        'home_remedy': 'Honey with warm water, turmeric milk, steam inhalation',
        'precautions': 'Avoid cold beverages, cover mouth while coughing'
    }
]

DEFAULT_HEALTH_PLANS = [
    {
        'name': 'Weight Gain Plan',
        'description': 'Healthy weight gain program for underweight individuals',
        'diet': 'High-calorie nutritious foods, protein-rich meals, healthy fats',
        'exercise': 'Strength training 3x/week, compound exercises, progressive overload',
        'lifestyle': 'Regular meals, adequate sleep (7-8 hours), stress management'
    },
    {
        'name': 'Liver Care Plan',
        'description': 'Comprehensive liver health maintenance program',
        'diet': 'Low-fat diet, avoid alcohol, increase fiber intake, green vegetables',
        'exercise': 'Moderate cardio 30 min daily, yoga, walking',
        'lifestyle': 'Avoid processed foods, regular health checkups, maintain healthy weight'
    },
    {
        'name': 'Heart Health Plan',
        'description': 'Cardiovascular health improvement program',
        'diet': 'Low sodium, omega-3 rich foods, fruits and vegetables',
        'exercise': 'Cardio exercises, brisk walking, swimming',
        'lifestyle': 'No smoking, limit alcohol, stress reduction, regular BP monitoring'
    },
    {
        'name': 'Diabetes Management',
        'description': 'Blood sugar control and diabetes management plan',
        'diet': 'Low glycemic index foods, portion control, regular meal timing',
        'exercise': 'Daily 30-45 min physical activity, strength training',
        'lifestyle': 'Regular glucose monitoring, medication compliance, foot care'
    }
]
