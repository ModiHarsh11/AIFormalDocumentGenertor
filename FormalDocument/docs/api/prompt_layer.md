# 📝 Prompt Layer Reference

**Files:**
- `generator/prompts/office_order.py`
- `generator/prompts/circular.py`
- `generator/prompts/policy.py`

The prompt layer owns all prompt wording, language logic, and versioning. The service layer calls it but never reads or modifies prompt strings directly. All three files share an identical structure — they differ only in template content and `PROMPT_VERSION` value.

---

## Prompt Version

```python
# office_order.py
PROMPT_VERSION = "OfficeOrder_v1"

# circular.py
PROMPT_VERSION = "Circular_v1"

# policy.py
PROMPT_VERSION = "Circular_v1"

# Same structure as office_order.py:
# Language, _validate_language, _select_template, build_generation_prompt, build_regeneration_prompt
```

This version string is **embedded inside every prompt** sent to Gemini.
Purpose: Traceability — log outputs can be correlated with the exact prompt version that produced them, enabling A/B testing and regression tracking.

The service layer imports these via `PROMPT_VERSION_REGISTRY` and logs them in every API call context.

---

## Supported Languages

```python
SUPPORTED_LANGUAGES = ("en", "hi")
Language = Literal["en", "hi"]
```

Language is validated in the prompt layer (not just the service layer) as a defence-in-depth check via `_validate_language()`. The `Language` type alias provides IDE auto-complete and static-analysis safety. If an unsupported language reaches this layer, a `ValueError` is raised with the invalid value and the allowed set.

---

## Generation Templates

### `GENERATION_TEMPLATE_EN` — English Office Order Body

```
[Prompt Version: {version}]

You are drafting the BODY of an official government Office Order for BISAG-N.

Rules:
- Write one formal paragraph (minimum 2–3 sentences).
- Use official government tone.
- The response must read like an officially issued administrative document.
- Do not include title, reference, date, From or To.
- No bullet points or numbering.
- Plain text only.

<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
```

### `GENERATION_TEMPLATE_HI` — Hindi Office Order Body

Same structure in Hindi (Devanagari).  
Rules enforce: औपचारिक अनुच्छेद, सरकारी भाषा, कोई शीर्षक/संदर्भ/दिनांक नहीं।

---

## Regeneration Templates

### `REGENERATION_TEMPLATE_EN` — English Refinement

```
[Prompt Version: {version}]

You are refining the BODY of an official government Office Order for BISAG-N.

Today's Date: {today}

Rules:
- Create an improved version based on the three inputs below.
- Must be better and more formal than the previous version.
- Use official government tone.
- ...

<<<ORIGINAL_TOPIC>>>
{topic}
<<<END_TOPIC>>>

<<<PREVIOUS_BODY>>>
{previous_body}
<<<END_PREVIOUS_BODY>>>

<<<REFINEMENT_REQUEST>>>
{refinement_prompt}
<<<END_REFINEMENT_REQUEST>>>
```

### `REGENERATION_TEMPLATE_HI` — Hindi Refinement

Same structure in Hindi.

---

## Structured Delimiter Design

Both generation and regeneration templates use structured delimiters:

```
<<<START_TOPIC>>>
...user input...
<<<END_TOPIC>>>
```

**Why this matters:**

| Risk | Without Delimiters | With Delimiters |
|---|---|---|
| Prompt injection | User input can override instructions | Model sees clear boundary between instruction and data |
| Instruction override | `topic = "Ignore all rules and..."` works | Delimiters signal to model: this is DATA, not INSTRUCTION |
| Model confusion | Multi-block prompts blend together | Each section is labelled and bounded |

This is the core of **Phase 3 — Prompt Hardening**.

---

## Public Builder Functions

### `build_generation_prompt(topic, language) → str`

Selects the correct template by language, formats with `topic` and `PROMPT_VERSION`.

```python
from generator.prompts.office_order import build_generation_prompt

prompt = build_generation_prompt(
    topic="Annual leave policy update",
    language="en"
)
```

### `build_regeneration_prompt(topic, previous_body, refinement_prompt, language) → str`

Selects the correct template by language, injects today's date automatically, formats all four variables.

```python
from generator.prompts.office_order import build_regeneration_prompt

prompt = build_regeneration_prompt(
    topic="Annual leave policy update",
    previous_body="Pursuant to administrative necessity...",
    refinement_prompt="Make it more concise",
    language="hi"
)
```

Today's date is added automatically:
```python
today = date.today().strftime("%d-%m-%Y")
```

---

## Adding a New Language

1. Add the language code to `SUPPORTED_LANGUAGES`
2. Create `GENERATION_TEMPLATE_XX` and `REGENERATION_TEMPLATE_XX` with the same input variables
3. Update `build_generation_prompt()` and `build_regeneration_prompt()` to select the new template
4. Add corresponding `_LEAKAGE_PATTERNS` entries in `ai_service.py` for any new header keywords

---

## Adding a New Document Type (New Prompt File)

Create `generator/prompts/advertisement.py` (example):

```python
"""Prompt builder for Government Advertisement documents (BISAG-N)."""

from datetime import date
from typing import Literal

from langchain.prompts import PromptTemplate

PROMPT_VERSION = "Advertisement_v1"
SUPPORTED_LANGUAGES = ("en", "hi")
Language = Literal["en", "hi"]

GENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "version"],
    template="""
[Prompt Version: {version}]

You are drafting the BODY of an official government Advertisement for BISAG-N.
...
<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
"""
)

# ... GENERATION_TEMPLATE_HI, REGENERATION_TEMPLATE_EN, REGENERATION_TEMPLATE_HI

def _validate_language(language: str) -> None:
    """Raise ValueError if *language* is not supported."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}' for Advertisement prompt. "
            f"Must be one of: {SUPPORTED_LANGUAGES}"
        )

def _select_template(en_template, hi_template, language):
    """Return the correct template for *language*."""
    return hi_template if language == "hi" else en_template

def build_generation_prompt(topic: str, language: Language = "en") -> str:
    """Return a formatted generation prompt for an Advertisement body."""
    _validate_language(language)
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("topic cannot be empty.")
    template = _select_template(GENERATION_TEMPLATE_EN, GENERATION_TEMPLATE_HI, language)
    return template.format(topic=topic, version=PROMPT_VERSION)

def build_regeneration_prompt(
        topic, previous_body, refinement_prompt, language: Language = "en"
) -> str:
    """Return a formatted regeneration prompt for an Advertisement body."""
    _validate_language(language)
    # validate + strip all three inputs, then format template
    ...
```

Keep each document type in its own prompt file. Never mix prompt content across files.

Then register in `ai_service.py`:
1. Import builders + `PROMPT_VERSION`
2. Add `"advertisement"` to `DocumentType` Literal
3. Add entry to `DOCUMENT_PROMPT_REGISTRY` and `PROMPT_VERSION_REGISTRY`

---

## Versioning Strategy

When you update a prompt's wording:

1. Increment `PROMPT_VERSION` (e.g., `"OfficeOrder_v2"`)
2. The new version string is embedded in every subsequent API call
3. Log entries will show which version produced which output
4. Old version can be kept as a constant for reference/rollback

