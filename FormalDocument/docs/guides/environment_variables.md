# 🔑 Environment Variables

All environment variables used by the project.

See also: `.env.example` in the project root for a ready-to-copy template.

---

## Required

### `GEMINI_API_KEY`

**Required.** Your Google Gemini API key.

```env
GEMINI_API_KEY=AIza...
```

Get a key from: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

**Where it's read:** `settings/base.py` → `os.environ.get("GEMINI_API_KEY", "")`  
Then consumed by `generator/services/ai_service.py` → `_get_client()`:

```python
api_key = getattr(settings, "GEMINI_API_KEY", None)
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured.")
```

### `DJANGO_SECRET_KEY`

**Required in production.** Django's secret key for cryptographic signing.

```env
DJANGO_SECRET_KEY=your-very-long-random-string
```

Generate one:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- **Development:** Falls back to a hardcoded insecure default (acceptable for local dev only).
- **Production:** `settings/production.py` does `os.environ["DJANGO_SECRET_KEY"]` — **will crash if missing**, by design.

---

## Optional

### `LLM_MODEL`

The Gemini model name to use. Defaults to `gemini-2.5-flash-lite` if not set.

```env
LLM_MODEL=gemini-2.5-flash-lite
```

| Model | Notes |
|---|---|
| `gemini-2.5-flash-lite` | Default. Fast, cost-efficient |
| `gemini-1.5-pro` | Higher capability, higher cost |
| `gemini-1.5-flash` | Balanced |

### `DJANGO_SETTINGS_MODULE`

Controls which settings file Django loads.

```env
# Development (default — no change needed)
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.development

# Production
DJANGO_SETTINGS_MODULE=ai_formal_generator.settings.production
```

### `ALLOWED_HOSTS` (production only)

Comma-separated list of allowed hostnames.

```env
ALLOWED_HOSTS=example.com,www.example.com
```

### Database Variables (production only)

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=bisag_formal
DB_USER=bisag
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
```

If not set, production falls back to SQLite.

---

## `.env` File Setup

Create `ai_formal_generator/.env` (alongside `manage.py`):

```env
GEMINI_API_KEY=your-key-here
LLM_MODEL=gemini-2.5-flash-lite
DJANGO_SECRET_KEY=your-secret-key
```

`settings/base.py` loads it automatically:
```python
from dotenv import load_dotenv
load_dotenv()
```

A template is provided at `.env.example` — copy and fill in values.

---

## Settings Files Reference

| Variable | File | Dev Default | Production |
|----------|------|-------------|------------|
| `DJANGO_SECRET_KEY` | `development.py` / `production.py` | Hardcoded insecure fallback | **Required** — crash on missing |
| `GEMINI_API_KEY` | `base.py` | `""` | Must be set |
| `LLM_MODEL` | `base.py` | `gemini-2.5-flash-lite` | Same |
| `DEBUG` | `development.py` / `production.py` | `True` | `False` |
| `ALLOWED_HOSTS` | `development.py` / `production.py` | `localhost`, `127.0.0.1` | From env var |
| `DB_*` | `production.py` | N/A (SQLite) | From env vars |

---

## Production Notes

For production, set these as system environment variables or use a secrets manager.  
Do **not** commit `.env` files or API keys to version control.

Add to `.gitignore`:
```
.env
*.env
```
