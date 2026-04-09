# Dependency Analysis & Management

## Overview
This document provides detailed information about each dependency in the BISAG-N DocumentGenerator project, including their purpose, version constraints, and security considerations.

---

## Core Dependencies

### 1. Django (4.2.26 - 4.2.x)
**Purpose**: Web framework, ORM, admin panel, authentication
**Why Used**: 
- Industry-standard Python web framework
- Built-in security features (CSRF, SQL injection protection)
- Excellent documentation and community support
- Admin interface with minimal setup

**Security Notes**:
- ✅ LTS (Long Term Support) version
- Always install updates via: `pip install --upgrade "Django>=4.2.26,<4.3"`
- Check for patches: https://www.djangoproject.com/weblog/

**Compatibility**:
- Python 3.9+
- PostgreSQL 12+
- All Django contrib packages

---

### 2. google-genai (1.0 - 2.x)
**Purpose**: Google Generative AI (Gemini) API client
**Why Used**:
- Official Google SDK for Gemini models
- Simple, intuitive API
- Automatic error handling
- Streaming support for long responses

**Key Features**:
- Multiple Gemini models (2.5, 2.0, Gemma)
- Automatic fallback chain on quota/errors
- Safety filter integration
- Rate limiting handling

**API Keys**:
- Required in `.env` as `GEMINI_API_KEY`
- Get from: https://ai.google.dev/
- Free tier available for development

---

### 3. psycopg2-binary (2.9.0 - 3.x)
**Purpose**: PostgreSQL database adapter
**Why Used**:
- Official Python PostgreSQL driver
- High performance
- Full PostgreSQL feature support
- Connection pooling capabilities

**Note**: 
- Using `psycopg2-binary` (precompiled) for easier installation
- For production, consider `psycopg2` with system libs for better security

---

### 4. python-dotenv (1.0.1)
**Purpose**: Load environment variables from `.env` file
**Why Used**:
- Keeps secrets out of source code
- Easy local development setup
- Environment-specific configurations
- Required for Django settings

**Security**:
- Never commit `.env` file to git
- Add `.env` to `.gitignore`
- Use strong random secrets

---

### 5. langchain-core (0.3.x - 0.4.x)
**Purpose**: Prompt templates and chain management
**Why Used**:
- Structured prompt engineering
- Template variables support
- Easy prompt versioning
- LLM abstraction layer

**Models**:
- Office Order, Circular, Policy prompts
- Shared templates in `_shared.py`
- Language-specific templates (English/Hindi)

---

## Document Generation Stack

### 6. reportlab (4.2.0)
**Purpose**: Advanced PDF generation (tables, charts, graphics)
**Why Used**:
- Low-level PDF control
- Complex layouts possible
- Lightweight dependency
- Widely used in production

**Use Cases**:
- Dynamic tables in documents
- Formatting complex layouts
- Custom headers/footers

---

### 7. python-docx (1.1.2)
**Purpose**: Create and modify Microsoft Word documents
**Why Used**:
- Native .docx file creation
- Comprehensive formatting support
- Industry standard format
- Easy table and list creation

**Document Generation Uses**:
- Office Orders
- Circulars
- Policy documents
- Export templates

---

### 8. weasyprint (68.0.0+)
**Purpose**: HTML/CSS to PDF conversion
**Why Used**:
- Precise CSS rendering to PDF
- Better quality than other tools
- Supports HTML5 and CSS3
- Server-side rendering

**System Dependencies**:
- Cairo, Pango, GDK-Pixbuf (required)
- Platform-specific installation needed

**Performance**:
- Process-intensive (use caching)
- Consider async processing for high volume

---

### 9. pypdf (4.0.0+)
**Purpose**: PDF file manipulation (merge, split, encrypt)
**Why Used**:
- Pure Python (no system dependencies)
- PDF manipulation operations
- Watermarking support
- Encryption capabilities

**Use Cases**:
- Merge multiple PDFs
- Add digital signatures
- Compress PDFs
- Extract metadata

---

### 10. pdf2image (1.17.0)
**Purpose**: Convert PDF pages to images
**Why Used**:
- Preview generation
- Thumbnail creation
- PDF validation
- Image export

**Dependencies**:
- Requires: poppler-utils (external)
- Lightweight for light use

---

### 11. Pillow (10.4.0 - 11.x)
**Purpose**: Image processing library
**Why Used**:
- Standard Python imaging library
- Support for many formats
- Image manipulation (resize, filter)
- OCR compatibility

**Common Operations**:
- Watermark addition
- Image resizing
- Format conversion
- Quality optimization

---

## Frontend Dependencies

### 12. django-crispy-forms (2.0+)
**Purpose**: Django form rendering with template packs
**Why Used**:
- DRY form rendering
- Bootstrap integration
- Customizable templates
- Reduces template duplication

**Template Pack**: bootstrap5

---

### 13. crispy-bootstrap5 (2.0+)
**Purpose**: Bootstrap 5 template pack for Crispy Forms
**Why Used**:
- Modern Bootstrap 5 styling
- Responsive design
- Consistent look and feel
- Active community support

---

## Development Dependencies Analysis

### Testing
| Package | Version | Purpose |
|---------|---------|---------|
| pytest | 7.4.0+ | Test framework (preferred over Django's default) |
| pytest-django | 4.5.0+ | Django integration for pytest |
| pytest-cov | 4.1.0+ | Code coverage measurement |
| factory-boy | 3.3.0+ | Test fixture factories |
| faker | 19.0.0+ | Fake data generation |

### Code Quality
| Package | Version | Purpose |
|---------|---------|---------|
| black | 23.0.0+ | Code formatter (opinionated) |
| flake8 | 6.0.0+ | Code linter |
| pylint | 2.17.0+ | Advanced analysis |
| isort | 5.12.0+ | Import sorting |
| bandit | 1.7.5+ | Security vulnerabilities scanner |

### Development Tools
| Package | Version | Purpose |
|---------|---------|---------|
| django-extensions | 3.2.0+ | `shell_plus`, `print_settings`, etc. |
| django-debug-toolbar | 4.0.0+ | SQL query inspection |
| ipython | 8.0.0+ | Enhanced shell |
| django-stubs | 4.2.0+ | Type hints for Django |
| mypy | 1.5.0+ | Static type checking |

---

## Production Dependencies Analysis

### WSGI & Web Servers
| Package | Version | Purpose |
|---------|---------|---------|
| gunicorn | 21.0.0+ | WSGI HTTP Server (production) |
| whitenoise | 6.5.0+ | Static file serving in production |

**Configuration**:
```bash
gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  ai_formal_generator.wsgi:application
```

### Caching
| Package | Version | Purpose |
|---------|---------|---------|
| redis | 5.0.0+ | In-memory data store |
| django-redis | 5.3.0+ | Django Redis backend |

**Use Cases**:
- Session storage
- Query result caching
- Rate limiting
- Task queuing

### Monitoring & Error Tracking
| Package | Version | Purpose |
|---------|---------|---------|
| sentry-sdk | 1.30.0+ | Error tracking & performance monitoring |
| newrelic | 8.0.0+ | Application performance monitoring |
| datadog | 0.45.0+ | Infrastructure monitoring |

**Recommendation**: 
- Start with Sentry for error tracking
- Add NewRelic for detailed APM
- Use Datadog if already in infrastructure

---

## Version Pinning Strategy

### Current Strategy (Recommended)
```
Exact pinning:     python-dotenv==1.0.1
Range pinning:     Django>=4.2.26,<4.3
Upper bound:       Pillow>=10.4.0,<12
Major.minor:       weasyprint>=68.0.0
```

### Reasons for Each Strategy
1. **Exact Pinning** (python-dotenv)
   - Package is stable
   - No breaking changes expected
   - Perfect for critical dependencies

2. **Range Pinning** (Django)
   - LTS release line
   - Bug fixes and security patches
   - Prevents major version jumps

3. **Upper Bound** (Pillow)
   - Development active
   - Keep below next major version
   - Avoid breaking changes

4. **Major.Minor** (weasyprint)
   - Stable API
   - Allow all patch versions
   - Latest features and fixes

---

## Security Considerations

### Regular Audits
```bash
# Check for known vulnerabilities
pip install safety
safety check

# Or use pip-audit (built into recent pip)
pip-audit
```

### Updating Dependencies
```bash
# Check what can be updated
pip list --outdated

# Update specific package
pip install --upgrade Django

# Update all (use with caution!)
pip install --upgrade -r requirements.txt
```

### Security Patches Priority
1. **Critical**: Django, google-genai, psycopg2
2. **High**: python-docx, weasyprint, Pillow, reportlab
3. **Medium**: Other packages

---

## Dependency Conflicts & Resolutions

### Known Issues
#### Issue 1: WeasyPrint System Dependencies
**Problem**: WeasyPrint requires Cairo, Pango (platform-specific)
**Solution**: Follow OS-specific installation in INSTALLATION_GUIDE.md

#### Issue 2: Pillow & Compressed Library Support
**Problem**: Need libjpeg, libpng for image processing
**Solution**: Install via system package manager before pip

#### Issue 3: PostgreSQL Binary Compatibility
**Problem**: psycopg2-binary may fail on ARM/custom systems
**Solution**: Use `psycopg2` with system libs instead

---

## Requirements File Maintenance

### When to Update
- Security patches: Immediately
- Bug fixes: Monthly
- Feature updates: Quarterly
- Major versions: Planned upgrade cycles

### Approval Process
1. Test locally with new versions
2. Run full test suite (`pytest`)
3. Check for deprecation warnings
4. Update requirements file
5. Commit to git with changelog

### Changelog Format
```markdown
## [YYYY-MM-DD] Dependencies Update

### Core
- Django upgraded from 4.2.25 → 4.2.26 (security patch)

### Features
- google-genai upgraded for new Gemini model support

### Development
- Black upgraded for better formatting

### Security
- psycopg2 security patch applied
```

---

## Dependency Monitoring

### Tools for Monitoring
1. **GitHub Dependabot**: Automated PR updates
2. **Renovate**: More flexible automated updates
3. **Safety**: Vulnerability scanning
4. **pip-audit**: Built-in auditing

### Setting Up Dependabot
1. Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/FormalDocument/ai_formal_generator"
    schedule:
      interval: "weekly"
      day: "monday"
```

---

## Performance Impact

### Package Size Analysis
```
Django:           ~10 MB
google-genai:     ~3 MB
weasyprint:       ~2 MB
python-docx:      ~2 MB
reportlab:        ~1 MB
All others:       ~5 MB
────────────────
Total:            ~23 MB (without system deps)
```

### Startup Time Impact (Approximate)
- Django import: 200-300ms
- Google GenAI import: 50-100ms
- Document processing: 100-200ms
- **Total**: 350-600ms average

### Runtime Memory Usage
- Django app: 100-150 MB
- Per request: 10-20 MB
- Per worker (Gunicorn): 150-250 MB

---

## Dependency Tree

```
DocumentGenerator
├── Django (web framework)
│   ├── psycopg2-binary (PostgreSQL)
│   └── django-crispy-forms
│       └── crispy-bootstrap5
│
├── google-genai (LLM API)
│   └── (internal dependencies)
│
├── langchain-core (prompt management)
│   └── (internal dependencies)
│
├── Document Processing
│   ├── python-docx (Word docs)
│   ├── weasyprint (HTML→PDF)
│   ├── reportlab (advanced PDF)
│   ├── pypdf (PDF manipulation)
│   ├── pdf2image (PDF→Image)
│   └── Pillow (image processing)
│
└── Configuration
    └── python-dotenv (env vars)
```

---

## Migration Guide (if upgrading)

### From Django 4.1 → 4.2
- ✅ Mostly compatible
- Update: `pip install "Django>=4.2.26,<4.3"`
- Run: `python manage.py makemigrations`
- Run: `python manage.py migrate`

### From google-genai 0.x → 1.x
- Breaking changes to API
- Update import paths if custom code
- Models naming may change
- Required update for new Gemini models

---

## Support & Resources

### Documentation Links
- [Django Docs](https://docs.djangoproject.com/)
- [Google GenAI SDK](https://ai.google.dev/docs)
- [LangChain Docs](https://python.langchain.com/)
- [WeasyPrint Docs](https://doc.courtbouillon.org/weasyprint/stable/)

### Community Support
- Stack Overflow
- GitHub Discussions
- Discord Communities
- Official Project Issues

---

**Last Updated**: April 6, 2026
**Maintainer**: BISAG-N Development Team
