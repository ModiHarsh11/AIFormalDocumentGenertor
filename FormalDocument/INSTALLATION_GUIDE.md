# Installation & Setup Guide

## Quick Start

### Prerequisites
- Python 3.9+ (Recommended: 3.11+)
- pip & virtualenv
- PostgreSQL 12+ (for production)
- Git

### 1. Clone the Repository
```bash
cd D:\BISAG\DocumentGenerator-main\DocumentGenerator-main
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

#### For Development
```bash
cd FormalDocument/ai_formal_generator
pip install -r requirements-dev.txt
```

#### For Production
```bash
cd FormalDocument/ai_formal_generator
pip install -r requirements-prod.txt
```

#### Minimal Installation (Core Only)
```bash
cd FormalDocument/ai_formal_generator
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the template
cp .env.example .env  # Create one if it doesn't exist

# Edit .env with your settings
# Set the following:
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.development
DJANGO_SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-2.5-flash-lite
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## System Dependencies Installation

### Windows
Install Microsoft C++ Build Tools:
```bash
# Using chocolatey
choco install visualstudio2019buildtools

# Or download from Microsoft manually
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
  libpq-dev \
  python3-dev \
  build-essential \
  libcairo2-dev \
  libpango-1.0-0 \
  libpango-cairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info \
  libpq5
```

### macOS
```bash
brew install \
  libpq \
  cairo \
  pango \
  gdk-pixbuf \
  libffi \
  postgresql
```

---

## Requirements Files Explanation

### requirements.txt (Base)
**Contains**: Core dependencies for web framework, database, AI/LLM, document processing
**Use**: All environments (development, staging, production)
**Size**: ~10 packages (minimal footprint)

### requirements-dev.txt (Development)
**Contains**: Base requirements + Testing, linting, debugging, documentation tools
**Use**: Local development and CI/CD testing
**Includes**: pytest, black, flake8, django-debug-toolbar, etc.
**Size**: ~25 packages

### requirements-prod.txt (Production)
**Contains**: Base requirements + WSGI servers, caching, monitoring, error tracking
**Use**: Production deployment environments
**Includes**: gunicorn, redis, sentry, newrelic, etc.
**Size**: ~20 packages

---

## Deployment Instructions

### Production via Gunicorn & Nginx

#### 1. Install Production Dependencies
```bash
pip install -r requirements-prod.txt
```

#### 2. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### 3. Run Gunicorn
```bash
# Basic (4 workers)
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  ai_formal_generator.wsgi:application

# With environment file
export DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.production
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  ai_formal_generator.wsgi:application
```

#### 4. Configure Nginx
```nginx
upstream django_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /path/to/static/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  libpq-dev \
  build-essential \
  libcairo2-dev \
  libpango-1.0-0 \
  libpango-cairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY FormalDocument/ai_formal_generator/requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "ai_formal_generator.wsgi:application"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: neondb
      POSTGRES_USER: neondb_owner
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn --workers 4 --bind 0.0.0.0:8000 ai_formal_generator.wsgi:application
    ports:
      - "8000:8000"
    environment:
      DJANGO_SETTINGS_MODULE: ai_formal_generator.settings.production
      DATABASE_URL: postgresql://neondb_owner:${DB_PASSWORD}@db:5432/neondb
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=generator --cov-report=html
```

### Run Specific Test File
```bash
pytest generator/tests.py -v
```

---

## Troubleshooting

### ImportError: No module named 'weasyprint'
**Solution**: Install system dependencies
```bash
# Windows: Install Visual C++ Build Tools
# Linux: sudo apt-get install libcairo2-dev libpango-1.0-0 libpango-cairo-1.0-0
# Mac: brew install cairo pango
```

### PostgreSQL Connection Error
**Solution**: Check credentials in .env
```bash
# Test connection
psql -h 52.220.170.93 -U neondb_owner -d neondb -c "SELECT 1;"
```

### Google Genai API Error
**Solution**: Verify API key
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Test API access
python -c "from google import genai; client = genai.Client(api_key='YOUR_KEY')"
```

### Static Files Not Found in Production
**Solution**: Collect static files
```bash
python manage.py collectstatic --noinput --clear
```

---

## Performance Optimization

### Database Optimization
```bash
# Create indexes
python manage.py migrate

# Monitor queries
# Enable django-debug-toolbar in development
# Use django-extensions: python manage.py shell_plus
```

### Caching Setup
```python
# In settings/production.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### Async Task Processing
```bash
# Install Celery
pip install celery django-celery-beat

# Run Celery worker
celery -A ai_formal_generator worker -l info

# Run Celery beat
celery -A ai_formal_generator beat -l info
```

---

## Next Steps

1. **Read Documentation**: Check `/docs` folder for detailed guides
2. **Configure Environment**: Set up `.env` with your API keys
3. **Run Migrations**: `python manage.py migrate`
4. **Test Generation**: Try generating a document via the UI
5. **Setup Monitoring**: Configure Sentry or New Relic for production
6. **Deploy**: Follow Docker or Nginx instructions above

---

**For more information, see:**
- [TECHNOLOGY_STACK.md](../TECHNOLOGY_STACK.md)
- [Project Documentation](../docs/README.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
