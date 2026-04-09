# 🎨 Frontend UX Features — Reference Guide

This guide documents all client-side UX features available in the document generator UI.

---

## 1. 🌐 Default Language Selection

All three document forms (Office Order, Circular, Policy) automatically pre-select **English** on page load. No manual selection is needed unless the user wants Hindi.

**Where:** `home.html` — all three `<select name="language">` elements  
**How:** `<option value="en" selected>English</option>`

---

## 2. 📅 Auto Date Fill

All `input[type="date"]` fields across all forms are automatically set to **today's date** when the page loads.

- The user can still change the date manually
- If a field already has a value, it is not overwritten
- Handled via `DOMContentLoaded` event

---

## 3. 📊 Live Word / Character Counter

Every **body prompt** and **body** textarea shows a live counter below it:

```
12 words · 84 chars
```

**Colour indicators:**

| Range | Colour | Meaning |
|-------|--------|---------|
| 0–999 chars | Grey | Normal |
| 1000–1499 chars | 🟠 Orange | Getting long |
| 1500+ chars | 🔴 Red | Very long — may affect AI quality |

The counter also auto-updates when body text is **restored from localStorage**.

---

## 4. ⏳ Loading Spinner on AI Generate

When the **🤖 Generate Body with AI** button is clicked:

- A circular CSS spinner appears inside the button
- The button label text is hidden
- The button is **disabled** to prevent duplicate API calls
- Once the response arrives (or errors), the button returns to normal

This applies to all three forms independently via IDs: `office_gen_btn`, `circular_gen_btn`, `policy_gen_btn`.

---

## 5. ✔ Select All / Deselect All Recipients

Each "To / Recipients" section has two small buttons above the checkbox list:

| Button | Action |
|--------|--------|
| **✔ Select All** | Checks all recipient checkboxes in that form |
| **✘ Deselect All** | Unchecks all recipient checkboxes in that form |

A **toast notification** confirms the action.

Available in all three forms: Office Order, Circular, Policy.

---

## 6. 🔔 Toast Notifications

Non-blocking bottom-centre pop-up messages replace browser `alert()` dialogs throughout the form page.

**Triggered by:**
- Select All / Deselect All actions
- Successful AI body generation
- Validation warnings (empty prompt, missing language)
- Errors during AI generation fetch

Toast auto-dismisses after 2 seconds. Does not block user interaction.

---

## 7. 💾 localStorage Form Persistence

Form data is automatically saved to the browser's `localStorage` as the user types. If the page is accidentally refreshed or navigated away from, data is restored on the next load.

**Fields persisted:**

| localStorage Key | Field |
|-----------------|-------|
| `form_office_body_prompt` | Office Order — AI prompt |
| `form_office_body` | Office Order — body text |
| `form_circular_body_prompt` | Circular — AI prompt |
| `form_circular_body` | Circular — body text |
| `form_policy_body_prompt` | Policy — AI prompt |
| `form_policy_body` | Policy — body text |

**Cleared automatically** when the form is submitted successfully, so old content doesn't appear on the next fresh document.

> **Note:** Checkboxes, dropdowns (language, from/to), dates, and reference fields are **not** persisted — only the long-text fields where re-typing would be most painful.

---

## 8. 📋 Copy Body Button (Result Pages)

Available on all three result pages: Office Order, Circular, Policy.

- Copies the **currently active body** (original or regenerated version) to the clipboard
- Button label changes to **✅ Copied!** for 2 seconds as visual confirmation
- Uses the modern `navigator.clipboard.writeText()` API

---

## 9. 🖨️ Print Button (Result Pages)

Available on all three result pages.

- Triggers `window.print()` directly
- Works with the existing `@media print` CSS already embedded in each result template
- Print output is clean: no buttons, no regenerate section, no version toggles, white background

---

## 10. 🔄 Version Toggle (Existing Feature — Reference)

After regenerating a body, a toggle bar appears:

| Button | Shows |
|--------|-------|
| **✓ Original / मूल** | The first AI-generated body |
| **✨ Regenerated / पुनर्जनित** | The refined/regenerated body |

Switching versions also silently updates the session (`update_*_body` endpoint) so that PDF/DOCX downloads always use the currently selected version.

---

## Keyboard & Accessibility Notes

- All form fields have visible `<label>` elements
- Buttons use descriptive emoji + text labels
- Toast notifications are purely visual (not announced to screen readers — future improvement)
- The spinner inside the generate button is CSS-only and does not affect tab order

---

---

## 11. 🏷️ Collapsible Selection Badges

**From (Position):** A green `✔ Director General` style badge appears in the header of the From collapsible after a position is selected — visible even when the section is collapsed.

**To (Recipients):** A green `✔ 5 selected` badge updates live in the To header whenever checkboxes are toggled, or Select All / Deselect All is used.

---

## 12. ⛔ Client-Side Form Validation

Clicking **Preview →** now validates before submitting:

| Check | Error shown |
|-------|------------|
| From position not selected | `⚠ Please select a From position.` below From section |
| No recipients checked | `⚠ Please select at least one recipient.` below To section |

When validation fails:
- The relevant collapsed sections **auto-open** so the user sees the problem immediately
- A toast notification summarises: `⚠️ Please fix the errors above before submitting.`
- The form is **not submitted**

---

## 13. 🗑 Clear Form Button

Each form has a **🗑 Clear Form** button in the top-right of its heading.

On click (after confirmation):
- All text inputs (prompt, body, subject) cleared
- From position reset; its badge hidden
- All To checkboxes unchecked; count badge hidden
- Date reset to today
- All localStorage data for that form cleared
- Char counters reset to `0 words · 0 chars`

---

## 14. 📅 Auto-Year Reference Number

The Office Order reference field auto-fills with the **current calendar year** on load:
```
BISAG-N/Office Order/2026/   ← auto, not hardcoded
```
Also updates correctly when language is toggled. No annual code changes needed.

---

## 15. 🔁 Last Active Tab Memory

When navigating back to the home page (e.g., after viewing a result), the **last used document type tab** (Office Order / Circular / Policy) is automatically re-opened. Stored in `localStorage` key `last_active_tab`.

---

## 16. 📄 PDF Upload Validation (Policy Form)

Before the Policy form submits, the attached PDF is validated:

| Check | Feedback |
|-------|---------|
| File is not a PDF | ❌ Red message; file input cleared |
| File exceeds 10 MB | ❌ Red message with actual size; file input cleared |
| Valid file | ✅ Green message with filename and size |

---

## Browser Compatibility
|---------|--------|---------|------|--------|
| `navigator.clipboard` | ✅ | ✅ | ✅ | ✅ (HTTPS only) |
| CSS spinner animation | ✅ | ✅ | ✅ | ✅ |
| `localStorage` | ✅ | ✅ | ✅ | ✅ |
| `input[type="date"]` auto-fill | ✅ | ✅ | ✅ | ✅ |
| `pointer-events: none` | ✅ | ✅ | ✅ | ✅ |

