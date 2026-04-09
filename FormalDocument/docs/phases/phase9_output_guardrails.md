# 🔬 Phase 9 — Output Guardrails & Observability Hardening

## What This Phase Covers

This phase tightens the service layer's defensive posture:

1. **Structural validation** — soft checks for paragraph count, bullet leakage, excessive length
2. **Leakage pattern expansion** — covers Circular and Policy headers (EN + HI)
3. **Lossy sanitization awareness** — documents destructive `_strip_markdown` behaviour
4. **Logging precision** — structured `extra=` logging, no redundant exception messages
5. **Type precision** — context dict typed as `dict[str, object]`, not bare `dict`

---

## 1. Structural Validation (`_check_structure`)

### The Problem

Prompts say "Write 2–3 paragraphs" and "No bullet points", but the service layer had **no way to detect violations**. Compliance was entirely trust-based — probabilistic, not verifiable.

### The Solution

A new `_check_structure()` function called from `_validate_body()`:

```python
_BULLET_PATTERN = re.compile(r"^[\s]*[-•*]\s", re.MULTILINE)
_NUMBERED_PATTERN = re.compile(r"^[\s]*\d+[.)]\s", re.MULTILINE)
_MAX_BODY_LENGTH = 3000

def _check_structure(text: str) -> None:
    """Log warnings if the body violates structural expectations.
    Checks are intentionally soft — they warn, never raise."""

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if len(paragraphs) == 0:
        logger.warning("Structural check: body has 0 paragraphs.")
    elif len(paragraphs) > 5:
        logger.warning("Structural check: body has %d paragraphs (expected ≤ 5).", ...)

    if _BULLET_PATTERN.search(text):
        logger.warning("Structural check: body appears to contain bullet points.")

    if _NUMBERED_PATTERN.search(text):
        logger.warning("Structural check: body appears to contain numbered lists.")

    if len(text) > _MAX_BODY_LENGTH:
        logger.warning("Structural check: body length %d exceeds %d characters.", ...)
```

### Design Decision: Soft, Not Hard

These checks **warn, never raise**. Rationale:

| Approach | Tradeoff |
|----------|----------|
| Hard-reject | Blocks valid-but-oddly-formatted output; user sees error for no real reason |
| Soft-warn | Output still served; production monitoring can alert on repeated violations |

The correct hardening path is: **log → monitor → tune prompts → only then consider rejecting**.

### Integration Point

```python
def _validate_body(text: str) -> str:
    cleaned, count = _LEAKAGE_PATTERNS.subn("", text)
    if count:
        logger.warning(...)
    cleaned = cleaned.strip()
    _check_structure(cleaned)     # ← called after leakage stripping
    return cleaned
```

---

## 2. Leakage Pattern Expansion

### The Problem

`_LEAKAGE_PATTERNS` was written when the service only handled Office Orders. It caught `Office Order:` and `कार्यालय आदेश:` but not `Circular:`, `Policy:`, `परिपत्र:`, or `नीति:`.

### The Fix

```python
_LEAKAGE_PATTERNS = re.compile(
    r"^("
    # English headers (shared)
    r"Subject|Ref|Reference|Date|From|To|Signature"
    r"|"
    # English headers (document-type specific)
    r"Office Order|Circular|Policy"
    r"|"
    # Hindi headers (shared)
    r"विषय|संदर्भ|दिनांक|प्रेषक|प्राप्तकर्ता|हस्ताक्षर"
    r"|"
    # Hindi headers (document-type specific)
    r"कार्यालय आदेश|परिपत्र|नीति"
    r")\s*[:—–-].*$",
    re.MULTILINE | re.IGNORECASE,
)
```

Comments are now organized into **shared** vs **document-type specific** groups for clarity.

---

## 3. `_strip_markdown` — Documented Lossy Behaviour

### The Issue

```python
text = re.sub(r"\*+", "", text)  # removes ALL asterisks
```

This deletes formatting characters globally. If a policy body legitimately contained `*`, it would be stripped.

### Resolution

Not a code change — a documentation change. The docstring now explicitly warns:

```python
def _strip_markdown(text: str) -> str:
    """Remove common markdown artifacts from LLM output.

    .. warning::
        This is *destructive* sanitization — literal ``*`` and ``_`` characters
        in legitimate content will be removed.  Acceptable for government
        document bodies which should never contain these characters, but be
        aware this is lossy if the domain changes.
    """
```

This is intentional: government document bodies in this domain do not contain `*` or `_`. The tradeoff is documented, not hidden.

---

## 4. Logging Precision

### Problem: Redundant Exception Logging

```python
# Before
except Exception as e:
    logger.exception("Gemini API call failed: %s | context=%s", e, ctx)
```

`logger.exception()` already captures the full exception via `exc_info=True`. Passing `e` as a format argument **double-printed** the exception message.

### Fix

```python
# After
except Exception:
    logger.exception("Gemini API call failed.", extra={"context": ctx})
```

- `exc_info=True` is implicit in `logger.exception()` — no need to bind `e`
- `extra={"context": ctx}` makes the context a structured field on the `LogRecord`, queryable in log aggregators (CloudWatch, Datadog, ELK)

---

## 5. Type Precision

### `_generate` context type

```python
# Before
def _generate(prompt: str, *, context: dict | None = None) -> str:

# After
def _generate(prompt: str, *, context: dict[str, object] | None = None) -> str:
```

Bare `dict` provides no type information. `dict[str, object]` tells the type checker: keys are strings, values are any object.

---

## Summary of Changes

| Change | Category | Impact |
|--------|----------|--------|
| `_check_structure()` | New function | Soft structural validation — paragraphs, bullets, length |
| `_LEAKAGE_PATTERNS` expanded | Regex | Catches Circular + Policy headers (EN + HI) |
| `_strip_markdown` docstring | Documentation | Warns about lossy `*` / `_` removal |
| `logger.exception` fix | Logging | No double-printing; structured `extra=` |
| `dict[str, object]` | Type hint | Precise context type |

---

## Outcome

✅ Structural violations are now observable (logged, not hidden)  
✅ Header leakage catches all three document types in both languages  
✅ Lossy sanitization is documented, not accidental  
✅ Logging is structured and non-redundant  
✅ Type annotations are precise throughout  

