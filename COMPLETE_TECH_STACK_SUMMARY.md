# BISAG-N DocumentGenerator - Complete Technology Stack Summary

**Project**: AI-Powered Formal Document Generator for Government  
**Version**: Phase 12 (2026)  
**Status**: Production Ready  

---

## Executive Summary

The BISAG-N DocumentGenerator is a Django-based web application that leverages Google's Gemini AI to generate formal government documents (Office Orders, Circulars, Policies) in English and Hindi. The stack is production-ready with comprehensive document processing, secure database integration, and modern web technologies.

### Key Metrics
- **Total Core Dependencies**: 11 packages
- **Development Dependencies**: 15+ packages  
- **Production Dependencies**: 10+ packages
- **Lines of Code**: Custom prompt & document handling
- **Document Types**: 4 (Office Order, Circular, Policy, Notice)
- **Languages**: 2 (English, Hindi)
- **Database**: PostgreSQL (Cloud + Local SQLite)

---

## Complete Technology Stack

### 1. Backend Framework & Runtime
```
┌─────────────────────────────────────────┐
│ Python 3.9+ (Recommended: 3.11+)       │
│ - Modern async/await support            │
│ - Type hints support                    │
│ - Security updates                      │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Django 4.2.26 - 4.2.x (LTS)            │
│ - Web framework                         │
│ - ORM & database migration              │
│ - Admin panel                           │
│ - Authentication & authorization        │
└─────────────────────────────────────────┘
```

### 2. Database Layer
```
Production:
  PostgreSQL (Neon Cloud)
  ├─ Host: 52.220.170.93
  ├─ Port: 5432
  ├─ Connection Pool: Neon Pooler
  └─ SSL: Required
       ↓
  psycopg2-binary (Python Driver)

Development:
  SQLite3 (local file)
```

### 3. AI/LLM Integration
```
Request ──→ google-genai SDK ──→ Gemini API
               │
        LangChain Core
               │
        ┌──────┴──────┬──────────┬──────────┐
        ↓             ↓          ↓          ↓
   Office Order   Circular    Policy     Notice
   (Templates)    (Templates) (Templates) (Templates)
        │             │          │          │
   English/Hindi  English/Hindi English/Hindi English/Hindi
        │             │          │          │
        └──────────────┴──────────┴──────────┘
               ↓
       Sanitization & Validation
               ↓
       Return Generated Text
```

### 4. Document Processing Pipeline
```
User Input ──→ AI Generation ──→ Content Validation
                                      ↓
        ┌─────────────────────────────┼─────────────────────────────┐
        ↓                             ↓                             ↓
   python-docx               weasyprint                    reportlab
   (.docx export)          (PDF export)               (Advanced PDF)
        ↓                             ↓                             ↓
      Format                  HTML→PDF                    Tables/Charts
      Tables                  Rendering                    Graphics
      Styles                  CSS Support
```

### 5. Frontend Stack
```
User Interface
    ↓
Django Templates (Jinja2)
    ↓
Crispy Forms + Bootstrap5
    ├─ Responsive design
    ├─ Form handling & validation
    └─ User authentication UI
    ↓
Static Files (CSS, JS, Images)
    ↓
WhiteNoise (Production)
```

### 6. Security Stack
```
┌──────────────────────────────────────┐
│ Django Security Features             │
├──────────────────────────────────────┤
│ ✓ CSRF Protection                   │
│ ✓ SQL Injection Prevention           │
│ ✓ XSS Protection                     │
│ ✓ Secure Password Hashing            │
│ ✓ Session Management                 │
│ ✓ HTTPS/SSL Support                  │
│ ✓ HSTS Headers                       │
│ ✓ Secure Cookies                     │
└──────────────────────────────────────┘

Environment Secrets
    ├─ GEMINI_API_KEY
    ├─ DJANGO_SECRET_KEY
    ├─ DB_PASSWORD
    └─ ALLOWED_HOSTS
```

---

## Detailed Version Requirements

### Core Production Stack
| Component | Package | Version | Purpose |
|-----------|---------|---------|---------|
| **Framework** | Django | 4.2.26-4.3 | Web framework |
| **Runtime** | Python | 3.9+ | Programming language |
| **Database Driver** | psycopg2-binary | 2.9-3.x | PostgreSQL adapter |
| **Environment** | python-dotenv | 1.0.1 | Config management |
| **LLM API** | google-genai | 1.0-2.x | Gemini API client |
| **Prompt Engine** | langchain-core | 0.3-0.4 | Prompt templates |
| **Word Export** | python-docx | 1.1.2 | .docx generation |
| **HTML to PDF** | weasyprint | 68.0+ | PDF rendering |
| **PDF Processing** | reportlab | 4.2.0 | Advanced PDF |
| **PDF Utility** | pypdf | 4.0.0+ | PDF manipulation |
| **PDF to Image** | pdf2image | 1.17.0 | Image conversion |
| **Image Library** | Pillow | 10.4-11.x | Image processing |
| **Forms** | django-crispy-forms | 2.0+ | Form rendering |
| **Styling** | crispy-bootstrap5 | 2.0+ | Bootstrap 5 UI |

### Development Stack
```
Testing              Code Quality         Development Tools
├─ pytest 7.4+       ├─ black 23+          ├─ django-extensions 3.2+
├─ pytest-django     ├─ flake8 6.0+        ├─ django-debug-toolbar 4.0+
├─ pytest-cov 4.1+   ├─ pylint 2.17+       ├─ ipython 8.0+
├─ factory-boy 3.3+  ├─ isort 5.12+        └─ django-stubs 4.2+
└─ faker 19.0+       └─ bandit 1.7.5+
```

### Production Stack (Optional)
```
WSGI Servers         Caching              Monitoring
├─ gunicorn 21+      ├─ redis 5.0+         ├─ sentry-sdk 1.30+
└─ whitenoise 6.5+   └─ django-redis 5.3+ └─ newrelic 8.0+
```

---

## Requirements Files Structure

```
FormalDocument/
├── requirements.txt                    (Core - 11 packages)
│   └── Base dependencies for all environments
│
├── ai_formal_generator/
│   ├── requirements.txt                (Duplicated core)
│   ├── requirements-dev.txt            (Dev + Core - 26 packages)
│   │   └── Testing, linting, debugging
│   │
│   └── requirements-prod.txt           (Prod + Core - 21 packages)
│       └── WSGI, caching, monitoring
```

### Installation Commands

```bash
# Minimal (core only)
pip install -r FormalDocument/ai_formal_generator/requirements.txt

# Development
pip install -r FormalDocument/ai_formal_generator/requirements-dev.txt

# Production
pip install -r FormalDocument/ai_formal_generator/requirements-prod.txt
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser (HTTP/HTTPS)               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Nginx/Reverse Proxy (Production)              │
├─────────────────────────────────────────────────────────────┤
│ • SSL/TLS Termination (HTTPS)                              │
│ • Static file serving (WhiteNoise)                         │
│ • Load balancing (multiple workers)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│         Gunicorn WSGI Application Server                   │
│  (4-8 worker processes)                                    │
├─────────────────────────────────────────────────────────────┤
│ Django Application                                          │
│ ├─ Views & URL Routing                                    │
│ ├─ Authentication & Permissions                           │
│ ├─ Form Handling & Validation                             │
│ └─ Business Logic                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼─────┐
    │ Database │    │AI API   │    │ Caching  │
    │          │    │         │    │          │
    │ Neon DB  │    │ Gemini  │    │ Redis    │
    │          │    │         │    │          │
    └──────────┘    └─────────┘    └──────────┘
```

---

## Configuration & Environment

### Development Environment
```
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASES: SQLite3 or local PostgreSQL
```

### Production Environment
```
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.production
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
DATABASES: PostgreSQL (Neon Cloud)
```

---

## Data Models

### Core Models
1. **User** (Built-in Django)
   - Authentication, permissions

2. **UserProfile** (Custom)
   - Extended user information

3. **DocumentLog** (Legacy)
   - Audit trail for documents

4. **GeneratedDocument** (Primary)
   - Full document storage with metadata
   - Editable fields
   - Version tracking

### Document Types
- Office Order (office)
- Circular (circular)  
- Policy (policy)
- (Notice/Advertisement - via advertisement app)

### Languages
- English (en)
- Hindi (hi)

---

## API Integration Points

### 1. Google Gemini API
```
Endpoint: https://generativelanguage.googleapis.com
Models: 
  - Primary: gemini-2.5-flash-lite
  - Fallback 1: gemini-2.0-flash
  - Fallback 2-6: Other Gemini models
Configuration:
  - Temperature: 0.3
  - Max tokens: 1024
  - Safety filters: Enabled
```

### 2. Database Access
```
PostgreSQL: 52.220.170.93:5432 (Neon Cloud)
Connection: SSL required
Pool: Neon Pooler (connection optimization)
```

### 3. Static File Serving
```
Development: Django development server
Production: WhiteNoise or CDN
Location: /static/
```

---

## Performance Characteristics

### Startup Time
- Cold start: 3-5 seconds
- Warm start: 1-2 seconds
- First request: 2-4 seconds

### Response Times
- Document generation: 5-30 seconds (API dependent)
- PDF export: 2-5 seconds
- Page render: 200-500ms

### Resource Usage
- Memory per worker: 150-250 MB
- Typical request memory: 10-20 MB
- Database connections: 1-3 per request

### Scalability
- Horizontal: Add more Gunicorn workers
- Vertical: Increase server resources
- Database: Neon auto-scaling
- Caching: Redis for session/query caching

---

## Security Considerations

### Authentication
- Django built-in authentication
- Password hashing: PBKDF2 (default)
- Session management: Database-backed (production)

### HTTPS/SSL
- Forced in production (SECURE_SSL_REDIRECT)
- HSTS headers enabled
- Secure cookies enforced

### API Key Management
- GEMINI_API_KEY: Environment variable only
- DJANGO_SECRET_KEY: Secure random generation
- Database credentials: .env file (never committed)

### Input Validation
- Django form validation
- Prompt sanitization
- Output validation (AI response checking)

---

## Monitoring & Logging

### Logging
- Console output (default)
- Configurable per environment
- Django: INFO level
- Generator: DEBUG level (dev), INFO (prod)

### Monitoring Tools (Optional)
- Sentry: Error tracking
- New Relic: Performance monitoring
- Datadog: Infrastructure monitoring
- Django Debug Toolbar: Development debugging

---

## Upgrade Path

### Minor Version Updates
```bash
pip install --upgrade "Django>=4.2.26,<4.3"
python manage.py migrate
```

### Major Version Prerequisites
- Read release notes
- Test in development
- Backup database
- Plan maintenance window
- Update requirements.txt
- Run full test suite

### Version Roadmap
- Python: 3.11 → 3.12 (2024-2025)
- Django: 4.2 → 5.x (2025-2026)
- Gemini: Current → Future models

---

## Support & Documentation

### Internal Resources
- [TECHNOLOGY_STACK.md](./TECHNOLOGY_STACK.md) - Detailed tech stack
- [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Setup instructions
- [DEPENDENCY_ANALYSIS.md](./DEPENDENCY_ANALYSIS.md) - Dependency details
- [/docs](./docs/) - Project documentation

### External Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Google GenAI SDK](https://ai.google.dev/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [WeasyPrint Docs](https://doc.courtbouillon.org/weasyprint/stable/)

---

## Key Contacts & Maintainers

- **Project**: BISAG-N DocumentGenerator
- **Maintained By**: BISAG-N Development Team
- **Last Updated**: April 6, 2026
- **Next Review**: Q3 2026

---

## Change Log

### v12.0 (Current)
- ✅ Complete technology stack analysis
- ✅ Optimized requirements.txt with documentation
- ✅ Separated dev/prod requirements
- ✅ Created installation guide
- ✅ Detailed dependency analysis
- ✅ Production deployment guidelines

### v11.0 (Previous)
- Production optimization phase
- UX enhancements
- Security hardening

---

**This document serves as the single source of truth for the BISAG-N DocumentGenerator technology stack and should be updated whenever dependencies or architecture changes occur.**
