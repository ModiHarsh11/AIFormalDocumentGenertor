# 🛠️ Local Development Setup

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9+ (Recommended: 3.11+) |
| pip | Latest |
| Git | Any |
| Gemini API Key | Required — get from [Google AI Console](https://console.cloud.google.com) |

### System Dependencies by OS

**Windows:**
- Visual C++ Build Tools (for weasyprint)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y \
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

**macOS:**
```bash
brew install libpq cairo pango gdk-pixbuf libffi
```

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/ModiHarsh11/AIFormalDocumentGenertor.git
cd DocumentGenerator-main/FormalDocument/ai_formal_generator
```

---

## Step 2 — Create and Activate Virtual Environment

```bash
# Navigate to project root
cd D:\BISAG\DocumentGenerator-main\DocumentGenerator-main

# Create virtual environment
python -m venv .venv

# Activate — Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Activate — Windows CMD
.venv\Scripts\activate.bat

# Activate — Linux/macOS
source .venv/bin/activate
```

---

## Step 3 — Install Dependencies

### For Development:
```bash
pip install -r FormalDocument/ai_formal_generator/requirements-dev.txt
```

### For Production:
```bash
pip install -r FormalDocument/ai_formal_generator/requirements-prod.txt
```

### For Core Only:
```bash
pip install -r FormalDocument/ai_formal_generator/requirements.txt
```

### All Core Packages Installed:

| Package | Version | Purpose |
|---|---|---|
| `Django` | 4.2.26-4.2.x | Web framework |
| `google-genai` | 1.0-2.x | Gemini AI SDK |
| `langchain-core` | 0.3-0.4 | Prompt templates |
| `python-docx` | 1.1.2 | Word document generation |
| `weasyprint` | 68.0+ | HTML to PDF conversion |
| `reportlab` | 4.2.0 | Advanced PDF creation |
| `pypdf` | 4.0.0+ | PDF manipulation |
| `pdf2image` | 1.17.0 | PDF to image conversion |
| `Pillow` | 10.4.0-11.x | Image processing |
| `django-crispy-forms` | 2.0+ | Form rendering |
| `crispy-bootstrap5` | 2.0+ | Bootstrap 5 styling |
| `psycopg2-binary` | 2.9.0+ | PostgreSQL driver |
| `python-dotenv` | 1.0.1 | Environment configuration |

---

## Step 4 — Configure Environment Variables

Create `.env` file from template:

```bash
# Windows
cp FormalDocument\ai_formal_generator\.env.example FormalDocument\ai_formal_generator\.env

# Linux/macOS
cp FormalDocument/ai_formal_generator/.env.example FormalDocument/ai_formal_generator/.env
```

Edit `.env` and configure the following:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.development
DEBUG=True

# AI/LLM Configuration
GEMINI_API_KEY=your-gemini-api-key-here
LLM_MODEL=gemini-2.5-flash-lite

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://neondb_owner:password@ep-winter-hall-a1y923vf-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

# Server Configuration
ALLOWED_HOSTS=localhost,127.0.0.1
```

For complete list of variables, see [`environment_variables.md`](environment_variables.md).

---

## Step 5 — Run Database Migrations

```bash
cd FormalDocument/ai_formal_generator

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

---

## Step 6 — Collect Static Files (Development)

```bash
python manage.py collectstatic --noinput
```

---

## Step 7 — Start the Development Server

```bash
python manage.py runserver
```

Access the application:
- Main URL: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Admin Panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Login: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)

---

## Project Structure After Setup

```
FormalDocument/
├── requirements.txt
├── requirements-dev.txt
├── INSTALLATION_GUIDE.md
├── DEPENDENCY_ANALYSIS.md
│
└── ai_formal_generator/
    ├── manage.py
    ├── db.sqlite3                    [Local database - development]
    ├── .env                          [Environment config - DO NOT COMMIT]
    ├── .env.example                  [Template for .env]
    │
    ├── ai_formal_generator/          [Django Configuration]
    │   ├── asgi.py                   [ASGI - production]
    │   ├── wsgi.py                   [WSGI - production]
    │   ├── urls.py                   [URL routing]
    │   └── settings/
    │       ├── base.py               [Shared settings]
    │       ├── development.py        [Dev settings]
    │       └── production.py         [Prod settings]
    │
    ├── generator/                    [Main Application]
    │   ├── admin.py
    │   ├── models.py                 [Database models]
    │   ├── urls.py
    │   ├── services/                 [Business Logic]
    │   │   ├── client.py             [Gemini API client]
    │   │   ├── service.py            [Generation services]
    │   │   ├── validation.py
    │   │   └── sanitization.py
    │   ├── prompts/                  [AI Prompts (EN/HI)]
    │   │   ├── office_order.py
    │   │   ├── circular.py
    │   │   ├── policy.py
    │   │   └── _shared.py
    │   ├── views/                    [HTTP Handlers]
    │   │   ├── auth_views.py
    │   │   ├── dashboard.py
    │   │   ├── office_order.py
    │   │   ├── circular.py
    │   │   ├── policy.py
    │   │   ├── advertisement.py
    │   │   └── common.py
    │   ├── migrations/               [Database migrations]
    │   ├── templates/                [HTML templates]
    │   └── data/
    │       ├── office_order.json
    │       ├── circular.json
    │       └── policy.json
    │
    ├── static/                       [CSS, JS, Images]
    │   └── generator/
    │
    ├── media/                        [User uploads]
    │   └── policy_uploads/
    │
    └── templates/                    [Django templates]
```

---

## Verifying the Setup

1. Navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
2. You should be redirected to the **Sign In** page
3. Use **Forgot password?** on the sign-in page to test reset flow (email prints in terminal in development)
4. Create an account or login
5. Go to Dashboard
6. Try generating a document:
   - Select **Office Order / Circular / Policy / Advertisement**
   - Enter a topic
   - Select language (English or Hindi)
   - Click **Generate Body**

If you see generated text appear, the AI layer is working correctly.

---

## Common Issues & Solutions

### ❌ `GEMINI_API_KEY not found`
**Solution:**
1. Check `.env` file has `GEMINI_API_KEY = xxx`
2. Ensure `.env` is in the correct directory: `ai_formal_generator/`
3. Restart Django server after adding the key
4. Verify key is valid in Google Cloud Console

### ❌ `ModuleNotFoundError: No module named 'weasyprint'`
**Solution:**
- Windows: Install Visual C++ Build Tools
- Linux: `sudo apt-get install libcairo2-dev libpango-1.0-0 libpango-cairo-1.0-0`
- macOS: `brew install cairo pango`
- Then: `pip install weasyprint`

### ❌ PDF generation errors on Windows
**Solution:**
- Install GTK for Windows: [GTK Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)
- Or use WSL (Windows Subsystem for Linux)
- Or run production server on Linux

### ❌ `no such table: auth_user`
**Solution:**
```bash
cd ai_formal_generator
python manage.py migrate
```

### ❌ Database connection refused
**Solution:**
1. Check `.env` DATABASE_URL is correct
2. Verify internet connection (cloud PostgreSQL)
3. Check firewall/proxy settings
4. Test connection: `psql -U neondb_owner -h ep-winter-hall-a1y923vf-pooler.ap-southeast-1.aws.neon.tech`

### ❌ Static files not found in development
**Solution:**
```bash
python manage.py collectstatic --clear --noinput
```

### ❌ Hindi text rendering issues in PDF
**Solution:**
- Ensure Devanagari fonts are installed
- Check `static/generator/fonts/` has proper fonts
- WeasyPrint may need system font configuration

### ❌ Port 8000 already in use
**Solution:**
```bash
# Use different port
python manage.py runserver 8001

# Or find and kill process using port 8000
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000 | kill -9 <PID>
```

---

## Development Tools

### Run Tests
```bash
pytest
pytest --cov=generator
```

### Format Code
```bash
black .
isort .
```

### Lint Code
```bash
flake8 .
pylint generator/
```

### Database Shell
```bash
python manage.py dbshell
```

### Django Shell
```bash
python manage.py shell_plus  # With django-extensions
```

### Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Production Deployment

### Using Gunicorn & Nginx

1. **Install production dependencies:**
```bash
pip install -r requirements-prod.txt
```

2. **Collect static files:**
```bash
python manage.py collectstatic --noinput
```

3. **Run Gunicorn:**
```bash
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  ai_formal_generator.wsgi:application
```

4. **Configure Nginx** (reverse proxy in front of Gunicorn)

See [`INSTALLATION_GUIDE.md`](../../INSTALLATION_GUIDE.md) for detailed deployment steps.

---

## Next Steps

1. Read [`PROJECT_DETAILS.txt`](../../PROJECT_DETAILS.txt) for complete project overview
2. Check [`environment_variables.md`](environment_variables.md) for all configuration options
3. Review [`adding_document_type.md`](adding_document_type.md) to extend with new document types
4. See [`DEPENDENCY_ANALYSIS.md`](../../DEPENDENCY_ANALYSIS.md) for package information
5. Explore `/docs` for complete documentation

