# 🔀 Phase 8 — Service Unification & Registry Architecture

## The Problem

Before this phase, `ai_service.py` had **six separate public functions**:

```python
generate_office_body(topic, language)
regenerate_office_body(topic, previous_body, refinement_prompt, language)
generate_circular_body(topic, language)
regenerate_circular_body(topic, previous_body, refinement_prompt, language)
generate_policy_body(topic, language)
regenerate_policy_body(topic, previous_body, refinement_prompt, language)
```

Each function was a copy-paste of the same pattern:
1. Validate inputs
2. Select prompt builder
3. Call `_generate()`
4. Return result

Adding a fourth document type required writing **two more functions** with identical logic.

---

## The Solution — Prompt Registry + Generic Functions

### Step 1 — `DocumentType` Literal

```python
DocumentType = Literal["office", "circular", "policy"]
```

Type-checked at static analysis time. No magic strings.

### Step 2 — Prompt Registry

```python
DOCUMENT_PROMPT_REGISTRY: dict[DocumentType, dict[str, Callable[..., str]]] = {
    "office": {
        "generate": build_office_generation_prompt,
        "regenerate": build_office_regeneration_prompt,
    },
    "circular": {
        "generate": build_circular_generation_prompt,
        "regenerate": build_circular_regeneration_prompt,
    },
    "policy": {
        "generate": build_policy_generation_prompt,
        "regenerate": build_policy_regeneration_prompt,
    },
}
```

Key design decisions:
- **Registry key is `DocumentType`, not `str`** — prevents `REGISTRY["random"] = ...` from passing type checks
- **`Callable[..., str]`** — tells the type checker that values are callable and return `str`

### Step 3 — Generic `generate_body`

```python
def generate_body(
    document_type: DocumentType,
    topic: str,
    language: Language = "en",
) -> str:
    _validate_document_type(document_type)
    _validate_inputs(language, topic=topic)
    topic = topic.strip()

    prompt_builder = DOCUMENT_PROMPT_REGISTRY[document_type]["generate"]

    return _generate(
        prompt_builder(topic, language),
        context={
            "fn": "generate_body",
            "document_type": document_type,
            "prompt_version": PROMPT_VERSION_REGISTRY.get(document_type, "unknown"),
            "language": language,
            "topic_length": len(topic),
        },
    )
```

### Step 4 — Generic `regenerate_body`

Same pattern, with additional `previous_body` and `refinement_prompt` fields.

### Step 5 — Backward-Compatibility Wrappers

```python
def generate_office_body(topic: str, language: Language = "en") -> str:
    """Compat wrapper → generate_body('office', ...)."""
    return generate_body("office", topic, language)
```

Views keep calling the old functions. Zero breakage.

---

## Prompt Version Traceability

### The Gap

Prompt files carry `PROMPT_VERSION` (e.g., `"OfficeOrder_v1"`), but this version was **never logged** in the service layer. If someone bumps to `OfficeOrder_v2`, there would be no trace of which version produced which output.

### The Fix

```python
from generator.prompts.office_order import PROMPT_VERSION as OFFICE_PROMPT_VERSION
from generator.prompts.circular import PROMPT_VERSION as CIRCULAR_PROMPT_VERSION
from generator.prompts.policy import PROMPT_VERSION as POLICY_PROMPT_VERSION

PROMPT_VERSION_REGISTRY: dict[DocumentType, str] = {
    "office": OFFICE_PROMPT_VERSION,
    "circular": CIRCULAR_PROMPT_VERSION,
    "policy": POLICY_PROMPT_VERSION,
}
```

Every `_generate()` context now includes `"prompt_version"`:

```python
context={
    "fn": "generate_body",
    "document_type": "office",
    "prompt_version": "OfficeOrder_v1",  # ← now traceable
    "language": "en",
    "topic_length": 47,
}
```

---

## Validation Architecture

### Validation Order

```
_validate_document_type(document_type)   ← First: is the type known?
_validate_inputs(language, topic=topic)  ← Second: is the language valid? Are fields non-empty?
```

Fail fast. Descriptive errors. Consistent order across both functions.

### `_validate_document_type`

```python
def _validate_document_type(document_type: DocumentType) -> None:
    """Raise ValueError if *document_type* is not in the registry."""
    if document_type not in DOCUMENT_PROMPT_REGISTRY:
        raise ValueError(
            f"Unsupported document_type '{document_type}'. "
            f"Must be one of: {tuple(DOCUMENT_PROMPT_REGISTRY)}"
        )
```

Note: parameter type is `DocumentType`, not `str` — consistent with the public functions that call it.

### `_validate_inputs`

```python
def _validate_inputs(language: str, **fields: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(...)
    for name, value in fields.items():
        if not (value or "").strip():
            raise ValueError(f"'{name}' cannot be empty.")
```

One helper, used by both `generate_body` and `regenerate_body`. No duplicated validation code.

---

## Before vs After

| Metric | Before | After |
|--------|--------|-------|
| Public functions (real logic) | 6 | **2** |
| Compat wrappers (thin) | 0 | 6 |
| Lines of validation code | ~60 (duplicated) | ~15 (shared) |
| Steps to add new document type | New prompt file + 2 service functions + validation | New prompt file + **1 registry entry** |
| Prompt version logged | ❌ | ✅ |
| `document_type` type-checked | ❌ (was `str`) | ✅ (`Literal`) |

---

## Adding a New Document Type (Updated Process)

To add e.g. "advertisement":

### 1. Create prompt file
```python
# generator/prompts/advertisement.py
PROMPT_VERSION = "Advertisement_v1"
# ... templates, builders (same pattern as other files)
```

### 2. Update `ai_service.py`

```python
# Imports
from generator.prompts.advertisement import (
    build_generation_prompt as build_advertisement_generation_prompt,
    build_regeneration_prompt as build_advertisement_regeneration_prompt,
    PROMPT_VERSION as ADVERTISEMENT_PROMPT_VERSION,
)

# Update Literal type
DocumentType = Literal["office", "circular", "policy", "advertisement"]

# Add to registries
DOCUMENT_PROMPT_REGISTRY["advertisement"] = {
    "generate": build_advertisement_generation_prompt,
    "regenerate": build_advertisement_regeneration_prompt,
}
PROMPT_VERSION_REGISTRY["advertisement"] = ADVERTISEMENT_PROMPT_VERSION
```

### 3. (Optional) Add compat wrapper if views need it

```python
def generate_advertisement_body(topic, language="en"):
    return generate_body("advertisement", topic, language)
```

**Zero new service logic.** The registry handles routing.

---

## Outcome

✅ 6 functions collapsed into 2 + thin wrappers  
✅ Registry-based routing — no switch/case, no if/elif chains  
✅ Prompt version traceable in every log entry  
✅ `DocumentType` is a `Literal`, not `str` — type-checked  
✅ Validation order is consistent and explicit  
✅ Backward compatibility preserved — views unchanged  
✅ Adding a document type = 1 prompt file + 1 registry entry  

