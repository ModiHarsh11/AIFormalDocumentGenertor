# 🧠 Phase 6 — Regeneration Symmetry

## The Problem with Asymmetric Flows

When generation and regeneration are implemented separately with different patterns, they behave differently in production. A guard added to generation might be missing from regeneration. A prompt hardening technique applied to generation might not be present in regeneration. A logging context used in generation might be absent in regeneration.

Asymmetry is where bugs breed.

---

## The Original Regeneration Pattern

Regeneration was ad-hoc:

```python
# views.py — old regeneration
def regenerate_office_body(request):
    regenerate_prompt = request.POST.get("regenerate_prompt", "").strip()
    previous_prompt = request.POST.get("previous_prompt", "").strip()
    previous_body = request.POST.get("previous_body", "").strip()
    lang = request.POST.get("language", "en")

    if lang == "hi":
        system_prompt = f"""
...
1. नया सुधार संकेत: {regenerate_prompt}
2. पिछला संकेत: {previous_prompt}
3. पिछला उत्पन्न मुख्य भाग: {previous_body}
...
"""
    res = gemini_model.generate_content(system_prompt)
    return HttpResponse(res.text.strip())
```

Issues:
- Inline prompt construction (same problem as Phase 5)
- User inputs directly interpolated into f-string (same injection risk as Phase 3)
- No markdown stripping
- No header leakage validation
- No empty-response guard
- No structured logging
- Different SDK usage pattern than generation
- No prompt versioning

---

## The Regeneration Path After Symmetry

The regeneration path now follows **exactly the same layers** as generation:

### Layer 1 — View (HTTP)

```python
def regenerate_office_body(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    regenerate_prompt = request.POST.get("regenerate_prompt", "").strip()
    previous_prompt = request.POST.get("previous_prompt", "").strip()
    previous_body = request.POST.get("previous_body", "").strip()
    lang = request.POST.get("language", "en")

    from .services.ai_service import regenerate_office_body as _regen_body
    body = _regen_body(
        topic=previous_prompt,
        previous_body=previous_body,
        refinement_prompt=regenerate_prompt,
        language=lang,
    )
    return HttpResponse(body)
```

### Layer 2 — Service (Transport + Validation)

```python
def regenerate_office_body(topic, previous_body, refinement_prompt, language="en") -> str:
    if not refinement_prompt or not refinement_prompt.strip():
        raise ValueError("Refinement prompt cannot be empty.")
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(...)

    full_prompt = build_regeneration_prompt(
        topic=topic,
        previous_body=previous_body,
        refinement_prompt=refinement_prompt,
        language=language,
    )

    return _generate(
        full_prompt,
        context={
            "fn": "regenerate_office_body",
            "language": language,
            "topic_length": len(topic),
            "refinement_length": len(refinement_prompt),
        },
    )
```

### Layer 3 — Prompt (Content + Versioning)

```python
REGENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "previous_body", "refinement_prompt", "today", "version"],
    template="""
[Prompt Version: {version}]

...

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
```

---

## Symmetry Comparison Table

| Capability | Generation | Regeneration |
|---|---|---|
| Input validation | ✅ `ValueError` on empty/invalid | ✅ Same |
| Prompt hardening (delimiters) | ✅ `<<<START_TOPIC>>>` | ✅ Three-block structure |
| Prompt versioning | ✅ `PROMPT_VERSION` | ✅ Same constant |
| Bilingual templates | ✅ EN + HI | ✅ EN + HI |
| Markdown stripping | ✅ `_strip_markdown()` | ✅ Same (via `_generate()`) |
| Header leakage guard | ✅ `_validate_body()` | ✅ Same (via `_generate()`) |
| Empty response guard | ✅ `if not response.candidates` | ✅ Same (via `_generate()`) |
| Post-validation empty check | ✅ `if not validated` | ✅ Same |
| Structured logging context | ✅ `{"fn": ..., "language": ..., "topic_length": ...}` | ✅ Plus `refinement_length` |
| SDK used | ✅ `google-genai` | ✅ Same |

Both paths route through `_generate()`. That single function owns all guardrails. By routing both paths through it, symmetry is structural — not just intended.

---

## The Extra Context in Regeneration Logging

Regeneration logging adds `refinement_length`:

```python
context={
    "fn": "regenerate_office_body",
    "language": language,
    "topic_length": len(topic),
    "refinement_length": len(refinement_prompt),  ← extra
}
```

This helps diagnose issues specific to regeneration: e.g., was a long refinement prompt causing unexpected model behavior?

---

## Why Today's Date Is in the Regeneration Template

```python
today = date.today().strftime("%d-%m-%Y")
```

The regeneration template includes the current date. This anchors the model to temporal context during refinement, which can affect formal phrasing ("in pursuance of the order dated..."). It is not present in the generation template because generation is based purely on topic, not temporal refinement context.

---

## Outcome

✅ Regeneration follows identical layers as generation  
✅ Same validation, same guards, same logging  
✅ Same prompt hardening (structured delimiters)  
✅ Same SDK, same `_generate()` function  
✅ Symmetry is structural — not just intended  
✅ Bugs cannot hide in an asymmetric fast path

