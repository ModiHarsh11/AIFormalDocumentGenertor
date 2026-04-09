# 🧠 Phase 2 — SDK Migration (Strategic Upgrade)

## What Changed

The project migrated from:

```
google-generativeai      ← deprecated, legacy
```

to:

```
google-genai             ← actively maintained, modern SDK
```

---

## This Is Not Cosmetic

A library deprecation is not just a version bump notice. It means:

| Risk | Without Migration | After Migration |
|---|---|---|
| Future breakage | API changes will not be backported | SDK tracks Gemini API evolution |
| Security stagnation | CVEs accumulate without fixes | Security patches are released |
| Technical debt | Code uses patterns that will be removed | Code uses current patterns |
| Reviewer signal | Signals unawareness of ecosystem | Signals active engineering hygiene |

---

## The Old SDK Pattern

```python
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

response = model.generate_content(prompt)
return response.text
```

**Problems:**
- Global configuration (`genai.configure`) is a side effect
- No explicit client object — hard to test, hard to mock
- `GenerativeModel` is a deprecated class in newer SDK versions
- `GenerationConfig` constructor is different
- No structured config object

---

## The New SDK Pattern

```python
from google import genai
from google.genai import types as genai_types

# Explicit client object — testable and injectable
_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client

# Structured config object
GENERATION_CONFIG = genai_types.GenerateContentConfig(
    temperature=0.3,
    max_output_tokens=300,
)

# Clean API call
response = _get_client().models.generate_content(
    model=MODEL_NAME,
    contents=prompt,
    config=GENERATION_CONFIG,
)
```

---

## Key Improvements

### 1. Client Abstraction
```python
_client: genai.Client | None = None
```
The client is a concrete object. It can be:
- Injected in tests
- Reset via `_reset_client()`
- Configured differently per environment
- Mocked without patching global state

### 2. `GenerateContentConfig`
The new SDK uses a typed config object instead of a loose kwargs dict.  
Type-safe, IDE-autocomplete-friendly, documents intent clearly.

### 3. Response Handling
```python
if not response.candidates:
    raise RuntimeError(
        "AI returned empty response (possibly blocked by safety filters.)"
    )
text = response.text.strip()
```
Explicit check for empty candidates — handles safety filter blocks gracefully.

### 4. `_reset_client()`
```python
def _reset_client() -> None:
    global _client
    _client = None
```
Enables API key rotation without restarting the server.  
Useful for testing without polluting state between test cases.

---

## Model Configuration

```python
MODEL_NAME = getattr(settings, "LLM_MODEL", "gemini-2.5-flash-lite")
```

`gemini-2.5-flash-lite` is:
- Fast (optimised for latency)
- Cost-efficient (lower token cost than Pro)
- Sufficient for formal paragraph generation (bounded output task)

Override by setting `LLM_MODEL` in `settings.py` or environment — no code change required.

---

## Outcome

✅ Modern SDK (`google-genai`) in use  
✅ Explicit client object — testable  
✅ Typed `GenerateContentConfig`  
✅ Proper safety-filter response handling  
✅ `_reset_client()` for key rotation  
✅ Model name is configurable via settings

