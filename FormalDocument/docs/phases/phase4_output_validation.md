# 🧠 Phase 4 — Output Validation Layer

## The Core Principle

LLMs are probabilistic systems. Production systems must be deterministic.

A model can follow instructions 95% of the time. The remaining 5% is where production bugs live. The validation layer exists to intercept and correct that 5%.

---

## What Was Added

### 1. Markdown Stripping

```python
def _strip_markdown(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)           # code blocks
    text = re.sub(r"\*+", "", text)                       # bold / italic asterisks
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text) # _italic_
    text = re.sub(r"^[-•]\s*", "", text, flags=re.MULTILINE) # bullet lists
    text = re.sub(r"^\d+\.\s*", "", text, flags=re.MULTILINE) # numbered lists
    text = re.sub(r"#+\s*", "", text)                     # headings
    text = re.sub(r" {2,}", " ", text)                    # double spaces
    return text.strip()
```

**Why:** Models trained on markdown-heavy data will often format output with bold text, bullet points, or headings — even when told not to. This is a probabilistic behavior. Every generated body passes through this function before it reaches the user.

---

### 2. Header Leakage Stripping

```python
_LEAKAGE_PATTERNS = re.compile(
    r"^("
    # English headers
    r"Subject|Ref|Reference|Date|From|To|Signature|Office Order"
    r"|"
    # Hindi headers
    r"विषय|संदर्भ|दिनांक|प्रेषक|प्राप्तकर्ता|कार्यालय आदेश|हस्ताक्षर"
    r")\s*[:—–-].*$",
    re.MULTILINE | re.IGNORECASE,
)
```

The prompt explicitly tells the model not to include headers. Sometimes it does anyway.

**Detected and removed — English:**
- `Subject: ...`
- `Reference: ...` / `Ref: ...`
- `Date: ...`
- `From: ...`
- `To: ...`
- `Signature: ...`
- `Office Order: ...`

**Detected and removed — Hindi:**
- `विषय: ...` (Subject)
- `संदर्भ: ...` (Reference)
- `दिनांक: ...` (Date)
- `प्रेषक: ...` (From)
- `प्राप्तकर्ता: ...` (To)
- `कार्यालय आदेश: ...` (Office Order)
- `हस्ताक्षर: ...` (Signature)

---

### 3. Structured Logging Context

```python
return _generate(
    full_prompt,
    context={
        "fn": "generate_office_body",
        "language": language,
        "topic_length": len(topic)
    },
)
```

Every API call attaches a context dict. If the API call fails, the log entry includes:
- Which function was called
- What language was requested
- How long the topic was

This enables production debugging without exposing the full prompt in logs.

For regeneration:
```python
context={
    "fn": "regenerate_office_body",
    "language": language,
    "topic_length": len(topic),
    "refinement_length": len(refinement_prompt),
}
```

---

### 4. Empty-Response Guard

```python
if not response.candidates:
    raise RuntimeError(
        "AI returned empty response (possibly blocked by safety filters.)"
    )
```

Gemini's safety filters can block a response entirely, returning zero candidates. Without this guard, accessing `response.text` would raise an `AttributeError` with no meaningful error message. The guard converts this into a clear, catchable `RuntimeError`.

---

### 5. Post-Validation Empty Check

```python
validated = _validate_body(text)
if not validated:
    raise RuntimeError("AI returned invalid or empty body after validation.")
```

After stripping markdown and headers, the result could theoretically be empty (e.g., the model responded with only headers and nothing else). This guard prevents returning an empty string as a successful response.

---

## The Validation Pipeline

```
response.text
    ↓
_strip_markdown(text)          ← remove formatting artifacts
    ↓
_validate_body(text)           ← remove leaked headers (EN + HI)
    ↓
if not validated: raise        ← guard against empty result
    ↓
return clean plain text
```

---

## Logging Behavior

| Event | Log Level | Message |
|---|---|---|
| Header lines stripped | `WARNING` | `"LLM output contained N leaked header line(s) — stripped automatically."` |
| API call exception | `EXCEPTION` | Full stack trace + context dict |

---

## Outcome

✅ Markdown stripping — removes formatting artifacts  
✅ Header leakage stripping — EN + HI  
✅ Empty-response guard — handles safety filter blocks  
✅ Post-validation empty check — prevents empty success responses  
✅ Structured logging context on every API call  
✅ The system does not blindly trust the model's output

