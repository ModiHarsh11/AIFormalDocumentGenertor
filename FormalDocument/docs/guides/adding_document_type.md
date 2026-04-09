# ➕ Adding a New Document Type

This guide walks through adding a new document type end-to-end.  
Example: **Advertisement** document.

---

## Overview of Steps

1. Create the prompt file (`prompts/advertisement.py`)
2. Add service functions (`services/ai_service.py`)
3. Create JSON config (`advertisement.json`)
4. Add view functions (`views.py`)
5. Register URL patterns (`urls.py`)
6. Create HTML templates

---

## Step 1 — Create the Prompt File

**File:** `generator/prompts/advertisement.py`

```python
from datetime import date
from langchain.prompts import PromptTemplate

PROMPT_VERSION = "Advertisement_v1"
SUPPORTED_LANGUAGES = ("en", "hi")

GENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "version"],
    template="""
[Prompt Version: {version}]

You are drafting the BODY of an official government Advertisement for BISAG-N.

Rules:
- Write 2–3 formal paragraphs.
- Use official government tone.
- The response must read like an officially issued public advertisement.
- Do not include title, reference number, date, or closing signature.
- No bullet points or numbering unless listing eligibility criteria.
- Plain text only.

<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
"""
)

GENERATION_TEMPLATE_HI = PromptTemplate(
    input_variables=["topic", "version"],
    template="""
[Prompt Version: {version}]

आप BISAG-N के लिए एक आधिकारिक विज्ञापन की मुख्य सामग्री लिख रहे हैं।

नियम:
- 2–3 औपचारिक अनुच्छेद लिखें।
- सरकारी भाषा का प्रयोग करें।
- कोई शीर्षक, संदर्भ, दिनांक या हस्ताक्षर न लिखें।
- केवल सादा पाठ में उत्तर दें।

<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
"""
)

REGENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "previous_body", "refinement_prompt", "today", "version"],
    template="""
[Prompt Version: {version}]

You are refining the BODY of an official government Advertisement for BISAG-N.

Today's Date: {today}

Rules:
- Create an improved version based on the three inputs below.
- Must be better and more formal than the previous version.
- Plain text only.

<<<ORIGINAL_TOPIC>>>
{topic}
<<<END_TOPIC>>>

<<<PREVIOUS_BODY>>>
{previous_body}
<<<END_PREVIOUS_BODY>>>

<<<REFINEMENT_REQUEST>>>
{refinement_prompt}
<<<END_REFINEMENT_REQUEST>>>
"""
)

REGENERATION_TEMPLATE_HI = PromptTemplate(
    input_variables=["topic", "previous_body", "refinement_prompt", "today", "version"],
    template="""
[Prompt Version: {version}]

आप BISAG-N के लिए एक आधिकारिक विज्ञापन की मुख्य सामग्री को परिष्कृत कर रहे हैं।

आज की तारीख: {today}

नियम:
- तीनों इनपुट के आधार पर एक बेहतर संस्करण बनाएं।
- केवल सादा पाठ में उत्तर दें।

<<<ORIGINAL_TOPIC>>>
{topic}
<<<END_TOPIC>>>

<<<PREVIOUS_BODY>>>
{previous_body}
<<<END_PREVIOUS_BODY>>>

<<<REFINEMENT_REQUEST>>>
{refinement_prompt}
<<<END_REFINEMENT_REQUEST>>>
"""
)


def build_generation_prompt(topic: str, language: str) -> str:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError("Unsupported language for Advertisement prompt.")
    template = GENERATION_TEMPLATE_HI if language == "hi" else GENERATION_TEMPLATE_EN
    return template.format(topic=topic, version=PROMPT_VERSION)


def build_regeneration_prompt(
    topic: str,
    previous_body: str,
    refinement_prompt: str,
    language: str,
) -> str:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError("Unsupported language for Advertisement prompt.")
    today = date.today().strftime("%d-%m-%Y")
    template = REGENERATION_TEMPLATE_HI if language == "hi" else REGENERATION_TEMPLATE_EN
    return template.format(
        topic=topic,
        previous_body=previous_body,
        refinement_prompt=refinement_prompt,
        today=today,
        version=PROMPT_VERSION,
    )
```

---

## Step 2 — Register in Service Layer

**File:** `generator/services/ai_service.py`

Add imports at the top:
```python
from generator.prompts.advertisement import (
    build_generation_prompt as build_advertisement_generation_prompt,
    build_regeneration_prompt as build_advertisement_regeneration_prompt,
    PROMPT_VERSION as ADVERTISEMENT_PROMPT_VERSION,
)
```

Update the `DocumentType` Literal:
```python
DocumentType = Literal["office", "circular", "policy", "advertisement"]
```

Add to the registries:
```python
DOCUMENT_PROMPT_REGISTRY["advertisement"] = {
    "generate": build_advertisement_generation_prompt,
    "regenerate": build_advertisement_regeneration_prompt,
}
PROMPT_VERSION_REGISTRY["advertisement"] = ADVERTISEMENT_PROMPT_VERSION
```

Update `_LEAKAGE_PATTERNS` regex to include `Advertisement` and its Hindi equivalent (e.g., `विज्ञापन`).

(Optional) Add backward-compatibility wrappers if views need them:
```python
def generate_advertisement_body(topic: str, language: Language = "en") -> str:
    """Compat wrapper → generate_body('advertisement', ...)."""
    return generate_body("advertisement", topic, language)

def regenerate_advertisement_body(
    topic: str,
    previous_body: str,
    refinement_prompt: str,
    language: Language = "en",
) -> str:
    """Compat wrapper → regenerate_body('advertisement', ...)."""
    return regenerate_body("advertisement", topic, previous_body, refinement_prompt, language)
```

**Zero new service logic.** The registry handles routing. `generate_body()` and `regenerate_body()` work for all document types.

---

## Step 3 — Create JSON Config

**File:** `ai_formal_generator/advertisement.json`

```json
{
  "header": {
    "en": {
      "org_name": "BISAG-N",
      "ministry": "Department of Space",
      "government": "Government of India"
    },
    "hi": {
      "org_name": "बायसेग-एन",
      "ministry": "अंतरिक्ष विभाग",
      "government": "भारत सरकार"
    }
  },
  "title_en": "Advertisement",
  "title_hi": "विज्ञापन"
}
```

---

## Step 4 — Add View Functions

**File:** `generator/views.py`

Load JSON at top (with other JSON loads):
```python
with open(os.path.join(BASE_DIR, "advertisement.json"), encoding="utf-8") as f:
    ADVERTISEMENT = json.load(f)
```

Add view functions:
```python
def generate_advertisement_body_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)
    prompt = request.POST.get("body_prompt", "").strip()
    lang = request.POST.get("language", "en")
    from .services.ai_service import generate_advertisement_body
    body = generate_advertisement_body(prompt, lang)
    return HttpResponse(body)


def regenerate_advertisement_body_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)
    from .services.ai_service import regenerate_advertisement_body
    body = regenerate_advertisement_body(
        topic=request.POST.get("previous_prompt", "").strip(),
        previous_body=request.POST.get("previous_body", "").strip(),
        refinement_prompt=request.POST.get("regenerate_prompt", "").strip(),
        language=request.POST.get("language", "en"),
    )
    return HttpResponse(body)
```

---

## Step 5 — Register URL Patterns

**File:** `generator/urls.py`

```python
# ADVERTISEMENT
path("advertisement/generate-body/", views.generate_advertisement_body_view, name="generate_advertisement_body"),
path("advertisement/regenerate-body/", views.regenerate_advertisement_body_view, name="regenerate_advertisement_body"),
path("advertisement/result/", views.result_advertisement, name="result_advertisement"),
path("advertisement/pdf/", views.download_advertisement_pdf, name="download_advertisement_pdf"),
path("advertisement/docx/", views.download_advertisement_docx, name="download_advertisement_docx"),
```

---

## Step 6 — Create HTML Templates

Create in `generator/templates/generator/`:
- `advertisement_form.html` — form with topic input, language selector, generate button
- `result_advertisement.html` — preview with regenerate support and download buttons
- `pdf_advertisement.html` — WeasyPrint PDF template

Follow the same pattern as `office_order_form.html` and `result_office_order.html`.

---

## Checklist

- [ ] `prompts/advertisement.py` — both templates, both languages, both builder functions, `Language` type alias, `_validate_language`, `_select_template`, input validation
- [ ] `services/ai_service.py` — import builders + `PROMPT_VERSION`, update `DocumentType` Literal, add to `DOCUMENT_PROMPT_REGISTRY` + `PROMPT_VERSION_REGISTRY`, update `_LEAKAGE_PATTERNS`
- [ ] `advertisement.json` — header strings
- [ ] `views.py` — JSON load, view functions (generate, regenerate, result, update, download)
- [ ] `urls.py` — all URL patterns registered
- [ ] Templates — form, result, pdf
- [ ] Home page updated to include Advertisement option

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Prompt file | `prompts/{doc_type}.py` | `prompts/advertisement.py` |
| Prompt version | `"DocType_v1"` | `"Advertisement_v1"` |
| Registry key | `DocumentType` Literal value | `"advertisement"` |
| Compat wrapper (optional) | `generate_{doc_type}_body`, `regenerate_{doc_type}_body` | `generate_advertisement_body` |
| JSON config | `{doc_type}.json` | `advertisement.json` |
| Session key | `{doc_type}_data` | `advertisement_data` |
| URL prefix | `/{doc_type}/` | `/advertisement/` |
| Template dir | `templates/generator/` | same for all |

