import logging
import os
import sys
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from googletrans import Translator
import asyncio
from pymongo import MongoClient
from datetime import datetime

# Add parent directory to path to import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')

# Initialize services
translator = Translator()
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# MongoDB connection
client = MongoClient(MONGODB_URI)
db = client.medaether

# Bot commands and keyboards
main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("🔍 Quick Health Solutions"), KeyboardButton("💊 Health Plans")],
    [KeyboardButton("🤖 AI Health Consultation"), KeyboardButton("📊 Health Status")],
    [KeyboardButton("📋 Community Reports"), KeyboardButton("🆘 Emergency Help")],
    [KeyboardButton("🌍 Change Language"), KeyboardButton("ℹ️ About MedAether")]
], resize_keyboard=True, persistent=True)

language_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("🇺🇸 English"), KeyboardButton("🇮🇳 Hindi")],
    [KeyboardButton("🇪🇸 Spanish"), KeyboardButton("🇫🇷 French")],
    [KeyboardButton("🇩🇪 German"), KeyboardButton("🇨🇳 Chinese")],
    [KeyboardButton("🔙 Back to Main Menu")]
], resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Save user to database
    user_data = {
        'telegram_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language_code': user.language_code,
        'created_at': datetime.utcnow(),
        'last_interaction': datetime.utcnow()
    }
    
    # Update or insert user
    db.telegram_users.update_one(
        {'telegram_id': user.id},
        {'$set': user_data},
        upsert=True
    )
    
    welcome_message = f"""
🩺 *Welcome to MedAether!* 🩺

Hi {user.first_name}! I'm your AI-powered health companion.

*What I can help you with:*
• 🤖 AI medical consultations
• 💊 Quick health solutions
• 📊 Health plans and guidance
• 📋 Community health reporting
• 🆘 Emergency assistance

*Features:*
• Multilingual support (8+ languages)
• Voice message support
• Quick health remedies
• Personalized health advice

⚠️ *Medical Disclaimer:* This bot provides general health information only. Always consult healthcare professionals for serious medical conditions.

👆 Use the menu below to get started!
"""
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=main_keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🆘 *MedAether Help* 🆘

*Available Commands:*
• /start - Start the bot
• /help - Show this help message
• /emergency - Get emergency contacts
• /language - Change language
• /status - Check your health status

*Quick Actions:*
• Send any health-related message for AI consultation
• Use voice messages for hands-free interaction
• Type symptoms for quick solutions
• Ask about health plans and advice

*Emergency:*
If you're experiencing a medical emergency, please contact your local emergency services immediately:
• 🚨 Emergency: 911
• 🏥 Poison Control: 1-800-222-1222

*Support:*
For technical support, contact: support@medaether.com
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def emergency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /emergency command"""
    emergency_text = """
🚨 *EMERGENCY CONTACTS* 🚨

*Immediate Emergency:*
📞 911 - Police/Fire/Medical Emergency

*Medical Emergency:*
🏥 Emergency Room - Go to nearest hospital
☎️ Poison Control: 1-800-222-1222

*Mental Health Crisis:*
🧠 National Suicide Prevention Lifeline: 988
💬 Crisis Text Line: Text HOME to 741741

*Important Notes:*
⚠️ If you're experiencing chest pain, difficulty breathing, severe bleeding, or any life-threatening symptoms, call 911 immediately!

⚠️ This bot cannot replace emergency medical services. For urgent medical situations, always contact professional emergency services.

🏥 For non-emergency medical advice, you can continue chatting with me or visit your local healthcare provider.
"""
    
    await update.message.reply_text(emergency_text, parse_mode='Markdown')

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    await update.message.reply_text(
        "🌍 *Select your preferred language:*",
        parse_mode='Markdown',
        reply_markup=language_keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user = update.effective_user
    message_text = update.message.text
    
    # Update last interaction
    db.telegram_users.update_one(
        {'telegram_id': user.id},
        {'$set': {'last_interaction': datetime.utcnow()}}
    )
    
    # Handle menu button presses
    if message_text == "🔍 Quick Health Solutions":
        await send_quick_solutions(update, context)
    elif message_text == "💊 Health Plans":
        await send_health_plans(update, context)
    elif message_text == "🤖 AI Health Consultation":
        await send_ai_consultation_prompt(update, context)
    elif message_text == "📊 Health Status":
        await send_health_status(update, context)
    elif message_text == "📋 Community Reports":
        await send_community_reports_info(update, context)
    elif message_text == "🆘 Emergency Help":
        await emergency_command(update, context)
    elif message_text == "🌍 Change Language":
        await language_command(update, context)
    elif message_text == "ℹ️ About MedAether":
        await send_about_info(update, context)
    elif message_text.startswith("🇺🇸") or message_text.startswith("🇮🇳") or message_text.startswith("🇪🇸"):
        await handle_language_selection(update, context)
    elif message_text == "🔙 Back to Main Menu":
        await update.message.reply_text(
            "🏠 Back to main menu!",
            reply_markup=main_keyboard
        )
    else:
        # Treat as health consultation request
        await handle_health_consultation(update, context)

async def send_quick_solutions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send quick health solutions"""
    solutions_text = """
💊 *QUICK HEALTH SOLUTIONS* 💊

*Common Problems & Remedies:*

🤒 *Fever*
• Medicine: Paracetamol 500mg (as prescribed)
• Home remedy: Rest, fluids, cool compress
• Precautions: Monitor temp, seek help if >3 days

🤧 *Common Cold*
• Medicine: Antihistamines (as prescribed)
• Home remedy: Warm salt water gargling, honey
• Precautions: Rest, avoid cold drinks

🤕 *Headache*
• Medicine: Paracetamol, Aspirin (as prescribed)
• Home remedy: Head massage, compress, sleep
• Precautions: Avoid stress, stay hydrated

🤢 *Stomach Ache*
• Medicine: Antacids, ORS (as prescribed)
• Home remedy: Ginger tea, BRAT diet
• Precautions: Light meals, avoid spicy food

😷 *Cough*
• Medicine: Cough syrup, lozenges (as prescribed)
• Home remedy: Honey with warm water, turmeric milk
• Precautions: Avoid cold beverages

💡 *Need more specific advice?* Just describe your symptoms and I'll provide personalized guidance!
"""
    
    await update.message.reply_text(solutions_text, parse_mode='Markdown')

async def send_health_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send health plans information"""
    plans_text = """
📅 *HEALTH PLANS* 📅

*Available Plans:*

🏋️ *Weight Gain Plan*
• Diet: High-calorie nutritious foods, proteins
• Exercise: Strength training 3x/week
• Lifestyle: Regular meals, adequate sleep

🍎 *Liver Care Plan*
• Diet: Low-fat, avoid alcohol, green vegetables
• Exercise: Moderate cardio, yoga, walking
• Lifestyle: Avoid processed foods, regular checkups

❤️ *Heart Health Plan*
• Diet: Low sodium, omega-3 rich foods
• Exercise: Cardio, brisk walking, swimming
• Lifestyle: No smoking, stress reduction

🩸 *Diabetes Management*
• Diet: Low glycemic foods, portion control
• Exercise: Daily 30-45 min activity
• Lifestyle: Glucose monitoring, medication compliance

💡 *Want a personalized plan?* Tell me your health goals and I'll create a custom plan for you!
"""
    
    await update.message.reply_text(plans_text, parse_mode='Markdown')

async def send_ai_consultation_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt for AI consultation"""
    consultation_text = """
🤖 *AI HEALTH CONSULTATION* 🤖

I'm ready to help with your health concerns!

*You can ask me about:*
• Symptoms and their possible causes
• Treatment recommendations
• Medicine information
• Health tips and lifestyle advice
• Disease prevention
• Mental health support

*How to get the best help:*
1. Describe your symptoms clearly
2. Mention your age and gender if relevant
3. Include any existing medical conditions
4. Ask specific questions

*Example questions:*
• "I have a headache and feel nauseous"
• "What foods are good for diabetes?"
• "How can I improve my sleep quality?"
• "I'm feeling anxious, what can help?"

💬 Just type your health question below, and I'll provide personalized advice!

🎤 You can also send voice messages for easier communication.
"""
    
    await update.message.reply_text(consultation_text, parse_mode='Markdown')

async def send_health_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send user's health status"""
    user = update.effective_user
    telegram_user = db.telegram_users.find_one({'telegram_id': user.id})
    
    if not telegram_user:
        await update.message.reply_text(
            "❌ No health profile found. Please register on our web platform first: https://medaether.com"
        )
        return
    
    # Get health status (this would be linked to web app user)
    health_status = telegram_user.get('health_status', 'green')
    
    status_text = f"""
📊 *YOUR HEALTH STATUS* 📊

👤 *Profile:*
• Name: {telegram_user.get('first_name', 'User')}
• Status: {"🟢 Healthy" if health_status == 'green' else "🟡 Moderate Issues" if health_status == 'yellow' else "🔴 Attention Needed"}

📈 *Recent Activity:*
• Last consultation: {telegram_user.get('last_interaction', 'Never').strftime('%Y-%m-%d') if isinstance(telegram_user.get('last_interaction'), datetime) else 'Recent'}
• Total consultations: {telegram_user.get('consultation_count', 0)}

💡 *Recommendations:*
• Regular health checkups
• Maintain healthy lifestyle
• Use our AI for health guidance

🌐 *For complete health profile, visit:* https://medaether.com
"""
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def send_community_reports_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send community reports information"""
    reports_text = """
📋 *COMMUNITY HEALTH REPORTS* 📋

*Help your community by reporting health issues:*

🏥 *What to report:*
• Disease outbreaks
• Water/air pollution affecting health
• Food poisoning incidents
• Environmental health hazards
• Public health concerns

📝 *How to report:*
1. Visit our web platform: https://medaether.com
2. Go to "Community Reports" section
3. Fill out the report form with details
4. Include location and evidence if possible

📧 *What happens next:*
• Reports are sent to health authorities
• Community gets notified of health issues
• Preventive measures can be taken

⚠️ *For immediate emergencies, call 911 directly!*

💬 You can also describe the issue here, and I'll guide you on the next steps.
"""
    
    await update.message.reply_text(reports_text, parse_mode='Markdown')

async def send_about_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send information about MedAether"""
    about_text = """
ℹ️ *ABOUT MEDAETHER* ℹ️

🩺 *MedAether* is an AI-driven public health chatbot designed to make healthcare accessible to everyone.

*Our Features:*
• 🤖 AI-powered medical consultations
• 💊 Quick solutions for common health problems
• 📅 Personalized health plans
• 📋 Community health reporting
• 🆔 Digital health cards
• 🌍 Multilingual support (8+ languages)

*Our Mission:*
To bridge the healthcare gap by providing instant, reliable health guidance and fostering community health awareness.

*Technology:*
• Advanced AI models for medical guidance
• Secure data handling and privacy protection
• Integration with health authorities
• Real-time translation capabilities

*Web Platform:* https://medaether.com
*Support:* support@medaether.com

🎯 *Join thousands of users* taking control of their health with MedAether!
"""
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    message_text = update.message.text
    user = update.effective_user
    
    language_map = {
        "🇺🇸 English": "en",
        "🇮🇳 Hindi": "hi",
        "🇪🇸 Spanish": "es",
        "🇫🇷 French": "fr",
        "🇩🇪 German": "de",
        "🇨🇳 Chinese": "zh"
    }
    
    selected_language = language_map.get(message_text)
    if selected_language:
        # Update user's language preference
        db.telegram_users.update_one(
            {'telegram_id': user.id},
            {'$set': {'preferred_language': selected_language}}
        )
        
        confirmation_text = "✅ Language updated successfully!"
        if selected_language != 'en':
            try:
                confirmation_text = translator.translate(confirmation_text, dest=selected_language).text
            except:
                pass
        
        await update.message.reply_text(
            confirmation_text,
            reply_markup=main_keyboard
        )

async def handle_health_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle health consultation requests"""
    user = update.effective_user
    message_text = update.message.text
    
    # Get user's preferred language
    telegram_user = db.telegram_users.find_one({'telegram_id': user.id})
    preferred_language = telegram_user.get('preferred_language', 'en') if telegram_user else 'en'
    
    try:
        # Get AI response
        ai_response = await get_ai_medical_advice(message_text, preferred_language)
        
        # Save consultation to database
        consultation_data = {
            'telegram_id': user.id,
            'user_message': message_text,
            'ai_response': ai_response,
            'language': preferred_language,
            'timestamp': datetime.utcnow()
        }
        db.telegram_consultations.insert_one(consultation_data)
        
        # Update consultation count
        db.telegram_users.update_one(
            {'telegram_id': user.id},
            {'$inc': {'consultation_count': 1}}
        )
        
        # Send response
        await update.message.reply_text(
            f"🤖 *MedAether AI Doctor:*\n\n{ai_response}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in health consultation: {e}")
        error_message = "😔 Sorry, I'm experiencing technical difficulties. Please try again in a moment."
        
        if preferred_language != 'en':
            try:
                error_message = translator.translate(error_message, dest=preferred_language).text
            except:
                pass
        
        await update.message.reply_text(error_message)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    user = update.effective_user
    
    await update.message.reply_text(
        "🎤 I received your voice message! However, voice processing is currently available only on our web platform.\n\n"
        "For voice consultations, please visit: https://medaether.com\n\n"
        "You can also type your question here, and I'll be happy to help! 😊"
    )

async def get_ai_medical_advice(message, language='en'):
    """Get medical advice from AI"""
    try:
        if OPENAI_API_KEY:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical AI assistant for MedAether, a public health chatbot. 
                        Provide helpful, accurate health advice and information. Always remind users to consult 
                        healthcare professionals for serious conditions. Keep responses concise but informative. 
                        Do not provide specific drug dosages without proper medical consultation. 
                        Focus on general health guidance, symptom information, and when to seek professional help."""
                    },
                    {"role": "user", "content": message}
                ],
                max_tokens=400
            )
            ai_response = response.choices[0].message.content
        else:
            # Fallback response
            ai_response = """I'm here to help with general health information. For your safety, please consult a qualified healthcare professional for personalized medical advice, especially for serious symptoms."""
        
        # Translate if needed
        if language != 'en':
            try:
                ai_response = translator.translate(ai_response, dest=language).text
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
        
        # Add disclaimer
        disclaimer = "\n\n⚠️ *Important:* This is general health information only. Always consult healthcare professionals for medical diagnosis and treatment."
        if language != 'en':
            try:
                disclaimer = translator.translate(disclaimer, dest=language).text
            except:
                pass
        
        return ai_response + disclaimer
        
    except Exception as e:
        logger.error(f"AI consultation error: {e}")
        return "Sorry, I'm experiencing technical difficulties. Please try again later or contact a healthcare professional."

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.warning(f'Update {update} caused error {context.error}')
    
    if update and update.message:
        await update.message.reply_text(
            "😔 Something went wrong. Please try again or contact support if the issue persists."
        )

def main():
    """Start the Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("emergency", emergency_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting MedAether Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()