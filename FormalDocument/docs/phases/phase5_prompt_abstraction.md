# 🧠 Phase 5 — Prompt Abstraction with LangChain

## What Changed

Prompt strings moved from inline f-strings in `views.py` to dedicated `PromptTemplate` objects in `generator/prompts/office_order.py`.

---

## Before — Inline Prompt Construction

```python
# views.py — the old way
def generate_body(request):
    if lang == "hi":
        system_prompt = f"""
आप BISAG-N के लिए एक आधिकारिक कार्यालय आदेश की मुख्य सामग्री लिख रहे हैं।
नियम:
- कम से कम 2–3 वाक्यों का एक औपचारिक अनुच्छेद लिखें।
...
Today's Date: {today}
"""
    else:
        system_prompt = f"""
You are drafting the BODY of an official government Office Order for BISAG-N.
Rules:
...
Today's Date: {today}
"""
    full_prompt = system_prompt + "\n\nTopic:\n" + prompt
```

Problems:
- Prompt wording is buried inside view logic
- Both languages live in the same function, making each harder to read
- No version tracking
- No reuse — circular and policy duplicate similar strings
- Changing tone requires navigating view code

---

## After — LangChain PromptTemplate

```python
# prompts/office_order.py
from langchain.prompts import PromptTemplate

PROMPT_VERSION = "OfficeOrder_v1"

GENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "version"],
    template="""
[Prompt Version: {version}]

You are drafting the BODY of an official government Office Order for BISAG-N.
...
<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
"""
)

def build_generation_prompt(topic: str, language: str) -> str:
    template = GENERATION_TEMPLATE_HI if language == "hi" else GENERATION_TEMPLATE_EN
    return template.format(topic=topic, version=PROMPT_VERSION)
```

```python
# ai_service.py — the service layer
from generator.prompts.office_order import build_generation_prompt

def generate_office_body(topic: str, language: str = "en") -> str:
    full_prompt = build_generation_prompt(topic, language)
    return _generate(full_prompt, context={...})
```

---

## What LangChain `PromptTemplate` Provides

### Declared Variables

```python
PromptTemplate(
    input_variables=["topic", "version"],
    template="..."
)
```

The template declares what variables it needs. If you call `.format()` without providing a required variable, it raises a `KeyError`. This is a compile-time-style check at prompt construction time.

### `.format()` Call Safety

LangChain's `.format()` method validates that all declared `input_variables` are provided before substituting. This is stricter than Python's native `str.format()` which would silently skip or error differently.

### Separation of Content from Delivery

The template object holds the wording. The service layer calls `.format()`. Neither needs to know about the other's internals.

---

## Modularity Benefits

| Capability | Before | After |
|---|---|---|
| Change wording | Edit `views.py` | Edit `prompts/office_order.py` only |
| Add A/B version | Requires branching view logic | Add `GENERATION_TEMPLATE_EN_v2`, update builder |
| Add language | Add `elif` in view | Add template, update `build_*_prompt()` |
| Introduce doc-specific logic | Scattered across views | Isolated in each prompt file |
| Swap LLM backend | Requires view changes | Service layer change only |
| Prompt versioning | Not possible inline | `PROMPT_VERSION` constant, embedded in prompt |

---

## Document-Type Isolation

Each document type gets its own prompt file:

```
prompts/
  ├── office_order.py    ← PROMPT_VERSION = "OfficeOrder_v1"
  ├── circular.py        ← PROMPT_VERSION = "Circular_v1"      (to be created)
  └── policy.py          ← PROMPT_VERSION = "Policy_v1"         (to be created)
```

Circular and Policy currently still use inline prompts in `views.py`. Migrating them follows the exact same pattern as Office Order.

---

## What Was Not Used from LangChain

LangChain provides:
- Chains (multi-step pipelines)
- Agents (tool-using LLM loops)
- Memory (conversation history)
- Output parsers (structured extraction)
- LLM wrappers (unified backend interface)

Only `PromptTemplate` was used. This was deliberate.

The use case here is a single-call, bounded-output workflow. Adding chains or agents would introduce unnecessary complexity without any benefit. The value of LangChain at this stage is purely the template abstraction — clean variable substitution and declaration.

---

## Outcome

✅ Prompt content isolated to `prompts/office_order.py`  
✅ Service layer has no awareness of prompt wording  
✅ Templates are versioned (`PROMPT_VERSION`)  
✅ Language validated in prompt layer  
✅ Four templates: generate EN, generate HI, regen EN, regen HI  
✅ Changing wording requires no service or view changes  
✅ A/B prompt versions are now possible  
✅ LangChain used minimally — only `PromptTemplate`

