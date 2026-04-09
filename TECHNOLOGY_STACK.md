# DocumentGenerator - Technology Stack Analysis

## Project Overview
**DocumentGenerator** is a Django-based formal document generation system for BISAG-N that leverages Google Generative AI (Gemini) to generate government documents (Office Orders, Circulars, Policy Documents, Notices).

---

## Core Technology Stack

### 1. **Web Framework**
| Technology | Version | Purpose |
|---|---|---|
| **Django** | 4.2.26 - 4.2.x | Web framework, ORM, Admin panel, Authentication |
| **Python** | 3.9+ (recommended 3.11+) | Programming language |
| **Gunicorn** | Latest | WSGI HTTP Server (for production) |
| **WhiteNoise** | Latest | Static file serving in production |

### 2. **Database**
| Technology | Version | Purpose |
|---|---|---|
| **PostgreSQL** | 12+ | Primary database (Neon Cloud PostgreSQL) |
| **SQLite3** | Built-in | Local development / fallback |
| **psycopg2** | Latest | PostgreSQL adapter for Python |

### 3. **AI/LLM Stack**
| Technology | Version | Purpose |
|---|---|---|
| **Google Generative AI** | 1.0 - 2.x | Gemini API for document generation |
| **LangChain Core** | 0.3.x | Prompt engineering & template management |
| **Gemini Models Used** | - | gemini-2.5-flash-lite (primary), gemini-2.0-flash (fallback) |

### 4. **Document Generation & Processing**
| Technology | Version | Purpose |
|---|---|---|
| **python-docx** | 1.1.2 | Word (.docx) document generation |
| **WeasyPrint** | 68.0+ | HTML to PDF conversion |
| **ReportLab** | 4.2.0 | Advanced PDF generation |
| **PyPDF** | 4.0.0+ | PDF manipulation & merging |
| **pdf2image** | 1.17.0 | PDF to image conversion |
| **Pillow** | 10.4.0 - 11.x | Image processing |

### 5. **Frontend & Forms**
| Technology | Version | Purpose |
|---|---|---|
| **Django Crispy Forms** | Latest | Django form rendering |
| **Crispy Bootstrap5** | Latest | Bootstrap 5 template pack |
| **Bootstrap 5** | 5.x | CSS Framework |
| **Jinja2** | Built-in (Django) | Template engine |

### 6. **Environment & Configuration**
| Technology | Version | Purpose |
|---|---|---|
| **python-dotenv** | 1.0.1 | Environment variable management |
| **Django Settings** | Multiple environments | development.py, production.py, base.py |

### 7. **Authentication & Security**
| Technology | Version | Purpose |
|---|---|---|
| **Django Auth** | Built-in | User authentication |
| **CSRF Protection** | Built-in | Cross-Site Request Forgery protection |
| **Django-admin** | Built-in | Admin panel |
| **SSL/TLS** | Production | HTTPS enforcement |

---

## Development & Deployment Stack

### 8. **Production-Ready Configuration**
- **Security Headers**: HSTS, X-Frame-Options, Content-Type-Nosniff
- **SSL/TLS**: HTTPS redirect enabled
- **Database Sessions**: Database-backed session storage
- **Static Files WhiteNoise**: Production-optimized static file serving
- **Environment Variables**: All secrets from .env

### 9. **Development Tools (Recommended)**
| Tool | Version | Purpose |
|---|---|---|
| **pytest** | Latest | Unit testing framework |
| **pytest-django** | Latest | Django testing plugin |
| **black** | Latest | Code formatter |
| **flake8** | Latest | Code linter |
| **isort** | Latest | Import sorting |
| **python-decouple** | Latest | Additional env config (optional) |

---

## Version Requirements Summary

### Production Environment (Current)
```
Django >= 4.2.26, < 4.3
google-genai >= 1.0, < 2
python-dotenv == 1.0.1
reportlab == 4.2.0
python-docx == 1.1.2
weasyprint >= 68.0.0
pypdf >= 4.0.0
pdf2image == 1.17.0
Pillow >= 10.4.0, < 12
langchain-core >= 0.3, < 0.4
django-crispy-forms (latest with Bootstrap5 support)
crispy-bootstrap5 (latest)
psycopg2-binary >= 2.9.0 (for PostgreSQL)
```

---

## System Dependencies (for PDF/Image Processing)

### Windows
- **Visual C++ Build Tools** (for weasyprint compilation)
- **Python development headers**

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install \
  libpq-dev \
  python3-dev \
  build-essential \
  libcairo2-dev \
  libpango-1.0-0 \
  libpango-cairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info
```

### macOS
```bash
brew install \
  libpq \
  cairo \
  pango \
  gdk-pixbuf \
  libffi
```

---

## Database Architecture

### Primary DB: PostgreSQL (Neon Cloud)
- **Host**: 52.220.170.93 (IP - bypasses corporate DNS)
- **Port**: 5432
- **Database**: neondb
- **User**: neondb_owner
- **SSL Mode**: Required
- **Connection Pooling**: Neon Pooler with endpoint routing
- **Connection Max Age**: 600 seconds

### Fallback DB: SQLite3
- Used for local development
- Location: `db.sqlite3` in project root

---

## Models

### Core Data Models
1. **DocumentLog** (Legacy) - Audit trail for generated documents
2. **GeneratedDocument** - Primary document storage with all metadata
3. **UserProfile** - User profile extensions
4. **User** (Django built-in) - Authentication

### Document Types Supported
- Office Order
- Circular
- Policy Document
- Notice / Advertisement

### Languages Supported
- English (en)
- Hindi (hi)

---

## Configuration Files & Settings

| File | Purpose |
|---|---|
| `settings/base.py` | Shared configuration (all environments) |
| `settings/development.py` | Local development overrides |
| `settings/production.py` | Production security & deployment settings |
| `.env` | Environment variables (secrets, API keys, DB credentials) |

### Key Environment Variables
```
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.development
DJANGO_SECRET_KEY=<secure-random-key>
GEMINI_API_KEY=<google-genai-api-key>
LLM_MODEL=gemini-2.5-flash-lite
DB_ENGINE=django.db.backends.postgresql
DB_HOST=52.220.170.93
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=<password>
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## API Integration

### Google Gemini API
- **Primary Model**: gemini-2.5-flash-lite
- **Fallback Chain**: Multiple Gemini 2.0 models for redundancy
- **Generation Config**: temperature=0.3, max_tokens=1024
- **Safety Filters**: Enabled (content validation)

### Error Handling
- Automatic model fallback on quota/unavailability
- Rate limit detection and handling
- Response validation and sanitization

---

## Deployment Architecture

### Recommended Stack
1. **Container**: Docker (optional)
2. **Web Server**: Nginx (reverse proxy)
3. **WSGI Server**: Gunicorn (4-8 workers)
4. **Database**: PostgreSQL (Neon)
5. **Cache**: Redis (optional, for sessions/caching)
6. **Static Files**: WhiteNoise or S3/CDN
7. **Platform**: AWS, Azure, Heroku, or on-premises VPS

### Production Features Enabled
- HTTPS/SSL Redirect
- HSTS Headers
- Secure Cookies
- Database Connection Pooling
- Database Connection Health Checks
- Session Database Backend

---

## Logging Configuration

- **Format**: Verbose with timestamp, level, name, message
- **Console Output**: Default handler
- **Log Levels**:
  - Root: INFO
  - Django: INFO  
  - Generator: DEBUG
- **Handlers**: StreamHandler (console)

---

## Project Statistics

| Metric | Value |
|---|---|
| **Main Python Packages** | 10+ core dependencies |
| **Document Types** | 4 (Office Order, Circular, Policy, Notice) |
| **Languages Supported** | 2 (English, Hindi) |
| **Database Models** | 5+ models |
| **Views/Endpoints** | 15+ views |
| **API Models (Gemini Fallback)** | 6 models with dynamic fallback |

---

## Notes

1. **WeasyPrint Dependencies**: Requires system libraries for HTML rendering (Cairo, Pango)
2. **Google Genai**: Requires valid API key from Google Cloud Console
3. **PostgreSQL**: Production uses Neon PostgreSQL pooler with special endpoint configuration
4. **Python Version**: Recommended 3.11+ for best compatibility
5. **CORS**: Not currently configured (backend-only API)
6. **Async**: Uses synchronous views (no async support currently)
7. **Caching**: No caching layer configured (potential optimization opportunity)
8. **Error Tracking**: No error tracking service configured (Sentry recommended)

---

**Project Version**: BISAG-N Document Generator (Phase 12)
