# MedAether Deployment Guide

This guide covers deploying MedAether to various cloud platforms.

## Prerequisites

1. **MongoDB Database**: Set up a MongoDB cluster (MongoDB Atlas recommended)
2. **API Keys**: Obtain required API keys:
   - OpenAI API key (for AI features)
   - Telegram Bot Token (for bot integration)
   - Email credentials (for community reports)

## Platform-Specific Deployment

### 1. Heroku Deployment

#### Setup Steps:
1. Install Heroku CLI
2. Create a new Heroku app
3. Set environment variables
4. Deploy the application

#### Commands:
```bash
# Login to Heroku
heroku login

# Create new app
heroku create medaether-app

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set MONGODB_URI="your-mongodb-connection-string"
heroku config:set OPENAI_API_KEY="your-openai-api-key"
heroku config:set TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
heroku config:set EMAIL_USER="your-email@gmail.com"
heroku config:set EMAIL_PASSWORD="your-email-password"
heroku config:set FLASK_ENV="production"

# Deploy
git add .
git commit -m "Initial deployment"
git push heroku main

# Scale the web dyno
heroku ps:scale web=1

# Enable Telegram bot (optional)
heroku ps:scale telegram_bot=1
```

### 2. Railway Deployment

#### Setup Steps:
1. Connect your GitHub repository to Railway
2. Configure environment variables
3. Deploy with automatic builds

#### Environment Variables to Set:
```
SECRET_KEY=your-secret-key-here
MONGODB_URI=your-mongodb-connection-string
OPENAI_API_KEY=your-openai-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-email-password
FLASK_ENV=production
PORT=5000
```

### 3. Render Deployment

#### Setup Steps:
1. Connect your repository to Render
2. Create a new Web Service
3. Configure build and start commands
4. Set environment variables

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
gunicorn app:app
```

### 4. Google Cloud Platform (Cloud Run)

#### Setup Steps:
1. Create a Dockerfile
2. Build and push to Google Container Registry
3. Deploy to Cloud Run

#### Sample Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

## Environment Variables

### Required Variables:
- `SECRET_KEY`: Flask secret key for session management
- `MONGODB_URI`: MongoDB connection string
- `FLASK_ENV`: Set to "production" for production deployment

### Optional Variables:
- `OPENAI_API_KEY`: For AI chat functionality
- `TELEGRAM_BOT_TOKEN`: For Telegram bot integration
- `EMAIL_USER`: Email for sending community reports
- `EMAIL_PASSWORD`: Email password/app password
- `SMTP_SERVER`: Email server (default: smtp.gmail.com)
- `SMTP_PORT`: Email server port (default: 587)

## MongoDB Setup (MongoDB Atlas)

1. Create a MongoDB Atlas account
2. Create a new cluster
3. Create a database user
4. Add connection IP addresses
5. Get the connection string
6. Replace `<password>` with your actual password in the connection string

Example connection string:
```
mongodb+srv://username:password@cluster.mongodb.net/medaether?retryWrites=true&w=majority
```

## Telegram Bot Setup

1. Create a new bot with @BotFather on Telegram
2. Get the bot token
3. Set the webhook URL (for production):
   ```
   https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://your-domain.com/webhook
   ```

## Post-Deployment Setup

1. **Initialize Database**: Run the database initialization script
2. **Test All Features**: Verify all functionality works
3. **Monitor Logs**: Check application logs for any issues
4. **Set up Health Checks**: Monitor application health

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to version control
2. **HTTPS**: Ensure your deployment uses HTTPS
3. **Database Security**: Use strong passwords and restrict IP access
4. **API Keys**: Rotate API keys regularly
5. **Rate Limiting**: Monitor and adjust rate limits as needed

## Troubleshooting

### Common Issues:

1. **MongoDB Connection Issues**:
   - Verify connection string format
   - Check IP whitelist in MongoDB Atlas
   - Ensure database user has proper permissions

2. **OpenAI API Issues**:
   - Verify API key is correct
   - Check API usage limits
   - Monitor API costs

3. **Email Issues**:
   - Use app-specific passwords for Gmail
   - Verify SMTP settings
   - Check spam/security settings

4. **Static Files Not Loading**:
   - Ensure static files are properly deployed
   - Check static file configurations

### Monitoring and Logs:

- **Heroku**: `heroku logs --tail`
- **Railway**: Check logs in Railway dashboard
- **Render**: View logs in Render dashboard

## Scaling Considerations

1. **Database**: Monitor MongoDB performance and scale as needed
2. **Application**: Use multiple dynos/instances for high traffic
3. **Caching**: Consider implementing Redis for session storage
4. **CDN**: Use a CDN for static asset delivery

## Backup Strategy

1. **Database Backups**: Set up automated MongoDB backups
2. **Code Repository**: Keep regular commits and tags
3. **Environment Variables**: Document all environment variables
4. **Configuration Files**: Backup any custom configurations

## Performance Optimization

1. **Database Indexing**: Add appropriate indexes to MongoDB collections
2. **Caching**: Implement caching for frequently accessed data
3. **Connection Pooling**: Configure database connection pooling
4. **Static Assets**: Optimize and compress static assets
5. **Rate Limiting**: Implement appropriate rate limiting

## Update and Maintenance

1. **Regular Updates**: Keep dependencies updated
2. **Security Patches**: Apply security updates promptly
3. **Monitoring**: Set up application and infrastructure monitoring
4. **Backup Testing**: Regularly test backup and restore procedures

For additional support or questions, refer to the platform-specific documentation or contact the development team.
