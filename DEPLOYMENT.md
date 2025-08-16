# 🚀 Mathrix API Deployment Guide for Render.com

## 📋 Prerequisites

- [Render.com](https://render.com) account
- Git repository with your code
- PostgreSQL database (Render provides this)

## 🗄️ Database Setup

### 1. Create PostgreSQL Database on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `mathrix-db`
   - **Database**: `mathrix`
   - **User**: `mathrix`
   - **Plan**: Free (for testing)
4. Click "Create Database"
5. Copy the **Internal Database URL** (you'll need this)

### 2. Environment Variables
Set these in your Render service:

```bash
# Database
DATABASE_URL=postgresql://mathrix:password@host:port/mathrix

# Security
SECRET_KEY=your-super-secret-key-here
DEBUG=false
ENVIRONMENT=production

# CORS (Update with your frontend URL)
ALLOWED_ORIGINS=https://mathrix-frontend.onrender.com,http://localhost:3000

# Optional: Email settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🌐 Backend API Deployment

### Option 1: Automatic Deployment with render.yaml

1. **Push your code** to GitHub/GitLab
2. **Connect repository** to Render:
   - Click "New +" → "Blueprint"
   - Connect your Git repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

### Option 2: Manual Deployment

1. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Configure:
     - **Name**: `mathrix-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `./start.sh`

2. **Set Environment Variables** (see above)

3. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy automatically

## 🔧 Configuration Files

### render.yaml
```yaml
services:
  - type: web
    name: mathrix-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: ./start.sh
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: DATABASE_URL
        fromDatabase:
          name: mathrix-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
```

### Dockerfile (Alternative)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📱 Frontend Deployment

### 1. Create Static Site
1. Click "New +" → "Static Site"
2. Connect your frontend repository
3. Configure:
   - **Name**: `mathrix-frontend`
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist` or `build`

### 2. Update API URLs
Update your frontend to use the new backend URL:
```javascript
// Change from localhost:8000 to your Render URL
const API_BASE_URL = 'https://mathrix-backend.onrender.com';
```

## 🔍 Health Checks

Your API includes health check endpoints:
- **Health**: `GET /health`
- **Root**: `GET /`
- **Docs**: `GET /docs` (only in debug mode)

## 📊 Monitoring

### Render Dashboard
- **Logs**: View real-time application logs
- **Metrics**: CPU, memory, and response time
- **Deployments**: Track deployment history

### Custom Monitoring
```bash
# Health check
curl https://mathrix-backend.onrender.com/health

# API status
curl https://mathrix-backend.onrender.com/
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` environment variable
   - Verify database is running
   - Check firewall settings

2. **Build Failed**
   - Check `requirements.txt` for typos
   - Verify Python version compatibility
   - Check build logs for specific errors

3. **Service Won't Start**
   - Check start command in `start.sh`
   - Verify port configuration
   - Check application logs

### Debug Mode
Set `DEBUG=true` temporarily to:
- Enable detailed error messages
- Show API documentation
- Enable hot reloading

## 🔒 Security Considerations

1. **Environment Variables**: Never commit secrets to Git
2. **CORS**: Restrict allowed origins in production
3. **Rate Limiting**: Consider adding rate limiting middleware
4. **HTTPS**: Render provides SSL certificates automatically

## 📈 Scaling

### Free Tier Limits
- **Backend**: 750 hours/month
- **Database**: 90 days retention
- **Bandwidth**: 100GB/month

### Upgrade Path
- **Backend**: $7/month for always-on
- **Database**: $7/month for persistent storage

## 🎯 Next Steps

1. **Deploy backend** using the guide above
2. **Update frontend** with new API URLs
3. **Deploy frontend** to Render
4. **Test thoroughly** in production environment
5. **Monitor performance** and logs
6. **Set up custom domain** (optional)

## 📞 Support

- **Render Docs**: [docs.render.com](https://docs.render.com)
- **Community**: [community.render.com](https://community.render.com)
- **Status**: [status.render.com](https://status.render.com)

---

**Happy Deploying! 🚀**
