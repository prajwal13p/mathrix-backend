# 🚀 Mathrix Backend API

AI-Powered Team Formation Platform Backend

## 🏗️ Architecture

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT with bcrypt
- **Deployment**: Render.com

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-backend-repo-url>
   cd mathrix-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database URL
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed Render.com deployment instructions.

## 📚 API Documentation

- **Swagger UI**: `/docs` (development only)
- **ReDoc**: `/redoc` (development only)
- **Health Check**: `/health`

## 🗄️ Database

The application uses PostgreSQL with the following main tables:
- `participants` - User accounts and skills
- `teams` - Team information and settings
- `team_requests` - Team join requests

## 🔧 Configuration

Key environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `DEBUG` - Enable debug mode
- `ENVIRONMENT` - Production/development environment

## 📁 Project Structure

```
mathrix-backend/
├── app/
│   ├── core/           # Database and config
│   ├── models/         # Database models
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic models
│   └── services/       # Business logic
├── alembic/            # Database migrations
├── render.yaml         # Render deployment config
├── Dockerfile          # Docker configuration
├── start.sh            # Production startup script
└── requirements.txt    # Python dependencies
```

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Health check
curl http://localhost:8000/health
```

## 📊 Monitoring

- Health check endpoint: `/health`
- Request timing headers
- Structured logging
- Database connection monitoring

## 🔒 Security

- JWT authentication
- Password hashing with bcrypt
- CORS configuration
- Environment variable protection
- Input validation with Pydantic

## 🚀 Deployment

This application is configured for deployment on Render.com with:
- Automatic database setup
- Health checks
- Production-ready configuration
- Docker support

## 📞 Support

For deployment help, see [DEPLOYMENT.md](./DEPLOYMENT.md)

---

**Built with ❤️ for Mathrix Team Formation Platform**
