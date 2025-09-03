from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import re
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    from googletrans import Translator
except ImportError:
    Translator = None
try:
    import bleach
except ImportError:
    bleach = None
from config import get_config, DEFAULT_HEALTH_PROBLEMS, DEFAULT_HEALTH_PLANS

# Initialize Flask app with configuration
app = Flask(__name__)
config_class = get_config()
app.config.from_object(config_class)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)


# Note: CSRF protection disabled for initial testing
# csrf = CSRFProtect(app)

# MongoDB Configuration
client = MongoClient(app.config['MONGODB_URI'])
db = client[app.config['MONGODB_DB_NAME']]

# AI Configuration
openai_client = None
if app.config['OPENAI_API_KEY'] and OpenAI is not None:
    openai_client = OpenAI(api_key=app.config['OPENAI_API_KEY'])

# Google Translate
translator = None
if Translator is not None:
    try:
        translator = Translator()
    except Exception as e:
        print(f"Failed to initialize translator: {e}")
        translator = None

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        
        # Check if user already exists
        if db.users.find_one({'email': email}):
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        # Create new user
        user_data = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'age': int(age),
            'gender': gender,
            'created_at': datetime.utcnow(),
            'health_status': 'green',
            'medical_history': []
        }
        
        result = db.users.insert_one(user_data)
        session['user_id'] = str(result.inserted_id)
        session['user_name'] = name
        
        flash('Registration successful!', 'success')
        return redirect(url_for('home'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/quick-solutions')
def quick_solutions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Health problems data
    health_problems = [
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
    
    return render_template('quick_solutions.html', problems=health_problems)

@app.route('/health-plans')
def health_plans():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Health plans data
    health_plans = [
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
    
    return render_template('health_plans.html', plans=health_plans)

@app.route('/community-reports', methods=['GET', 'POST'])
def community_reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        report_data = {
            'user_id': session['user_id'],
            'issue_title': request.form['issue_title'],
            'description': request.form['description'],
            'location': request.form['location'],
            'severity': request.form['severity'],
            'submitted_at': datetime.utcnow(),
            'status': 'pending'
        }
        
        # Save report to database
        db.reports.insert_one(report_data)
        
        # Send email to authorities (if configured)
        if app.config['EMAIL_USER'] and app.config['EMAIL_PASSWORD']:
            send_report_email(report_data)
        
        flash('Report submitted successfully!', 'success')
        return redirect(url_for('community_reports'))
    
    # Get user's previous reports
    user_reports = list(db.reports.find({'user_id': session['user_id']}).sort('submitted_at', -1))
    
    return render_template('community_reports.html', reports=user_reports)

@app.route('/digital-health-card')
def digital_health_card():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get fresh user data from database
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    # Always recalculate health status to ensure it's current
    health_status = calculate_health_status(user)
    
    # Update user's health status in database if it changed
    current_status = user.get('health_status')
    if current_status != health_status:
        db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'health_status': health_status, 'health_status_updated': datetime.utcnow()}}
        )
        # Refresh user data with updated status
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    # Get health status configuration for display
    from config import HEALTH_STATUS_CONFIG
    status_config = HEALTH_STATUS_CONFIG.get(health_status, {
        'label': 'Unknown',
        'description': 'Status could not be determined',
        'color': '#6c757d',
        'icon': 'question-circle'
    })
    
    return render_template('digital_health_card.html', 
                         user=user, 
                         health_status=health_status,
                         status_config=status_config)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if request.method == 'POST':
        # Get all form data
        medical_history = [hist for hist in request.form.getlist('medical_history') if hist.strip()]
        
        update_data = {
            'name': request.form['name'],
            'age': int(request.form['age']),
            'gender': request.form['gender'],
            'medical_history': medical_history,
            'blood_group': request.form.get('blood_group', ''),
            'phone': request.form.get('phone', ''),
            'emergency_contact': request.form.get('emergency_contact', ''),
            'address': request.form.get('address', ''),
            'last_updated': datetime.utcnow()
        }
        
        db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': update_data}
        )
        
        # Recalculate health status after medical history update
        updated_user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        new_health_status = calculate_health_status(updated_user)
        
        if new_health_status != user.get('health_status'):
            db.users.update_one(
                {'_id': ObjectId(session['user_id'])},
                {'$set': {'health_status': new_health_status}}
            )
            flash(f'Profile updated successfully! Health status updated to {new_health_status.title()}.', 'success')
        else:
            flash('Profile updated successfully!', 'success')
        
        session['user_name'] = update_data['name']
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/ai-chat', methods=['GET', 'POST'])
def ai_chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_message = request.form['message']
        language = request.form.get('language', 'en')
        
        # Get user information for personalized advice
        user = db.users.find_one({'_id': ObjectId(session['user_id'])})
        
        # Get AI response with user context
        ai_response = get_ai_medical_advice(user_message, language, user)
        
        # Save chat history
        chat_data = {
            'user_id': session['user_id'],
            'user_message': user_message,
            'ai_response': ai_response,
            'language': language,
            'timestamp': datetime.utcnow()
        }
        db.chat_history.insert_one(chat_data)
        
        return jsonify({'response': ai_response})
    
    # Get chat history
    chat_history = list(db.chat_history.find({'user_id': session['user_id']}).sort('timestamp', -1).limit(20))
    
    return render_template('ai_chat.html', chat_history=chat_history)

def get_ai_medical_advice(message, language='en', user=None):
    """Get medical advice from AI (OpenAI GPT or fallback) with user context"""
    try:
        if openai_client and user:
            # Create user context for personalized advice
            user_context = f"""
            User Profile:
            - Age: {user.get('age', 'Unknown')}
            - Gender: {user.get('gender', 'Unknown')}
            - Medical History: {', '.join(user.get('medical_history', [])) if user.get('medical_history') else 'No significant medical history'}
            - Health Status: {user.get('health_status', 'Unknown')}
            - Blood Group: {user.get('blood_group', 'Unknown')}
            """
            
            system_content = f"""You are MedAether AI, a medical assistant. Provide helpful health advice and information based on the user's profile.
            
            {user_context}
            
            Important guidelines:
            - Consider the user's age, gender, and medical history when providing advice
            - If the user has serious medical conditions (like diabetes, heart disease), mention their relevance to current symptoms
            - Always remind users to consult healthcare professionals for serious conditions
            - Keep responses concise, informative, and empathetic
            - Do not provide specific drug dosages without proper medical consultation
            - Include relevant precautions and when to seek immediate medical help
            - Personalize your response based on their medical history
            """
            
            response = openai_client.chat.completions.create(
                model=app.config['OPENAI_MODEL'],
                messages=[
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {"role": "user", "content": message}
                ],
                max_tokens=600,
                temperature=0.3
            )
            ai_response = response.choices[0].message.content
        elif openai_client:
            # Basic AI response without user context
            response = openai_client.chat.completions.create(
                model=app.config['OPENAI_MODEL'],
                messages=[
                    {
                        "role": "system",
                        "content": """You are MedAether AI, a medical assistant. Provide helpful health advice and information. 
                        Always remind users to consult healthcare professionals for serious conditions. 
                        Keep responses concise, informative, and empathetic. Do not provide specific drug dosages without 
                        proper medical consultation. Include relevant precautions and when to seek immediate medical help."""
                    },
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.3
            )
            ai_response = response.choices[0].message.content
        else:
            # Fallback response when API is not configured
            if user and user.get('medical_history'):
                conditions = ', '.join(user.get('medical_history', []))
                ai_response = f"""I'm here to help with general health information. Based on your medical history ({conditions}), I recommend:
                
                1. Monitor your symptoms carefully, especially considering your existing conditions
                2. Stay hydrated and get adequate rest
                3. Consult your healthcare professional for personalized advice
                4. Seek immediate medical attention if symptoms worsen or interact with your existing conditions
                
                Please note: This is general guidance only and not a substitute for professional medical consultation, especially given your medical history."""
            else:
                ai_response = """I'm here to help with general health information. For your specific concern, I recommend:
                
                1. Monitor your symptoms carefully
                2. Stay hydrated and get adequate rest
                3. Consult a healthcare professional for personalized advice
                4. Seek immediate medical attention if symptoms worsen
                
                Please note: This is general guidance only and not a substitute for professional medical consultation."""
        
        # Translate if needed
        if language != 'en':
            try:
                ai_response = translator.translate(ai_response, dest=language).text
            except:
                pass  # Continue with English if translation fails
        
        return ai_response
    except Exception as e:
        print(f"AI consultation error: {e}")
        return "Sorry, I'm experiencing technical difficulties. Please try again later or consult a healthcare professional directly."

def calculate_health_status(user):
    """Calculate user's health status based on medical history and conditions"""
    medical_history = user.get('medical_history', [])
    
    # Serious conditions that require immediate medical attention
    serious_conditions = [
        'diabetes', 'heart disease', 'cancer', 'kidney disease', 'liver disease',
        'stroke', 'heart attack', 'coronary artery disease', 'chronic kidney disease',
        'cirrhosis', 'heart failure', 'chronic obstructive pulmonary disease', 'copd',
        'tuberculosis', 'tb', 'hiv', 'aids', 'leukemia', 'lymphoma', 'brain tumor',
        'liver cancer', 'lung cancer', 'breast cancer', 'prostate cancer',
        'chronic liver disease', 'end stage renal disease', 'cardiomyopathy',
        'pulmonary embolism', 'deep vein thrombosis', 'aortic aneurysm'
    ]
    
    # Moderate conditions requiring monitoring
    moderate_conditions = [
        'hypertension', 'asthma', 'arthritis', 'thyroid', 'anxiety', 'depression',
        'high blood pressure', 'high cholesterol', 'osteoporosis', 'fibromyalgia',
        'migraines', 'sleep apnea', 'acid reflux', 'irritable bowel syndrome', 'ibs',
        'rheumatoid arthritis', 'osteoarthritis', 'hypothyroidism', 'hyperthyroidism',
        'bipolar disorder', 'schizophrenia', 'epilepsy', 'seizures', 'chronic pain',
        'psoriasis', 'eczema', 'crohn disease', 'ulcerative colitis', 'gallstones',
        'kidney stones', 'chronic fatigue syndrome', 'lupus', 'multiple sclerosis',
        'parkinson', 'alzheimer', 'dementia', 'glaucoma', 'cataracts'
    ]
    
    # Mild conditions that don't significantly affect daily life
    mild_conditions = [
        'allergies', 'seasonal allergies', 'mild asthma', 'occasional headaches',
        'minor joint pain', 'occasional insomnia', 'hay fever', 'sinusitis',
        'minor back pain', 'vitamin deficiency', 'iron deficiency', 'anemia'
    ]
    
    if not medical_history:
        return 'green'
    
    # Check for serious conditions
    for condition in serious_conditions:
        for hist in medical_history:
            if condition.lower() in hist.lower():
                return 'red'
    
    # Check for moderate conditions
    for condition in moderate_conditions:
        for hist in medical_history:
            if condition.lower() in hist.lower():
                return 'yellow'
    
    # Check for mild conditions
    for condition in mild_conditions:
        for hist in medical_history:
            if condition.lower() in hist.lower():
                return 'yellow'  # Even mild conditions warrant yellow status
    
    # If medical history exists but no specific conditions matched, assume yellow
    if medical_history:
        return 'yellow'
    
    # Default to green (healthy)
    return 'green'

def send_report_email(report_data):
    """Send community report via email to authorities"""
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['EMAIL_USER']
        msg['To'] = app.config['HEALTH_DEPARTMENT_EMAIL']
        msg['Subject'] = f"Health Report: {report_data['issue_title']}"
        
        body = f"""
        Health Issue Report
        
        Title: {report_data['issue_title']}
        Location: {report_data['location']}
        Severity: {report_data['severity']}
        Description: {report_data['description']}
        
        Submitted by User ID: {report_data['user_id']}
        Submitted at: {report_data['submitted_at']}
        
        This report was submitted through the MedAether platform.
        Please review and take appropriate action as necessary.
        
        Best regards,
        MedAether System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
        server.starttls()
        server.login(app.config['EMAIL_USER'], app.config['EMAIL_PASSWORD'])
        text = msg.as_string()
        server.sendmail(app.config['EMAIL_USER'], app.config['HEALTH_DEPARTMENT_EMAIL'], text)
        server.quit()
        
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/translate', methods=['POST'])
def translate_text():
    """Translate text to specified language"""
    data = request.get_json()
    text = data.get('text')
    target_language = data.get('target_language', 'en')
    
    try:
        translated = translator.translate(text, dest=target_language)
        return jsonify({'translated_text': translated.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adopt-plan', methods=['POST'])
def adopt_plan():
    """Adopt a health plan"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    plan_name = data.get('plan_name')
    
    # Add plan to user's adopted plans
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$addToSet': {'adopted_plans': plan_name}}
    )
    
    return jsonify({'success': True, 'message': f'{plan_name} adopted successfully'})

@app.route('/update-health-metrics', methods=['POST'])
def update_health_metrics():
    """Update user's health metrics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    # Update user's health metrics
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': data}
    )
    
    return jsonify({'success': True})

@app.route('/update-health-status', methods=['POST'])
def update_health_status_route():
    """Recalculate and update user's health status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    new_status = calculate_health_status(user)
    
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': {'health_status': new_status}}
    )
    
    return jsonify({'success': True, 'new_status': new_status})

@app.route('/change-password', methods=['POST'])
def change_password():
    """Change user's password"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if not check_password_hash(user['password'], current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    # Update password
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': {'password': generate_password_hash(new_password)}}
    )
    
    return jsonify({'success': True})

@app.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    """Upload user's profile picture"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'profile_picture' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['profile_picture']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    # In a real application, you would save the file to a storage service
    # For now, we'll just update the user record to indicate a picture was uploaded
    db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': {'profile_picture': True, 'profile_picture_uploaded': datetime.utcnow()}}
    )
    
    return jsonify({'success': True})

# Validation Functions
def validate_email(email):
    """Validate email format"""
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return email_regex.match(email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    return True, "Password is valid"

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return text
    # Remove potentially dangerous HTML tags
    allowed_tags = ['b', 'i', 'u', 'strong', 'em']
    return bleach.clean(text, tags=allowed_tags, strip=True)

def validate_age(age):
    """Validate age input"""
    try:
        age_int = int(age)
        return 1 <= age_int <= 150
    except (ValueError, TypeError):
        return False

def validate_health_metrics(data):
    """Validate health metrics data"""
    errors = []
    
    if 'current_weight' in data:
        try:
            weight = float(data['current_weight'])
            if not (20 <= weight <= 500):  # kg
                errors.append("Weight must be between 20-500 kg")
        except (ValueError, TypeError):
            errors.append("Invalid weight format")
    
    if 'height' in data:
        try:
            height = int(data['height'])
            if not (50 <= height <= 250):  # cm
                errors.append("Height must be between 50-250 cm")
        except (ValueError, TypeError):
            errors.append("Invalid height format")
    
    if 'blood_pressure' in data:
        bp = data['blood_pressure']
        if bp and not re.match(r'^\d{2,3}/\d{2,3}$', bp):
            errors.append("Blood pressure format should be XXX/XXX")
    
    if 'blood_sugar' in data:
        try:
            sugar = int(data['blood_sugar'])
            if not (30 <= sugar <= 500):  # mg/dL
                errors.append("Blood sugar must be between 30-500 mg/dL")
        except (ValueError, TypeError):
            errors.append("Invalid blood sugar format")
    
    return errors

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'].split(',')

# Error Handlers
# @app.errorhandler(CSRFError)
# def handle_csrf_error(e):
#     return render_template('error.html', 
#                          error_title="Security Error", 
#                          error_message="CSRF token missing or invalid. Please refresh the page and try again."), 400

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_title="Page Not Found", 
                         error_message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_title="Server Error", 
                         error_message="An internal server error occurred. Please try again later."), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error.html', 
                         error_title="Rate Limit Exceeded", 
                         error_message="You've made too many requests. Please wait before trying again."), 429

# Note: Rate limiting will be applied to existing ai-chat route

# Security Headers
@app.after_request
def add_security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # HTTPS redirect (commented out for development)
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Health check endpoint for deployment
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
