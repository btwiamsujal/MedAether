# MedAether - AI Driven Public Health Chatbot

MedAether is a comprehensive AI-powered public health platform that provides medical consultations, health management tools, community reporting, and multilingual support through both web and Telegram interfaces.

## 🌟 Features

### Core Features
- **AI-Powered Medical Consultations**: Get health advice using OpenAI's GPT models
- **Telegram Bot Integration**: Access health services through Telegram
- **Multilingual Support**: 8+ languages supported with Google Translate
- **Digital Health Card**: Color-coded health status tracking
- **Quick Health Solutions**: Instant remedies for common health problems
- **Personalized Health Plans**: Custom health and wellness programs
- **Community Health Reporting**: Report local health issues to authorities
- **User Profile Management**: Complete health profile with metrics tracking

### Technical Features
- **Security**: CSRF protection, input validation, rate limiting
- **Database**: MongoDB with proper indexing and validation
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **File Upload Support**: Profile pictures with validation
- **Email Integration**: Automated reporting to health authorities
- **Health Status Calculation**: Intelligent health assessment
- **Session Management**: Secure user authentication

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB (local or Atlas)
- OpenAI API Key (optional)
- Telegram Bot Token (optional)
- Email credentials (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/medaether.git
   cd medaether
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python init_database.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## 📋 Environment Configuration

### Required Variables
```env
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017/
FLASK_ENV=development
```

### Optional Variables
```env
# AI Integration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Email Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Health Authorities
HEALTH_DEPARTMENT_EMAIL=health.dept@city.gov
```

## 🧪 Testing Guide

### Database Testing

1. **Initialize test database**
   ```bash
   FLASK_ENV=development python init_database.py
   ```

2. **Verify collections and indexes**
   ```bash
   # Connect to MongoDB and run:
   use medaether
   show collections
   db.users.getIndexes()
   ```

### Web Application Testing

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Test user registration**
   - Navigate to `http://localhost:5000`
   - Click "Sign Up"
   - Register with test credentials
   - Verify email validation and password hashing

3. **Test authentication**
   - Login with registered credentials
   - Verify session management
   - Test logout functionality

4. **Test core features**
   - **Home Page**: Verify all links and information display
   - **AI Chat**: Test with/without OpenAI API key
   - **Quick Solutions**: Check health problem display
   - **Health Plans**: Verify plan information
   - **Community Reports**: Submit test report
   - **Digital Health Card**: Check QR code generation
   - **Profile**: Update user information

### Telegram Bot Testing

1. **Start the bot**
   ```bash
   cd telegram_bot
   python bot.py
   ```

2. **Test bot commands**
   - `/start` - Initial bot setup
   - `/help` - Help information
   - `/emergency` - Emergency contacts
   - `/language` - Language selection

3. **Test conversational features**
   - Send health-related questions
   - Test multilingual responses
   - Verify database storage of conversations

### API Endpoint Testing

Use tools like Postman or curl to test API endpoints:

```bash
# Health check
curl http://localhost:5000/health

# Translation API
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "target_language": "es"}'

# Health metrics update (requires authentication)
curl -X POST http://localhost:5000/update-health-metrics \
  -H "Content-Type: application/json" \
  -d '{"current_weight": 70, "height": 175}'
```

### Security Testing

1. **CSRF Protection**
   - Try submitting forms without CSRF tokens
   - Verify error handling

2. **Rate Limiting**
   - Make multiple rapid requests to AI chat
   - Verify rate limit responses

3. **Input Validation**
   - Submit invalid email formats
   - Test XSS prevention with HTML input
   - Test SQL injection attempts (should fail with MongoDB)

4. **Authentication**
   - Try accessing protected routes without login
   - Test session timeout

## 📁 Project Structure

```
MedAether/
├── app.py                  # Main Flask application
├── config.py              # Configuration management
├── init_database.py       # Database initialization
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── Procfile               # Heroku deployment
├── runtime.txt            # Python version
├── DEPLOYMENT.md          # Deployment guide
├── .env.template          # Environment variables template
├── static/
│   ├── css/style.css      # Custom styles
│   └── js/main.js         # JavaScript functions
├── templates/
│   ├── base.html          # Base template
│   ├── home.html          # Homepage
│   ├── login.html         # Login page
│   ├── signup.html        # Registration page
│   ├── ai_chat.html       # AI chat interface
│   ├── quick_solutions.html   # Health solutions
│   ├── health_plans.html  # Health plans
│   ├── community_reports.html # Community reporting
│   ├── digital_health_card.html # Health card
│   ├── profile.html       # User profile
│   └── error.html         # Error page
├── telegram_bot/
│   └── bot.py             # Telegram bot implementation
└── uploads/               # File upload directory
```

## 🔧 Development

### Adding New Features

1. **New Routes**: Add to `app.py` with proper authentication checks
2. **New Templates**: Create in `templates/` following the existing structure
3. **Database Changes**: Update `init_database.py` for new collections
4. **API Endpoints**: Add validation and error handling
5. **Telegram Commands**: Update `telegram_bot/bot.py`

### Code Style

- Follow PEP 8 guidelines
- Use descriptive function and variable names
- Add docstrings to all functions
- Include error handling and logging
- Validate all user inputs

### Testing New Features

1. **Unit Tests**: Write tests for individual functions
2. **Integration Tests**: Test feature workflows
3. **Security Tests**: Verify input validation and authentication
4. **Performance Tests**: Check database query performance
5. **User Experience Tests**: Test UI/UX flows

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Heroku
- Railway
- Render
- Google Cloud Platform
- Docker containers

### Quick Deployment Commands

**Heroku:**
```bash
heroku create medaether-app
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set MONGODB_URI="your-mongodb-uri"
git push heroku main
```

**Docker:**
```bash
docker build -t medaether .
docker run -p 5000:5000 medaether
```

## 📊 Monitoring and Maintenance

### Health Checks
- Database connectivity: `/health` endpoint
- Application performance monitoring
- Error rate tracking
- User activity analytics

### Database Maintenance
- Regular backups
- Index optimization
- Data cleanup routines
- Performance monitoring

### Security Updates
- Dependency updates
- Security patch application
- SSL certificate renewal
- API key rotation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper testing
4. Submit a pull request
5. Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions:
- Create an issue on GitHub
- Contact: support@medaether.com
- Documentation: See project wiki

## 🔗 Links

- **Live Demo**: [medaether.com](https://medaether.com)
- **API Documentation**: [api.medaether.com](https://api.medaether.com)
- **Telegram Bot**: [@medaether_bot](https://t.me/medaether_bot)

---

**Medical Disclaimer**: This application provides general health information only. Always consult qualified healthcare professionals for medical diagnosis, treatment, and advice. In case of emergency, contact local emergency services immediately.
