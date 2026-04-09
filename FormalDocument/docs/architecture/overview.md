# 🏗️ System Architecture Overview

## The Full Request Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER / FRONTEND                        │
│  HTML form  →  AJAX POST (fetch)  →  Django URL router           │
└──────────────────────────────┬──────────────────────────────────┘
                               │  HTTP POST
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1 — HTTP / VIEW LAYER                   │
│  generator/views.py                                              │
│  • Parses POST params (topic, language, previous_body, …)        │
│  • Calls service layer                                           │
│  • Returns HttpResponse / JsonResponse                           │
│  • Handles session (doc_data, circular_data, …)                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │  function call
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 2 — SERVICE / TRANSPORT LAYER             │
│  generator/services/ai_service.py                                │
│  • Input validation (empty topic, unsupported language)          │
│  • Lazy Gemini client initialisation (_get_client)               │
│  • Registry-based prompt routing (DOCUMENT_PROMPT_REGISTRY)      │
│  • Calls Gemini API (google-genai SDK)                           │
│  • Post-processes response (_strip_markdown, _validate_body)     │
│  • Structural validation (_check_structure — soft, non-blocking) │
│  • Structured logging with context dict + prompt version         │
└──────────────────────────────┬──────────────────────────────────┘
                               │  build_*_prompt()
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LAYER 3 — PROMPT / TEMPLATE LAYER              │
│  generator/prompts/office_order.py                               │
│  generator/prompts/circular.py                                   │
│  generator/prompts/policy.py                                     │
│  • LangChain PromptTemplate definitions (EN + HI)                │
│  • Prompt version constant (PROMPT_VERSION)                      │
│  • Language validation + Literal type alias                      │
│  • build_generation_prompt()                                     │
│  • build_regeneration_prompt()                                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │  formatted string prompt
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 4 — EXTERNAL AI / LLM LAYER               │
│  Google Gemini API  (model: gemini-2.5-flash-lite)               │
│  SDK: google-genai  (actively maintained)                        │
│  Config: GenerateContentConfig(temperature=0.3, max_tokens=300)  │
└──────────────────────────────┬──────────────────────────────────┘
                               │  response.text
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                LAYER 5 — OUTPUT / DOCUMENT LAYER                 │
│  generator/utils/docx_generator.py                               │
│  WeasyPrint (PDF rendering via HTML templates)                   │
│  python-docx  (DOCX assembly with logo, tables, fonts)           │
│  Jinja/Django templates: pdf_*.html, result_*.html               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

| Component | File | Responsibility |
|---|---|---|
| URL Router | `ai_formal_generator/urls.py` + `generator/urls.py` | Route HTTP requests to view functions |
| Views | `generator/views/` package | HTTP layer — split by document type |
| AI Service | `generator/services/` package | Transport, validation, registry routing, sanitization |
| Prompt Layer | `generator/prompts/` package | Prompt construction & versioning (shared via `_shared.py`) |
| Constants | `generator/constants.py` | `DESIGNATION_MAP` (EN/HI designations) |
| Fonts | `static/generator/fonts/` | Devanagari (Hindi) font files for WeasyPrint PDF |
| Templates | `generator/templates/generator/` | HTML templates for render + PDF |
| Static | `static/generator/` | Logo, CSS, fonts |
| Config JSON | `generator/data/*.json` | Header strings, people list |

---

## Data Flow — Generation

```
User submits document_type + topic + language
        ↓
views.generate_body()
        ↓ document_type, topic, lang
ai_service.generate_body()
        ↓ validates, looks up DOCUMENT_PROMPT_REGISTRY
prompts.build_generation_prompt()   →   returns formatted string
        ↓ full_prompt
genai.Client.models.generate_content()
        ↓ response.text
_strip_markdown()   →   _validate_body()   →   _check_structure()
        ↓ clean text
HttpResponse(clean_body)
        ↓
Frontend displays in textarea
```

## Data Flow — Regeneration

```
User provides refinement_prompt + previous_body
        ↓
views.regenerate_office_body()
        ↓ document_type, topic, previous_body, refinement_prompt, lang
ai_service.regenerate_body()
        ↓ validates, looks up DOCUMENT_PROMPT_REGISTRY
prompts.build_regeneration_prompt()   →   structured prompt with 3 input blocks
        ↓ full_prompt
genai.Client.models.generate_content()
        ↓
_strip_markdown()   →   _validate_body()   →   _check_structure()
        ↓
HttpResponse(refined_body)
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Web Framework | Django 5.2 |
| LLM Provider | Google Gemini (`gemini-2.5-flash-lite`) |
| LLM SDK | `google-genai` (new, actively maintained) |
| Prompt Framework | LangChain `PromptTemplate` |
| PDF Generation | WeasyPrint |
| DOCX Generation | python-docx |
| Database | SQLite (dev) |
| Language Support | English + Hindi (Devanagari) |

