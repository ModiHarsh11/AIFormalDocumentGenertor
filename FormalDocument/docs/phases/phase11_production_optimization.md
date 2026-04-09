# 🏗 Phase 11 — Production-Grade Optimization & Modular Refactor

## What This Phase Covers

1. **Prompt-layer bug fixes** — two runtime bugs in `circular.py` and `policy.py`
2. **Service layer split** — monolithic `ai_service.py` (400 lines) → 5 focused modules
3. **View layer split** — monolithic `views.py` (837 lines) → per-document-type view modules
4. **Caller migration** — views now use unified `generate_body()` / `regenerate_body()` directly
5. **Dead code removal** — unused `docx_generator.py`, backward-compat wrappers
6. **Model update** — `Policy` added to `DOCUMENT_TYPES` choices
7. **Project hygiene** — corrupted `requirements.txt` fixed, `.gitignore` extended

---

## 1. Prompt-Layer Bug Fixes

### Bug 1: `circular.py` — Undefined `_select_template`

**Before:**
```python
# circular.py — build_regeneration_prompt()
template = _select_template(REGENERATION_TEMPLATE_EN, REGENERATION_TEMPLATE_HI, language)
```

`_select_template` was never defined in `circular.py` — it was imported as `select_template` from `_shared.py` but the regeneration function called the wrong name.

**After:**
```python
template = select_template(REGENERATION_TEMPLATE_EN, REGENERATION_TEMPLATE_HI, language)
```

**Impact:** Circular regeneration would have raised `NameError` at runtime.

### Bug 2: `policy.py` — Local Duplicates of Shared Utilities

**Before:**
```python
# policy.py — had its own copies
SUPPORTED_LANGUAGES = ("en", "hi")
Language = Literal["en", "hi"]

def _validate_language(language: str) -> None: ...
def _select_template(...): ...
```

**After:**
```python
from ._shared import Language, validate_language, select_template
```

All three prompt files (`office_order.py`, `circular.py`, `policy.py`) now use the same shared utilities from `_shared.py`. Adding a new language requires changing only `_shared.py`.

---

## 2. Service Layer Split

### Before

```
services/
    __init__.py          ← empty
    ai_service.py        ← 400 lines, everything in one file
```

### After

```
services/
    __init__.py          ← public API re-exports
    ai_service.py        ← DEPRECATED thin re-export (backward compat)
    client.py            ← Gemini client, lazy init, reset, config
    validation.py        ← Language, DocumentType, input validators
    sanitization.py      ← markdown stripping, leakage detection, structural checks
    registry.py          ← DOCUMENT_PROMPT_REGISTRY, PROMPT_VERSION_REGISTRY
    service.py           ← generate_body(), regenerate_body() — the real API
```

### Module Responsibilities

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `client.py` | ~42 | `get_client()`, `reset_client()`, `MODEL_NAME`, `GENERATION_CONFIG` |
| `validation.py` | ~48 | `Language`, `DocumentType`, `validate_document_type()`, `validate_inputs()` |
| `sanitization.py` | ~100 | `strip_markdown()`, `validate_body()`, `_check_structure()`, leakage patterns |
| `registry.py` | ~52 | Prompt import routing — one entry per document type |
| `service.py` | ~130 | `_generate()`, `generate_body()`, `regenerate_body()` |

### Import Surface

```python
# Recommended usage — clean, explicit
from generator.services import generate_body, regenerate_body

# Also available for testing / advanced use
from generator.services import reset_client, DocumentType, Language
```

### Adding a New Document Type

With this structure, adding a new document type requires:

1. New prompt file in `generator/prompts/` (e.g., `notice.py`)
2. Two entries in `registry.py` (`DOCUMENT_PROMPT_REGISTRY` + `PROMPT_VERSION_REGISTRY`)
3. Add the literal value to `DocumentType` in `validation.py`
4. **Zero** new service functions

---

## 3. View Layer Split

### Before

```
generator/
    views.py             ← 837 lines, all 3 document types + all exports
```

### After

```
generator/
    views/
        __init__.py      ← re-exports all view functions (urls.py unchanged)
        common.py        ← home(), JSON loading, format_date_ddmmyyyy()
        office_order.py  ← Office Order: generate, regenerate, preview, PDF, DOCX
        circular.py      ← Circular: generate, regenerate, preview, PDF, DOCX
        policy.py        ← Policy: generate, regenerate, preview, PDF, DOCX
```

### Key Design Decision: Re-export via `__init__.py`

```python
# views/__init__.py
from .office_order import generate_body, regenerate_office_body, ...
from .circular import generate_circular_body, regenerate_circular_body, ...
from .policy import generate_policy_body, regenerate_policy_body, ...
```

This means `urls.py` requires **zero changes** — it still does:
```python
from . import views
path("generate-body/", views.generate_body, ...)
```

---

## 4. Caller Migration — Unified API

### Before (views used compat wrappers)

```python
# Old pattern in views
from .services.ai_service import generate_office_body
body = generate_office_body(prompt, lang)
```

### After (views use unified API)

```python
# New pattern in views
from generator.services import generate_body
body = generate_body("office", prompt, lang)
```

All views now call `generate_body(document_type, ...)` and `regenerate_body(document_type, ...)` directly. The old 6 wrapper functions (`generate_office_body`, `regenerate_office_body`, etc.) are no longer needed.

---

## 5. Dead Code Removal

| Item | Location | Reason |
|------|----------|--------|
| `docx_generator.py` | `generator/utils/` | Never imported — dead since the beginning |
| Compat wrappers | `ai_service.py` | Replaced by `generate_body()` / `regenerate_body()` |
| Local `_validate_language` | `policy.py` | Replaced by shared `validate_language()` |
| Local `_select_template` | `policy.py` | Replaced by shared `select_template()` |

---

## 6. Model Update

Added `("Policy", "Policy")` to `DocumentLog.DOCUMENT_TYPES`:

```python
DOCUMENT_TYPES = [
    ("Office Order", "Office Order"),
    ("Circular", "Circular"),
    ("Policy", "Policy"),          # ← NEW
    ("Notice", "Notice"),
    ("Other", "Other"),
]
```

Migration: `0002_add_policy_document_type.py` — data-safe (choices-only change).

---

## 7. Project Hygiene

| Item | Fix |
|------|-----|
| Root `requirements.txt` | Rewritten in UTF-8 (was corrupted with encoding artifacts) |
| `.gitignore` | Added coverage/testing entries (`htmlcov/`, `.coverage`, `.pytest_cache/`) |
| `.env.example` | Added `DEBUG` and `MEDIA_ROOT` hints for production |

---

## File Change Summary

| Action | Files |
|--------|-------|
| **Created** | `services/client.py`, `services/validation.py`, `services/sanitization.py`, `services/registry.py`, `services/service.py` |
| **Created** | `views/__init__.py`, `views/common.py`, `views/office_order.py`, `views/circular.py`, `views/policy.py` |
| **Modified** | `prompts/circular.py`, `prompts/policy.py`, `prompts/office_order.py` |
| **Modified** | `services/__init__.py`, `services/ai_service.py` (→ thin re-export) |
| **Modified** | `models.py`, `.gitignore`, `.env.example`, `requirements.txt` |
| **Deleted** | `views.py` (monolithic), `utils/docx_generator.py` (dead code) |
| **Generated** | `migrations/0002_add_policy_document_type.py` |

---

## Architecture After Phase 11

```
generator/
    models.py
    constants.py
    admin.py
    apps.py
    urls.py                      ← unchanged
    prompts/
        _shared.py               ← Language, validate_language, select_template
        office_order.py          ← uses _shared
        circular.py              ← uses _shared (bug fixed)
        policy.py                ← uses _shared (migrated from local)
    services/
        __init__.py              ← public API surface
        client.py                ← Gemini client management
        validation.py            ← input validation
        sanitization.py          ← post-processing
        registry.py              ← prompt routing
        service.py               ← generate_body(), regenerate_body()
        ai_service.py            ← DEPRECATED re-export
    views/
        __init__.py              ← re-exports for urls.py
        common.py                ← shared helpers, JSON loading
        office_order.py          ← Office Order views
        circular.py              ← Circular views
        policy.py                ← Policy views
```

---

## ⚠️ Known Remaining Items (Future Phases)

1. **`ai_service.py` deletion** — Once confirmed no external code imports from it, delete.
2. **Type narrowing in views** — Django `request.POST.get()` returns `str`, not `Literal["en", "hi"]`. Runtime validation handles this; type stubs could be added later.
3. **Deterministic output guardrails** — Structural checks are still soft (warn-only). Hard rejection is deferred until prompt tuning is more mature.
4. **`_strip_markdown` lossy behaviour** — Documented but not changed. Acceptable for government documents.

