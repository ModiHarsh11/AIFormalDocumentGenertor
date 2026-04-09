# 🌐 HTTP Endpoints Reference

All endpoints are prefixed at the root (`/`). The app serves directly from `/`.

---

## Office Order

### `GET /`
Renders the home page with the document type selector.

**View:** `views.home`  
**Template:** `generator/home.html`  
**Context:** `designations` (keys from `DESIGNATION_MAP`), `people` (from `circular.json`)

---

### `POST /generate-body/`
AI-generates the body of an Office Order.

**View:** `views.generate_body`  
**Content-Type:** `application/x-www-form-urlencoded`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `body_prompt` | string | ✅ | The topic / subject for the body |
| `language` | `"en"` \| `"hi"` | ✅ | Output language |

**Response:** `200 OK` — plain text body string  
**Errors:** `400` if method is not POST

**Delegates to:** `ai_service.generate_office_body(topic, lang)`

---

### `POST /regenerate-body/`
Regenerates/refines a previously generated Office Order body.

**View:** `views.regenerate_office_body`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `regenerate_prompt` | string | ✅ | User's refinement instruction |
| `previous_prompt` | string | ✅ | Original topic used in generation |
| `previous_body` | string | ✅ | Previously generated body text |
| `language` | `"en"` \| `"hi"` | ✅ | Output language |

**Response:** `200 OK` — plain text refined body  
**Delegates to:** `ai_service.regenerate_office_body(topic, previous_body, refinement_prompt, lang)`

---

### `POST /result/`
Submits the Office Order form and renders the preview page.

**View:** `views.result_office_order`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `language` | `"en"` \| `"hi"` | ✅ | Document language |
| `date` | `YYYY-MM-DD` | ❌ | Document date (defaults to today) |
| `reference` | string | ❌ | Reference number |
| `body_prompt` | string | ✅ | Original topic |
| `body` | string | ✅ | Final body text |
| `from_position` | string | ✅ | Issuing designation key |
| `to_recipients[]` | string[] | ✅ | List of receiving designation keys |

**Saves to:** `request.session["doc_data"]`  
**Template:** `generator/result_office_order.html`

---

### `POST /update-body/`
Updates the body stored in the session (called when user edits body in preview).

| Parameter | Type | Description |
|---|---|---|
| `body` | string | Updated body text |

**Response:** `{"status": "success"}` or `{"status": "error"}`

---

### `GET /download/pdf/`
Generates and downloads the Office Order as PDF.

**View:** `views.download_pdf`  
**Reads from:** `request.session["doc_data"]`  
**Content-Type:** `application/pdf`  
**Filename:** `OfficeOrder.pdf`

---

### `GET /download/docx/`
Generates and downloads the Office Order as DOCX.

**View:** `views.download_docx`  
**Reads from:** `request.session["doc_data"]`  
**Content-Type:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`  
**Filename:** `OfficeOrder.docx`

---

## Circular

| Endpoint | Method | View | Description |
|---|---|---|---|
| `/circular/generate-body/` | POST | `generate_circular_body` | AI-generate circular body |
| `/circular/regenerate-body/` | POST | `regenerate_circular_body` | Refine circular body |
| `/circular/update-body/` | POST | `update_circular_body` | Update session body |
| `/circular/result/` | POST | `result_circular` | Preview circular |
| `/circular/pdf/` | GET | `download_circular_pdf` | Download circular PDF |
| `/circular/docx/` | GET | `download_circular_docx` | Download circular DOCX |

**Session key:** `circular_data`

---

## Policy

| Endpoint | Method | View | Description |
|---|---|---|---|
| `/policy/generate-body/` | POST | `generate_policy_body` | AI-generate policy body |
| `/policy/regenerate-body/` | POST | `regenerate_policy_body` | Refine policy body |
| `/policy/update-body/` | POST | `update_policy_body` | Update session body |
| `/policy/result/` | POST | `result_policy` | Preview policy |
| `/policy/pdf/` | GET | `download_policy_pdf` | Download policy PDF |
| `/policy/docx/` | GET | `download_policy_docx` | Download policy DOCX |

---

## Error Handling

All AI endpoints return `HttpResponse` with the generated text on success.  
On service-layer failure, a `RuntimeError` is raised and should be caught at the view level.

| Scenario | Behavior |
|---|---|
| Method not POST | `JsonResponse({"error": "Invalid request"}, status=400)` |
| Empty topic | `ValueError` from service layer |
| Invalid language | `ValueError` from service layer |
| Gemini API failure | `RuntimeError("AI generation failed. Please try again.")` |
| Empty response after validation | `RuntimeError("AI returned invalid or empty body after validation.")` |
| Safety filter block | `RuntimeError("AI returned empty response (possibly blocked by safety filters.")` |

