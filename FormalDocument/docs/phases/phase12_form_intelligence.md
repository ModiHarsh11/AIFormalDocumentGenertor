# ✨ Phase 12 — Form Intelligence & Validation

## What This Phase Covers

1. **Selected value badge on From collapsibles** — shows which position is chosen without reopening
2. **Recipient count badge on To collapsibles** — shows how many recipients are selected
3. **Client-side form validation** — blocks submit if From is empty or no To recipients selected; auto-opens the offending section
4. **Clear Form button** — one-click reset of all fields in each form
5. **Auto-year in reference number** — Office Order reference auto-uses current calendar year, never hardcoded
6. **Last active tab memory** — returns to the same document type tab after navigating back from result
7. **Subject field localStorage persistence** — Circular and Policy subject fields now also saved on reload
8. **PDF upload validation** — file type and size (max 10 MB) checked before form submission

---

## 1. Selected Value Badge on From Collapsibles

### Problem
After selecting a "From" position inside the collapsible dropdown and closing it, there was no visible indicator of what was selected. Users had to reopen it just to confirm.

### Solution
A green badge appears in the collapsible header immediately after a selection is made.

```html
<span>From (Position) / से (पद)
  <span id="office_from_badge" class="collapsible-selected" style="display:none;"></span>
</span>
```

```js
function updateBadge(selectId, badgeId) {
    const sel = document.getElementById(selectId);
    const badge = document.getElementById(badgeId);
    if (sel.value) {
        badge.textContent = '✔ ' + sel.options[sel.selectedIndex].text;
        badge.style.display = 'inline';
    } else {
        badge.style.display = 'none';
    }
}
```

Called via `onchange="updateBadge('office_from_select','office_from_badge')"` on each From `<select>`.

---

## 2. Recipient Count Badge on To Collapsibles

### Problem
Same issue — no feedback on how many recipients were checked inside the collapsed To section.

### Solution
A green badge showing `✔ N selected` updates whenever any checkbox is toggled, or Select All / Deselect All is used.

```js
function updateCheckCount(sectionId, badgeId) {
    const count = document.querySelectorAll(
        `#${sectionId} input[type="checkbox"]:checked`
    ).length;
    const badge = document.getElementById(badgeId);
    if (count > 0) {
        badge.textContent = `✔ ${count} selected`;
        badge.style.display = 'inline';
    } else {
        badge.style.display = 'none';
    }
}
```

`selectAll()` and `deselectAll()` were also updated to accept and pass `badgeId`.

---

## 3. Client-Side Form Validation

### Problem
If a user clicked "Preview →" without selecting a From position or any To recipients, the form submitted and the backend either crashed or produced a broken document.

### Solution
Each form's `<form>` element now has `onsubmit="return validateForm('office')"` (or `'circular'` / `'policy'`).

```js
function validateForm(type) {
    let valid = true;

    // Check From dropdown is selected
    const fromEl = document.getElementById(`${type}_from_select`);
    if (fromEl && !fromEl.value) {
        document.getElementById(`${type}_from_err`).style.display = 'block';
        // Auto-open the collapsible so user sees the error
        ...
        valid = false;
    }

    // Check at least one To checkbox
    const toChecked = document.querySelectorAll(
        `#${type}_to_content input[type="checkbox"]:checked`
    ).length;
    if (toChecked === 0) {
        document.getElementById(`${type}_to_err`).style.display = 'block';
        valid = false;
    }

    if (!valid) showToast('⚠️ Please fix the errors above before submitting.');
    return valid;
}
```

**Validation messages** appear below each collapsible section:
```html
<div class="validation-msg" id="office_from_err">⚠ Please select a From position.</div>
<div class="validation-msg" id="office_to_err">⚠ Please select at least one recipient.</div>
```

When validation fails, the relevant collapsed sections are **automatically opened** so the user immediately sees what needs to be filled.

---

## 4. Clear Form Button

### Problem
Once the AI generated body text, there was no way to reset the form cleanly. Users had to manually delete each field.

### Solution

A **🗑 Clear Form** button appears in the top-right of each form header:

```html
<h5 ...>
    Office Order Form
    <button type="button" class="btn-clear-form" onclick="clearForm('office')">🗑 Clear Form</button>
</h5>
```

`clearForm(type)` does the following on confirmation:
- Clears all text fields (body prompt, body, subject)
- Resets char counters to `0 words · 0 chars`
- Resets From select dropdown + clears its badge
- Unchecks all To checkboxes + clears count badge
- Resets date field to today
- Removes all associated localStorage keys

---

## 5. Auto-Year in Reference Number

### Problem
The Office Order reference was hardcoded as `"BISAG-N/Office Order/2026/"` — every new year this would be wrong without a manual fix.

### Solution

On `DOMContentLoaded`, the year is injected dynamically:

```js
const currentYear = new Date().getFullYear();
const refField = document.getElementById('office_reference');
if (refField) {
    refField.value = refField.value.replace(/\d{4}/, currentYear);
}
```

`updateOfficeRef()` (called on language toggle) also uses `new Date().getFullYear()`:

```js
function updateOfficeRef() {
    const lang = document.getElementById('office_language').value;
    const year = new Date().getFullYear();
    refField.value = lang === 'hi'
        ? `बायसेग-एन/कार्यालय आदेश/${year}/`
        : `BISAG-N/Office Order/${year}/`;
}
```

No code changes needed next year — works automatically.

---

## 6. Last Active Tab Memory

### Problem
After viewing a result and clicking "← Back to Home", the page always loaded with no form visible. The user had to click their document type again to re-open the form.

### Solution

`selectDocType()` now saves the active type to `localStorage`:

```js
localStorage.setItem('last_active_tab', type);
```

On `DOMContentLoaded`, it restores it:

```js
const lastTab = localStorage.getItem('last_active_tab');
if (lastTab) {
    document.querySelector(`.doc-type-btn[data-type="${lastTab}"]`).classList.add('active');
    document.getElementById(lastTab + 'Form').classList.add('active');
}
```

Also added `data-type` attributes to each `.doc-type-btn` so they can be targeted:

```html
<div class="doc-type-btn" data-type="office" onclick="selectDocType('office')">
```

---

## 7. Subject Field localStorage Persistence

### Problem
Previously only the 6 body text areas were persisted in localStorage. The **Circular subject** and **Policy subject** inputs were not saved — they would be blank after a refresh.

### Solution

Added `id` attributes and `oninput="saveFormData()"` to both subject fields:

```html
<!-- Circular -->
<input type="text" name="subject" id="circular_subject" ... oninput="saveFormData()" required>

<!-- Policy -->
<input type="text" name="subject" id="policy_subject" ... oninput="saveFormData()" required>
```

Added to `LS_FIELDS`:

```js
const LS_FIELDS = [
    'office_body_prompt', 'office_body',
    'circular_body_prompt', 'circular_body', 'circular_subject',
    'policy_body_prompt', 'policy_body', 'policy_subject'
];
```

---

## 8. PDF Upload Validation

### Problem
The Policy form accepted any file without frontend checks. A user could accidentally upload a non-PDF or a 50 MB file, wasting time waiting for a server-side failure.

### Solution

Added `onchange="validatePdfUpload(this)"` to the file input:

```js
function validatePdfUpload(input) {
    const msgEl = document.getElementById('pdf_upload_msg');
    const file = input.files[0];
    const maxSize = 10 * 1024 * 1024; // 10 MB

    if (file.type !== 'application/pdf') {
        msgEl.textContent = '❌ Only PDF files are allowed.';
        msgEl.style.color = '#dc3545';
        input.value = '';          // clear the input
        return false;
    }
    if (file.size > maxSize) {
        msgEl.textContent = `❌ File too large (${(file.size/1024/1024).toFixed(1)} MB). Max is 10 MB.`;
        msgEl.style.color = '#dc3545';
        input.value = '';
        return false;
    }
    // Success
    msgEl.textContent = `✅ ${file.name} (${(file.size/1024/1024).toFixed(2)} MB)`;
    msgEl.style.color = '#28a745';
    return true;
}
```

**Feedback shown:**
- ✅ Green — valid file with name and size
- ❌ Red — invalid type or too large; input is cleared

---

## Files Changed

| File | Changes |
|------|---------|
| `templates/generator/home.html` | From badge, To count badge, form validation, clear form button, auto-year ref, last-tab memory, subject localStorage, PDF validation |

---

## Summary

All changes are **pure frontend** — zero backend modifications. These improvements close the gap between the form and the user, making it impossible to accidentally submit an incomplete document.

