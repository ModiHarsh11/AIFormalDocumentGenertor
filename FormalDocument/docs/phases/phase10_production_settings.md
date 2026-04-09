# 🏭 Phase 10 — Production-Grade Settings & Full Project Optimization

## What This Phase Covers

1. **Settings split** — monolith `settings.py` → `settings/` package (base / development / production)
2. **Runtime-breaking bugs fixed** — 4 view functions that crashed on every call
3. **Dead code removal** — 165 lines of unused inline prompts eliminated
4. **Security hardening** — secrets moved to environment variables
5. **Logging standardization** — `print()` → `logging.logger` throughout
6. **Import hygiene** — missing `Document` import, unused imports removed
7. **Data integrity** — stray tab in constants removed

---

## 1. Settings Split

### Before

```
ai_formal_generator/
    settings.py     ← 147 lines, everything in one file, DEBUG=True hardcoded
```

### After

```
ai_formal_generator/
    settings.py         ← deprecated breadcrumb (empty, safe to delete)
    settings/
        __init__.py     ← imports development.py by default
        base.py         ← shared settings (all environments)
        development.py  ← DEBUG=True, SQLite, relaxed security
        production.py   ← DEBUG=False, HTTPS, rotating file logs
```

### `base.py` — Shared Settings

Contains everything that does NOT vary between environments:
- `INSTALLED_APPS`, `MIDDLEWARE`, `TEMPLATES`
- `ROOT_URLCONF`, `WSGI_APPLICATION`
- `AUTH_PASSWORD_VALIDATORS`
- `STATIC_URL`, `MEDIA_URL`
- `GEMINI_API_KEY`, `LLM_MODEL` (from env vars)
- `LOGGING` (base structure — levels overridden per env)
- `TIME_ZONE = "Asia/Kolkata"` (corrected from `"UTC"` for BISAG-N in India)

### `development.py` — Local Development

```python
from .base import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-...")
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
DATABASES = {"default": {"ENGINE": "...sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
LOGGING["loggers"]["generator"]["level"] = "DEBUG"
```

### `production.py` — Deployed Environments

```python
from .base import *

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # MUST be set — crash on missing
DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# HTTPS enforcement
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000

# Database from env vars (supports PostgreSQL)
DATABASES = {"default": {
    "ENGINE": os.environ.get("DB_ENGINE", "...sqlite3"),
    "NAME": os.environ.get("DB_NAME", ...),
    ...
}}

# File-based rotating logs
LOGGING["handlers"]["file"] = {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": "logs/app.log",
    "maxBytes": 10 * 1024 * 1024,  # 10 MB
    "backupCount": 5,
}
```

### Switching Environments

```bash
# Development (default — no change needed)
python manage.py runserver

# Production
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.production gunicorn ai_formal_generator.wsgi
```

Or set in `.env`:
```
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.production
```

---

## 2. Runtime-Breaking Bugs Fixed

### The Problem

Four view functions in `views.py` called `gemini_model.generate_content()` — but `gemini_model` was **never defined or imported**. These functions crashed on every request:

| View Function | Line | Error |
|--------------|------|-------|
| `generate_circular_body` | 220 | `NameError: name 'gemini_model' is not defined` |
| `regenerate_circular_body` | 270 | Same |
| `generate_policy_body` | 623 | Same |
| `regenerate_policy_body` | 673 | Same |

These were **leftover monolith code** from before the service layer was introduced. The office order views had already been migrated, but circular and policy were not.

### The Fix

Each function now delegates to the service layer, following the exact pattern of the working office order views:

```python
# Before (crashed)
res = gemini_model.generate_content(system_prompt + "\n\nTopic:\n" + prompt)
return HttpResponse(res.text.strip())

# After (works)
from .services.ai_service import generate_circular_body as _gen_circular
body = _gen_circular(prompt, lang)
return HttpResponse(body)
```

All four views now go through:
1. **Service layer** — input validation, transport, sanitization
2. **Prompt layer** — versioned, hardened templates with delimiters
3. **Post-processing** — markdown stripping, leakage detection, structural checks

---

## 3. Dead Code Removed (165 lines)

| Location | What was removed | Lines saved |
|----------|-----------------|-------------|
| `generate_body` view | Entire inline `system_prompt` (EN + HI) + unused `full_prompt` variable | ~35 |
| `generate_circular_body` view | Entire inline prompt (EN + HI) | ~30 |
| `regenerate_circular_body` view | Inline prompt with f-string user input interpolation | ~40 |
| `generate_policy_body` view | Entire inline prompt (EN + HI) | ~30 |
| `regenerate_policy_body` view | Inline prompt with f-string user input interpolation | ~40 |
| Duplicate import | `from datetime import date` (already imported on line 9) | 2 |
| Unused imports | `from docx.oxml.ns import qn`, `from docx.oxml import OxmlElement` | 2 |

**`views.py` went from 1002 lines → 837 lines.**

---

## 4. Security Hardening

| Setting | Before | After |
|---------|--------|-------|
| `SECRET_KEY` | Hardcoded in source | `os.environ.get("DJANGO_SECRET_KEY", "<dev-fallback>")` |
| `GEMINI_API_KEY` | Hardcoded API key in plain text | `os.environ.get("GEMINI_API_KEY", "")` |
| `DEBUG` | Always `True` | `True` in dev, `False` in production |
| `ALLOWED_HOSTS` | Empty `[]` | `["localhost", ...]` in dev, from env in prod |
| HTTPS | Not configured | Full HSTS + secure cookies in production |

Created `.env.example` documenting all required variables.

---

## 5. Logging Standardization

### Before

```python
print(f"Error merging PDFs: {e}")
print(f"PDF conversion error: {conv_error}")
print(f"ImportError: {imp_err}")
```

7 `print()` calls scattered through policy PDF/DOCX generation.

### After

```python
logger = logging.getLogger(__name__)

logger.error("Error merging PDFs: %s", e)
logger.error("PDF conversion error: %s", conv_error)
logger.error("ImportError: %s", imp_err)
```

All errors now go through Django's logging system — visible in console during dev, written to rotating log files in production.

Also fixed: bare `except:` → `except OSError:` (was silently swallowing all exceptions).

---

## 6. Import Hygiene

| Fix | Detail |
|-----|--------|
| Added `from docx import Document` at module level | Was used at lines 369, 532, 831 but never imported — would fail on first DOCX generation |
| Added `import logging` + `logger` | Required for the `print()` → `logger` migration |
| Removed `from datetime import date` duplicate | Already imported via `from datetime import datetime, date` |
| Removed unused `qn`, `OxmlElement` imports | IDE flagged, confirmed unused |

---

## 7. Data Integrity

`constants.py` line 18 contained a tab character in the English value:

```python
# Before
"en": "\tDirector-Geo Spatial Applications",

# After
"en": "Director-Geo Spatial Applications",
```

This would have been visible in generated Office Order documents as a horizontal tab in the designation field.

---

## Final File Structure

```
ai_formal_generator/
    settings/
        __init__.py          ← imports development.py (default)
        base.py              ← shared settings (~150 lines)
        development.py       ← dev overrides (~35 lines)
        production.py        ← prod overrides (~65 lines)
    settings.py              ← deprecated breadcrumb
    .env.example             ← all required env vars documented
```

---

## Outcome

✅ Settings split into base / dev / prod — production-ready  
✅ 4 runtime-crashing views fixed — circular and policy AI generation now works  
✅ 165 lines of dead code removed — views.py is 16% smaller  
✅ Secrets read from environment — no hardcoded API keys  
✅ All logging goes through Django's logging framework  
✅ Structured production logging with rotating file handler  
✅ HTTPS enforcement + HSTS in production settings  
✅ `.env.example` documents all required environment variables  

