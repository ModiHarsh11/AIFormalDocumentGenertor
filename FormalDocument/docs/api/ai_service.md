# 🤖 AI Service API Reference

**File:** `generator/services/ai_service.py`

The service layer is the single point of contact between the Django views and the Gemini API. It owns input validation, transport, post-processing, structured logging, and prompt routing via a registry.

---

## Configuration

```python
MODEL_NAME = getattr(settings, "LLM_MODEL", "gemini-2.5-flash-lite")
SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "hi")
Language = Literal["en", "hi"]
DocumentType = Literal["office", "circular", "policy"]

# Read-only config shared across all generate_content calls.
GENERATION_CONFIG = genai_types.GenerateContentConfig(
    temperature=0.3,        # Low temperature → more deterministic, formal output
    max_output_tokens=300,  # Keeps responses concise (body paragraph only)
)
```

Override `MODEL_NAME` via `settings.LLM_MODEL` without changing code.

---

## Prompt Registry

```python
DOCUMENT_PROMPT_REGISTRY: dict[DocumentType, dict[str, Callable[..., str]]] = {
    "office":   {"generate": ..., "regenerate": ...},
    "circular": {"generate": ..., "regenerate": ...},
    "policy":   {"generate": ..., "regenerate": ...},
}

PROMPT_VERSION_REGISTRY: dict[DocumentType, str] = {
    "office":   "OfficeOrder_v1",
    "circular": "Circular_v1",
    "policy":   "Policy_v1",
}
```

- Registry key is `DocumentType` (a `Literal`), **not `str`** — prevents invalid keys at type-check time
- Prompt version is logged in every API call context for traceability

---

## Public Functions

### `generate_body(document_type, topic, language="en") → str`

**Primary API.** Generates the body for any supported document type.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `document_type` | `DocumentType` | ✅ | `"office"`, `"circular"`, or `"policy"` |
| `topic` | `str` | ✅ | The subject/topic for the document body |
| `language` | `Language` | ❌ | Output language. Default: `"en"` |

**Returns:** Clean plain-text body string (no markdown, no leaked headers)

**Raises:**
- `ValueError` — if `document_type` is unknown, `topic` is empty, or `language` is unsupported
- `RuntimeError` — if Gemini API fails or returns empty/invalid response

**Example:**
```python
from generator.services.ai_service import generate_body

body = generate_body(
    document_type="office",
    topic="Extension of office working hours during year-end audit",
    language="en",
)
```

---

### `regenerate_body(document_type, topic, previous_body, refinement_prompt, language="en") → str`

**Primary API.** Refines a previously generated document body.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `document_type` | `DocumentType` | ✅ | `"office"`, `"circular"`, or `"policy"` |
| `topic` | `str` | ✅ | Original topic used in first generation |
| `previous_body` | `str` | ✅ | The body text shown to the user |
| `refinement_prompt` | `str` | ✅ | User's refinement/change instruction |
| `language` | `Language` | ❌ | Output language. Default: `"en"` |

**Returns:** Refined plain-text body string

**Raises:**
- `ValueError` — if any required field is empty, `document_type` unknown, or `language` unsupported
- `RuntimeError` — on API failure or empty validation result

---

### Backward-Compatibility Wrappers

These thin wrappers delegate to `generate_body` / `regenerate_body`. Views can continue calling them unchanged.

```python
generate_office_body(topic, language)          → generate_body("office", ...)
regenerate_office_body(topic, ...)             → regenerate_body("office", ...)
generate_circular_body(topic, language)        → generate_body("circular", ...)
regenerate_circular_body(topic, ...)           → regenerate_body("circular", ...)
generate_policy_body(topic, language)          → generate_body("policy", ...)
regenerate_policy_body(topic, ...)             → regenerate_body("policy", ...)
```

Remove only after all callers are migrated to the generic functions.

---

## Private Functions

> These are internal implementation details. Do not call them from views.

### `_get_client() → genai.Client`

Lazily initialises and caches a singleton `genai.Client` instance.  
Reads `settings.GEMINI_API_KEY`.  
Thread-safe per-worker (acceptable at current scale).

### `_reset_client() → None`

Resets the cached client. Used in tests or for API key rotation.

### `_validate_document_type(document_type: DocumentType) → None`

Raises `ValueError` if `document_type` is not in `DOCUMENT_PROMPT_REGISTRY`.  
Parameter type is `DocumentType` (not `str`) — consistent with public functions.

### `_validate_inputs(language, **fields) → None`

Validates language against `SUPPORTED_LANGUAGES`, then checks each keyword argument for emptiness. Fails on the first bad value.

### `_strip_markdown(text: str) → str`

Removes common LLM markdown artifacts:
- Code blocks (` ```...``` `)
- Bold/italic asterisks (`**`, `*`)
- Underscore italics (`_text_`)
- Bullet lists (`-`, `•`)
- Numbered lists (`1.`, `2.`)
- Headings (`#`, `##`)
- Double spaces

> ⚠️ **Lossy:** This is destructive sanitization. Literal `*` and `_` in content will be removed. Acceptable for government document bodies which should never contain these characters.

### `_validate_body(text: str) → str`

Strips any lines that match header-leakage patterns, then calls `_check_structure()`.  
Covers both English and Hindi headers across all document types.

**Detected leakage patterns:**

| English | Hindi |
|---------|-------|
| `Subject:` | `विषय:` |
| `Reference:` | `संदर्भ:` |
| `Date:` | `दिनांक:` |
| `From:` | `प्रेषक:` |
| `To:` | `प्राप्तकर्ता:` |
| `Signature:` | `हस्ताक्षर:` |
| `Office Order:` | `कार्यालय आदेश:` |
| `Circular:` | `परिपत्र:` |
| `Policy:` | `नीति:` |

### `_check_structure(text: str) → None`

Soft structural validation — logs warnings, never raises. Checks:

| Check | Threshold | Log Level |
|-------|-----------|-----------|
| Paragraph count = 0 | 0 | WARNING |
| Paragraph count > 5 | > 5 | WARNING |
| Bullet points detected | `[-•*]\s` at line start | WARNING |
| Numbered lists detected | `\d+[.)]\s` at line start | WARNING |
| Body length excessive | > 3000 chars | WARNING |

Production monitoring can alert on repeated violations.

### `_generate(prompt, *, context) → str`

Core internal function. Calls `genai.Client.models.generate_content()`.

Logging context dict example:
```python
{
    "fn": "generate_body",
    "document_type": "office",
    "prompt_version": "OfficeOrder_v1",
    "language": "en",
    "topic_length": 47,
}
```

On failure, logs via `logger.exception()` with `extra={"context": ctx}` for structured log aggregation.

---

## Error Taxonomy

```
ValueError
  ├─ "Unsupported document_type 'xxx'. Must be one of: ('office', 'circular', 'policy')"
  ├─ "'topic' cannot be empty."
  ├─ "'previous_body' cannot be empty."
  ├─ "'refinement_prompt' cannot be empty."
  └─ "Unsupported language 'xx'. Must be one of: ('en', 'hi')"

RuntimeError
  ├─ "GEMINI_API_KEY is not configured."
  ├─ "AI returned empty response (possibly blocked by safety filters)."
  ├─ "AI returned invalid or empty body after validation."
  └─ "AI generation failed. Please try again."   ← wraps SDK exceptions
```

---

## Extending for New Document Types

To add a new document type (e.g., Advertisement):

### 1. Create prompt file
```python
# generator/prompts/advertisement.py
PROMPT_VERSION = "Advertisement_v1"
# ... templates + builders (same pattern as existing files)
```

### 2. Update `ai_service.py`

```python
from generator.prompts.advertisement import (
    build_generation_prompt as build_advertisement_generation_prompt,
    build_regeneration_prompt as build_advertisement_regeneration_prompt,
    PROMPT_VERSION as ADVERTISEMENT_PROMPT_VERSION,
)

# Update Literal
DocumentType = Literal["office", "circular", "policy", "advertisement"]

# Add to registries
DOCUMENT_PROMPT_REGISTRY["advertisement"] = {
    "generate": build_advertisement_generation_prompt,
    "regenerate": build_advertisement_regeneration_prompt,
}
PROMPT_VERSION_REGISTRY["advertisement"] = ADVERTISEMENT_PROMPT_VERSION
```

### 3. Update `_LEAKAGE_PATTERNS`
Add `Advertisement` and its Hindi equivalent to the regex.

### 4. (Optional) Add compat wrapper
```python
def generate_advertisement_body(topic, language="en"):
    return generate_body("advertisement", topic, language)
```

**Zero new service logic.** The registry handles routing.
