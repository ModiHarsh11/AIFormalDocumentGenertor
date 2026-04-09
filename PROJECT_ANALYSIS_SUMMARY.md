# Project Analysis & Requirements Summary - Visual Reference

## 📊 Complete Technology Stack at a Glance

```
┌──────────────────────────────────────────────────────────────────────────┐
│                  BISAG-N DocumentGenerator Stack                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  LAYER 1: Runtime                                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Python 3.9+ (Recommended: 3.11+)                                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  LAYER 2: Web Framework & ORM                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Django 4.2.26 - 4.2.x (LTS)                                       │ │
│  │ - Admin Panel                                                      │ │
│  │ - Authentication                                                   │ │
│  │ - ORM & Migrations                                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  LAYER 3: Database                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ PostgreSQL (Production: Neon Cloud)                               │ │
│  │ psycopg2-binary 2.9+                                              │ │
│  │ SQLite3 (Development)                                             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  LAYER 4: AI/LLM Integration                                            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ google-genai 1.0-2.x                                              │ │
│  │ langchain-core 0.3-0.4                                            │ │
│  │ Gemini Models (Multi-model fallback)                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  LAYER 5: Document Processing                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ Word Export:    python-docx 1.1.2                                 │ │
│  │ PDF Generation: weasyprint 68.0+, reportlab 4.2.0                 │ │
│  │ PDF Tools:      pypdf 4.0.0+, pdf2image 1.17.0                    │ │
│  │ Images:         Pillow 10.4.0-11.x                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  LAYER 6: Frontend & Forms                                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ django-crispy-forms 2.0+                                          │ │
│  │ crispy-bootstrap5 2.0+                                            │ │
│  │ Bootstrap 5 (CSS Framework)                                       │ │
│  │ Jinja2 (Template Engine)                                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  LAYER 7: Configuration & Environment                                   │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ python-dotenv 1.0.1                                               │ │
│  │ Environment Variables Management                                  │ │
│  │ Settings: base.py, development.py, production.py                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Dependencies Overview

### Core Production Dependencies (11 packages)
```
✓ Django                    4.2.26
✓ google-genai              1.0-2.x
✓ langchain-core            0.3-0.4
✓ python-docx               1.1.2
✓ weasyprint                68.0+
✓ reportlab                 4.2.0
✓ pypdf                      4.0.0+
✓ pdf2image                 1.17.0
✓ Pillow                    10.4.0-11.x
✓ django-crispy-forms       2.0+
✓ crispy-bootstrap5         2.0+
✓ psycopg2-binary           2.9-3.x
✓ python-dotenv             1.0.1
```

### Development Only (15+ packages)
```
Testing:        pytest, pytest-django, pytest-cov, factory-boy, faker
Linting:        black, flake8, pylint, isort, bandit
Tools:          django-extensions, django-debug-toolbar, ipython
Type Checking:  django-stubs, mypy
```

### Production Only (10+ packages)
```
WSGI:           gunicorn, whitenoise
Caching:        redis, django-redis
Monitoring:     sentry-sdk, newrelic, datadog
```

---

## 📋 Requirements Files Summary

| File | Size | Purpose | Usage |
|------|------|---------|-------|
| **requirements.txt** | ~500KB | Base (11 deps) | All environments |
| **requirements-dev.txt** | ~3MB | Dev + Base (26 deps) | Local development |
| **requirements-prod.txt** | ~2MB | Production + Base (21 deps) | Production deployment |

**Total Footprint**: ~23 MB (without system dependencies)

---

## 🔄 Installation Workflow

```
1. Create Virtual Environment
   python -m venv .venv
   .\.venv\Scripts\activate

2. Choose Your Path:
   ├─ Development:      pip install -r requirements-dev.txt
   ├─ Production:       pip install -r requirements-prod.txt
   └─ Minimal/Core:     pip install -r requirements.txt

3. Configure Environment
   Create/Edit .env file with secrets

4. Setup Database
   python manage.py migrate

5. Create Admin User
   python manage.py createsuperuser

6. Start Server
   python manage.py runserver  # Development
   gunicorn ...                # Production
```

---

## 🌍 Document Types & Languages

| Type | English | Hindi | Format |
|------|---------|-------|--------|
| Office Order | ✓ | ✓ | .docx, .pdf |
| Circular | ✓ | ✓ | .docx, .pdf |
| Policy | ✓ | ✓ | .docx, .pdf |
| Advertisement | ✓ | ✓ | .docx, .pdf |

---

## 🔌 System Dependencies by OS

### Windows
```powershell
# Visual C++ Build Tools (required for weasyprint)
choco install visualstudio2019buildtools
```

### Ubuntu/Debian
```bash
sudo apt-get install -y \
  libpq-dev libcairo2-dev libpango-1.0-0 \
  libpango-cairo-1.0-0 libgdk-pixbuf2.0-0 \
  libffi-dev shared-mime-info python3-dev
```

### macOS
```bash
brew install libpq cairo pango gdk-pixbuf libffi
```

---

## 📊 Version Strategy

```
Exact Pinning:       python-dotenv==1.0.1
Range Pinning:       Django>=4.2.26,<4.3
Upper Bound:         Pillow>=10.4.0,<12
Major.Minor:         weasyprint>=68.0.0
```

---

## 🚀 Deployment Stack

```
Production Environment:
┌─ Client Browser (HTTPS)
├─ Nginx Reverse Proxy
├─ Gunicorn (4-8 workers)
├─ Django Application
├─ PostgreSQL (Neon)
├─ Redis Cache (optional)
└─ Monitoring (Sentry/NewRelic)
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Startup Time | 1-5 seconds |
| Document Generation | 5-30 seconds |
| PDF Export | 2-5 seconds |
| Memory per Worker | 150-250 MB |
| Typical Request Memory | 10-20 MB |

---

## ✅ Security Features

- ✓ Django CSRF Protection
- ✓ SQL Injection Prevention
- ✓ XSS Protection
- ✓ Secure Password Hashing
- ✓ HTTPS/SSL Support (Production)
- ✓ HSTS Headers
- ✓ Secure Cookies
- ✓ Environment Variable Secrets
- ✓ Database Connection Pooling

---

## 🎯 Quick Reference

### Start Development
```bash
pip install -r requirements-dev.txt
python manage.py runserver
# → http://localhost:8000
```

### Deploy to Production
```bash
pip install -r requirements-prod.txt
python manage.py collectstatic --noinput
gunicorn --workers 4 ai_formal_generator.wsgi:application
```

### Run Tests
```bash
pytest --cov=generator
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
pip-audit  # Check for vulnerabilities
```

---

## 🔗 Key Integration Points

### 1. Google Gemini API
- **Authentication**: GEMINI_API_KEY environment variable
- **Models**: gemini-2.5-flash-lite (primary)
- **Fallback**: 6-model degradation chain
- **Rate Limits**: Automatic handling

### 2. Database
- **Production**: PostgreSQL Neon (52.220.170.93:5432)
- **Development**: SQLite3 (local)
- **Connection Pooling**: Enabled in production

### 3. Static Files
- **Development**: Django development server
- **Production**: WhiteNoise or CDN

---

## 📋 Pre-Deployment Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] requirements-prod.txt installed
- [ ] .env configured with all secrets
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] SSL certificate configured
- [ ] Nginx/Apache configured
- [ ] Gunicorn configured (4+ workers)
- [ ] Redis configured (optional but recommended)
- [ ] Monitoring service configured (Sentry recommended)
- [ ] Backup strategy documented
- [ ] CI/CD pipeline setup
- [ ] Security audit completed

---

## 💾 Project Size Overview

| Component | Size |
|-----------|------|
| Python Packages | 23 MB |
| Application Code | ~2 MB |
| Database (Initial) | ~5 MB |
| Media/Uploads | Variable |
| Static Files | ~5 MB |
| **Total (minimal)** | **~40 MB** |

---

## 🎓 Recommended Learning Path

1. **Django Basics** - https://docs.djangoproject.com/
2. **PostgreSQL** - https://www.postgresql.org/docs/
3. **Google GenAI** - https://ai.google.dev/docs
4. **Document Processing** - Weasyprint, python-docx docs
5. **Deployment** - Gunicorn + Nginx setup

---

## 📞 Support Resources

### Documentation
- [Project Docs](./docs/)
- [Django Docs](https://docs.djangoproject.com/)
- [Google GenAI API](https://ai.google.dev/)

### Community
- Stack Overflow
- GitHub Discussions
- Django Forum

---

## 🔄 Version History

**Current Version**: 12.0
- ✅ Complete tech stack analysis
- ✅ Optimized requirements.txt
- ✅ Production-ready configuration
- ✅ Comprehensive documentation

**Previous**: Phase 1-11 (Architecture, SDK migration, hardening, production settings)

---

## 📝 Notes

1. All system dependencies must be installed before Python package installation
2. Keep .env file with secrets out of version control (add to .gitignore)
3. Use virtual environments for all projects
4. Regular security updates recommended for all packages
5. Monitor API quota for Google Gemini (especially in production)
6. Backup database regularly
7. Test all changes in development before production deployment

---
 
**Maintainer**: BISAG-N Development Team

For detailed information, refer to the comprehensive documentation files in the project root.
