# 📂 Codebase Folder Structure

```
ai_formal_generator/                  ← Django project root
│
├── manage.py
├── db.sqlite3
├── requirements.txt
├── .env                              ← Environment variables (not in git)
├── .env.example                      ← Template for .env
│
├── ai_formal_generator/              ← Django project settings package
│   ├── settings/                     ← Split settings (production-grade)
│   │   ├── __init__.py               ← imports development.py by default
│   │   ├── base.py                   ← shared settings (all environments)
│   │   ├── development.py            ← DEBUG=True, SQLite, relaxed security
│   │   └── production.py             ← DEBUG=False, HTTPS, rotating file logs
│   ├── urls.py                       ← Root URL dispatcher
│   ├── wsgi.py
│   └── asgi.py
│
├── generator/                        ← Main Django app
│   │
│   ├── data/                         ← JSON configuration files
│   │   ├── office_order.json         ← Header strings & config for Office Order
│   │   ├── circular.json             ← Header strings, people list for Circular
│   │   └── policy.json               ← Header strings for Policy
│   │
│   ├── views/                        ← HTTP layer (split by document type)
│   │   ├── __init__.py               ← re-exports all views for urls.py
│   │   ├── common.py                 ← home(), JSON loading, date helpers
│   │   ├── office_order.py           ← Office Order views
│   │   ├── circular.py               ← Circular views
│   │   └── policy.py                 ← Policy views
│   │
│   ├── urls.py                       ← URL patterns for generator app
│   ├── models.py                     ← Django ORM models
│   ├── admin.py                      ← Django admin registration
│   ├── apps.py                       ← App config
│   ├── constants.py                  ← DESIGNATION_MAP (EN + HI designations)
│   │
│   ├── services/                     ← AI service layer (modular)
│   │   ├── __init__.py               ← public API: generate_body, regenerate_body
│   │   ├── client.py                 ← Gemini client init, config, reset
│   │   ├── validation.py             ← Language, DocumentType, input validators
│   │   ├── sanitization.py           ← markdown stripping, leakage removal, checks
│   │   ├── registry.py               ← DOCUMENT_PROMPT_REGISTRY, version registry
│   │   ├── service.py                ← generate_body(), regenerate_body()
│   │   └── ai_service.py             ← DEPRECATED re-export (safe to delete)
│   │
│   ├── prompts/                      ← LangChain prompt template layer
│   │   ├── __init__.py
│   │   ├── _shared.py                ← Language, validate_language, select_template
│   │   ├── office_order.py           ← Office Order prompts
│   │   ├── circular.py               ← Circular prompts
│   │   └── policy.py                 ← Policy prompts
│   │
│   ├── utils/                        ← Utility helpers (reserved for future use)
│   │   └── __init__.py
│   │
│   ├── templates/
│   │   └── generator/                ← Django HTML templates
│   │       ├── home.html
│   │       ├── circular_form.html
│   │       ├── result_office_order.html
│   │       ├── pdf_office_order.html
│   │       ├── result_circular.html
│   │       ├── pdf_circular.html
│   │       ├── result_policy.html
│   │       └── pdf_policy.html
│   │
│   └── migrations/                   ← Django DB migrations
│
└── static/
    └── generator/
        ├── bisag_logo.png
        ├── bisag_img1.jpg
        ├── style.css
        └── fonts/                    ← Devanagari fonts for WeasyPrint PDF
            ├── NotoSansDevanagari-Regular.ttf
            ├── NotoSansDevanagari-Bold.ttf
            ├── NotoSerifDevanagari-Regular.ttf
            └── NotoSerifDevanagari-Bold.ttf
```

---

## File Ownership by Layer

| Layer | Files |
|---|---|
| HTTP Layer | `generator/views/` package, `generator/urls.py` |
| Service Layer | `generator/services/` package (`service.py`, `client.py`, `validation.py`, `sanitization.py`, `registry.py`) |
| Prompt Layer | `generator/prompts/_shared.py`, `office_order.py`, `circular.py`, `policy.py` |
| Output/Render Layer | `generator/templates/` |
| Configuration | `ai_formal_generator/settings/`, `.env`, `generator/data/*.json` |
| Data/Constants | `generator/constants.py`, `generator/models.py` |

---

## Key Files — Quick Reference

### `services/service.py`
Public API entry point:
- `generate_body(document_type, topic, language)` — unified generation
- `regenerate_body(document_type, topic, previous_body, refinement_prompt, language)` — unified regeneration

### `services/client.py`
- `get_client()` — lazy Gemini singleton
- `reset_client()` — for testing or API key rotation
- `MODEL_NAME`, `GENERATION_CONFIG`

### `services/registry.py`
- `DOCUMENT_PROMPT_REGISTRY` — maps `DocumentType` → prompt builders
- `PROMPT_VERSION_REGISTRY` — maps `DocumentType` → version strings for tracing

### `services/validation.py`
- `DocumentType = Literal["office", "circular", "policy"]`
- `Language = Literal["en", "hi"]`
- `validate_document_type()`, `validate_inputs()`

### `services/sanitization.py`
- `strip_markdown()` — removes code blocks, asterisks, bullets, headings
- `validate_body()` — strips leaked EN + HI headers
- `_check_structure()` — soft validation (paragraph count, bullets, length)

### `prompts/_shared.py`
Single source of truth for language support:
- `Language = Literal["en", "hi"]`
- `validate_language()`, `select_template()`

### `generator/data/*.json`
Document-specific header strings and people lists.
Loaded once at module import in `views/common.py`.

### `constants.py`
Maps English designation keys → bilingual `{en: ..., hi: ...}` dicts.
