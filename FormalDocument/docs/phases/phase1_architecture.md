# 🧠 Phase 1 — From Prototype to Layered Architecture

## The Before State

When the project started, everything lived inside `views.py`:

```
views.py
  ├─ Prompt strings (inline f-strings mixed with logic)
  ├─ Gemini SDK call
  ├─ Error handling
  ├─ Regeneration logic
  └─ HTTP response logic
```

This is the natural starting point for any Django project — and it was the right call for the prototype stage. Getting it working matters first.

The problem is that a monolith like this has no internal boundaries. Every part of the system is aware of every other part.

**Practical consequences:**

- Changing a prompt tone required navigating 1000+ lines of `views.py`
- Circular, Policy, and Office Order each duplicated the same generation pattern
- Swapping the Gemini SDK would require touching view functions
- Unit testing was impossible without HTTP context
- A bug in generation silently affected all three document types

---

## The Transformation

The codebase was restructured into three distinct layers:

```
views.py                           ← HTTP only
    ↓
services/ai_service.py             ← Transport + Validation
    ↓
prompts/office_order.py            ← Prompt content
    ↓
Google Gemini API
```

### What Changed

**Before — inline in `views.py`:**
```python
def generate_body(request):
    # prompt built here
    if lang == "hi":
        system_prompt = "آپ BISAG-N کے..."
    else:
        system_prompt = "You are drafting..."
    
    full_prompt = system_prompt + "\n\nTopic:\n" + prompt
    
    # API called here
    res = gemini_model.generate_content(full_prompt)
    return HttpResponse(res.text.strip())
```

**After — clean delegation:**
```python
def generate_body(request):
    prompt = request.POST.get("body_prompt", "").strip()
    lang = request.POST.get("language", "en")
    
    from .services.ai_service import generate_office_body
    body = generate_office_body(prompt, lang)
    return HttpResponse(body)
```

The view no longer knows what the prompt says. It no longer knows which SDK is used. It does one thing: handle HTTP.

---

## The Boundaries That Matter

| Boundary | What it isolates |
|---|---|
| `views.py` ↔ `ai_service.py` | HTTP concerns from AI concerns |
| `ai_service.py` ↔ `prompts/` | Transport concerns from prompt content |
| `prompts/` ↔ Gemini SDK | Wording from delivery mechanism |

Boundaries are what make systems durable.

When you change a prompt, you touch `prompts/office_order.py` only.  
When you swap the LLM SDK, you touch `ai_service.py` only.  
When you change the HTTP response format, you touch `views.py` only.

That isolation is the value of Phase 1.

---

## Outcome

✅ Clear layer separation  
✅ Single-responsibility files  
✅ View functions become thin and readable  
✅ AI logic becomes independently testable  
✅ Prompt content becomes independently editable

