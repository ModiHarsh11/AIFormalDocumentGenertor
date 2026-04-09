# 📄 BISAG-N AI Formal Document Generator — Documentation

> **AI-powered formal document generation subsystem** for BISAG-N (Bhaskaracharya National Institute for Space Applications and Geo-informatics), built on Django + Google Gemini + LangChain.

---

## 📁 Documentation Structure

```
docs/
├── README.md                    ← You are here
│
├── architecture/
│   ├── overview.md              ← System architecture & layer diagram
│   ├── layered_design.md        ← Why layers matter; boundary rationale
│   └── folder_structure.md      ← Codebase map with file responsibilities
│
├── api/
│   ├── endpoints.md             ← All HTTP endpoints (URL, method, params)
│   ├── ai_service.md            ← ai_service.py public API reference
│   └── prompt_layer.md          ← Prompt templates & versioning reference
│
├── phases/
│   ├── phase1_architecture.md   ← From monolith to layered design
│   ├── phase2_sdk_migration.md  ← google-generativeai → google-genai
│   ├── phase3_prompt_hardening.md ← Prompt injection hardening
│   ├── phase4_output_validation.md ← Sanitization & guardrails
│   ├── phase5_prompt_abstraction.md ← LangChain prompt layer
│   ├── phase6_regeneration.md   ← Regeneration symmetry
│   ├── phase7_prompt_hardening_all_types.md ← Uniform prompt layer across all doc types
│   ├── phase8_service_unification.md ← Registry architecture & generic functions
│   ├── phase9_output_guardrails.md ← Structural validation & observability
│   ├── phase10_production_settings.md ← Settings split, runtime fixes, dead code removal
│   ├── phase11_ux_enhancements.md ← Frontend UX: counters, spinners, toast, localStorage, copy/print
│   └── phase12_form_intelligence.md ← From/To badges, validation, clear form, auto-year, tab memory
│
└── guides/
    ├── setup.md                 ← Local development setup
    ├── adding_document_type.md  ← How to add a new document type
    ├── environment_variables.md ← All required env vars
    └── frontend_ux_features.md  ← All client-side UX features reference
```

---

## 🚀 Quick Start

```bash
# 1. Activate the virtual environment
.\finale_BISAG-N\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables (see docs/guides/environment_variables.md)
cp ai_formal_generator/.env.example ai_formal_generator/.env
# Edit .env and set GEMINI_API_KEY=your-key-here

# 4. Run migrations & start server
cd ai_formal_generator
python manage.py migrate
python manage.py runserver
```

---

## 🧩 Supported Document Types

| Document Type | Languages | AI Body Generation | Regeneration | PDF | DOCX |
|---|---|---|---|---|---|
| Office Order | EN / HI | ✅ | ✅ | ✅ | ✅ |
| Circular | EN / HI | ✅ | ✅ | ✅ | ✅ |
| Policy | EN / HI | ✅ | ✅ | ✅ | ✅ |

---

## 🏗️ System at a Glance

```
Browser / Frontend
      ↓  HTTP POST
views.py  (Django HTTP layer)
      ↓  calls
services/ai_service.py  (transport + validation)
      ↓  uses
prompts/office_order.py  (LangChain PromptTemplate)
      ↓  calls
Google Gemini API  (google-genai SDK)
      ↓  returns
Sanitized plain-text body  →  PDF / DOCX
```

See [`architecture/overview.md`](architecture/overview.md) for the full diagram.

---

## 📌 Key Design Decisions

- **Layered architecture** — each layer has a single responsibility
- **Prompt versioning** — every template carries `PROMPT_VERSION`, logged in every API call
- **Registry-based routing** — `DOCUMENT_PROMPT_REGISTRY` maps document types to prompt builders; adding a type = 1 prompt file + 1 registry entry
- **Output validation** — markdown stripping + header-leakage guards (EN + HI, all document types)
- **Structural guardrails** — soft checks for paragraph count, bullet leakage, and excessive length (warn, never reject)
- **SDK modernization** — migrated to `google-genai` (actively maintained)
- **Prompt hardening** — structured delimiters prevent injection/override
- **Type safety** — `DocumentType`, `Language` as `Literal` types; `Callable`-typed registry
- **No over-engineering** — no LangChain agents, no memory, no chains

---

*Last updated: February 23, 2026 — Phase 12*

