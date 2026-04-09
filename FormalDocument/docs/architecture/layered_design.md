# 🧱 Layered Design — Boundaries & Rationale

## Why Layers Matter

A monolith works for demos. It collapses under scale.

When everything lives in one place — prompts, API calls, error handling, HTTP logic — every change touches everything. A one-line prompt tweak requires you to navigate 1000-line `views.py`. A SDK upgrade might silently break prompt formatting. A bug in generation logic leaks into HTTP responses.

Layers introduce **boundaries**. Boundaries are what make systems durable.

---

## The Original Monolith

```
views.py
  ├─ Prompt strings (inline f-strings)
  ├─ Gemini SDK call (google-generativeai)
  ├─ Error handling
  ├─ Regeneration logic (ad-hoc)
  └─ HTTP response
```

**Problems:**
- Changing tone required editing `views.py`
- No reuse: circular, policy, office order all duplicated prompt logic
- SDK changes would cascade through view functions
- No consistent output validation
- Testing was effectively impossible without HTTP context

---

## The Current Layered Architecture

```
views.py                          ← LAYER 1: HTTP only
    ↓  calls
services/ai_service.py            ← LAYER 2: Transport + Validation
    ↓  uses
prompts/office_order.py           ← LAYER 3: Prompt content + versioning
    ↓  sends to
Google Gemini API (google-genai)  ← LAYER 4: External LLM
    ↓  result flows back through
Output sanitization               ← Built into Layer 2
```

---

## Each Layer's Contract

### Layer 1 — `views.py`
**Knows:** HTTP request/response format, session keys, template names  
**Does NOT know:** What the prompt says, how the API works, what SDK is used  
**Contract:** Accepts POST params → delegates → returns `HttpResponse`

```python
# views.py — correct usage
from .services.ai_service import generate_office_body

body = generate_office_body(prompt, lang)
return HttpResponse(body)
```

### Layer 2 — `services/ai_service.py`
**Knows:** Input validation rules, API configuration, sanitization logic, prompt registry routing
**Does NOT know:** What the prompt says (delegates to prompt layer)
**Contract:** Accepts `(document_type, topic, language)` → returns clean `str`

```python
# ai_service.py — correct usage
prompt_builder = DOCUMENT_PROMPT_REGISTRY[document_type]["generate"]
return _generate(prompt_builder(topic, language), context={...})
```

### Layer 3 — `prompts/office_order.py` (+ `circular.py`, `policy.py`)
**Knows:** Prompt wording, tone, delimiters, language rules, version  
**Does NOT know:** How the API is called, what SDK is used  
**Contract:** Accepts `(topic, language)` → returns formatted prompt `str`

```python
# prompt layer — correct usage
return GENERATION_TEMPLATE_EN.format(topic=topic, version=PROMPT_VERSION)
```

---

## What Each Boundary Prevents

| Boundary | Prevents |
|---|---|
| views ↔ service | HTTP coupling to AI logic |
| service ↔ prompt | Transport coupling to prompt wording |
| prompt ↔ LLM SDK | Prompt content coupling to SDK version |

---

## The Regeneration Symmetry Rule

The regeneration path follows **exactly the same layers** as the generation path:

| Step | Generation | Regeneration |
|---|---|---|
| HTTP layer | `views.generate_body()` | `views.regenerate_office_body()` |
| Service layer | `ai_service.generate_body()` | `ai_service.regenerate_body()` |
| Prompt layer | `build_generation_prompt()` | `build_regeneration_prompt()` |
| Validation | `_strip_markdown` + `_validate_body` + `_check_structure` | Same |
| Logging | Yes (with `prompt_version`) | Same |

Asymmetry is where bugs breed. Both paths share identical guardrails.

---

## What Was Intentionally Left Out

The following were considered and explicitly **not added**:

| Not Added | Reason |
|---|---|
| LangChain chains | Not needed — single-call workflow |
| LangChain agents | Not needed — no tool use or multi-step reasoning |
| LangChain memory | Not needed — context passed explicitly |
| LLM output parsing | Not needed — plain text response |
| Streaming | Not needed at current scale |
| Async views | Not needed — response time acceptable |
| Multiple LLM backends | Not needed yet — abstraction ready via `_get_client()` |

Keeping control is rare. Premature abstraction is a form of technical debt.

