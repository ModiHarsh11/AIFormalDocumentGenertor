# ✨ Phase 11 — UX Enhancements & New Features

## What This Phase Covers

1. **English as default language** — all three forms pre-select English on load
2. **Auto-set today's date** — all date fields auto-fill with current date on page load
3. **Disable Purchase Order button** — fully blocked with `pointer-events: none`
4. **Live word/char counter** — real-time feedback on all body prompt & body textareas
5. **Loading spinner on AI Generate** — visual feedback while AI is working
6. **Select All / Deselect All** — batch recipient selection in all three forms
7. **Toast notifications** — non-blocking user feedback replacing `alert()`
8. **localStorage form persistence** — prevent data loss on accidental reload
9. **Copy Body button** — one-click clipboard copy on all result pages
10. **Print button** — direct print trigger on all result pages

---

## 1. English as Default Language

### Problem
The Policy form had a blank `-- Select Language --` placeholder as the default option, while Office Order and Circular already pre-selected English. This was inconsistent and required an extra click for every Policy document.

### Fix

**File:** `templates/generator/home.html`

```html
<!-- Before -->
<select name="language" id="policy_language" class="form-select" required>
    <option value="">-- Select Language --</option>
    <option value="en">English</option>
    <option value="hi">हिंदी (Hindi)</option>
</select>

<!-- After -->
<select name="language" id="policy_language" class="form-select" required>
    <option value="en" selected>English</option>
    <option value="hi">हिंदी (Hindi)</option>
</select>
```

All three forms (Office Order, Circular, Policy) now consistently pre-select **English**.

---

## 2. Auto-Set Today's Date

### Problem
All date input fields were empty on load. Users had to manually open the date picker and select today's date every single time.

### Fix

Added a `DOMContentLoaded` listener that auto-populates every `input[type="date"]` field that hasn't been filled yet.

**File:** `templates/generator/home.html`

```js
document.addEventListener('DOMContentLoaded', function () {
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(function (input) {
        if (!input.value) input.value = today;
    });
});
```

Applies to all three forms automatically. Works for future forms too — any `input[type="date"]` added later is covered.

---

## 3. Disable Purchase Order Button

### Problem
The Purchase Order button had `opacity: 0.45` and `cursor: not-allowed` but was still technically clickable via JavaScript or developer tools.

### Fix

Added `pointer-events: none` to fully block all interaction.

```html
<!-- Before -->
<div class="doc-type-btn" style="opacity:0.45;cursor:not-allowed;" title="Coming soon">

<!-- After -->
<div class="doc-type-btn" style="opacity:0.45;cursor:not-allowed;pointer-events:none;" title="Coming soon">
```

No `onclick` handler exists on this button, and now CSS also guarantees zero interaction at the browser level.

---

## 4. Live Word / Character Counter

### Problem
Users had no feedback on how long their prompt or body text was. This led to either very short (low quality) or excessively long inputs.

### Solution

Added a `<div class="char-counter">` below each textarea with live updates via `oninput`.

**HTML (example — same pattern for all 6 textareas):**
```html
<textarea ... oninput="updateCounter(this, 'office_prompt_counter')"></textarea>
<div id="office_prompt_counter" class="char-counter">0 words · 0 chars</div>
```

**JavaScript:**
```js
function updateCounter(textarea, counterId) {
    const text = textarea.value;
    const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
    const chars = text.length;
    const el = document.getElementById(counterId);
    el.textContent = `${words} words · ${chars} chars`;
    el.className = 'char-counter'
        + (chars > 1500 ? ' limit' : chars > 1000 ? ' warn' : '');
}
```

**CSS colour thresholds:**

| Chars | Colour | Class |
|-------|--------|-------|
| 0–999 | Grey (default) | `.char-counter` |
| 1000–1499 | Orange warning | `.char-counter.warn` |
| 1500+ | Red limit | `.char-counter.limit` |

**Applies to:**
- `office_body_prompt` → `office_prompt_counter`
- `office_body` → `office_body_counter`
- `circular_body_prompt` → `circular_prompt_counter`
- `circular_body` → `circular_body_counter`
- `policy_body_prompt` → `policy_prompt_counter`
- `policy_body` → `policy_body_counter`

---

## 5. Loading Spinner on AI Generate Button

### Problem
After clicking "🤖 Generate Body with AI", there was no visual indicator that a request was in progress. Users clicked the button multiple times, causing duplicate API calls.

### Solution

Each generate button now has an embedded spinner element. The `setLoading()` helper toggles the `loading` CSS class, which shows the spinner and hides the label text. The button is also `disabled` during the request.

**HTML structure:**
```html
<button type="button" class="btn btn-generate mt-2" id="office_gen_btn" onclick="generateOfficeBody()">
    <span class="spinner"></span>
    <span class="btn-label">🤖 Generate Body with AI</span>
</button>
```

**CSS:**
```css
.btn-generate .spinner {
    display: none;
    width: 14px; height: 14px;
    border: 2px solid #fff;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
    vertical-align: middle;
    margin-right: 5px;
}
.btn-generate.loading .spinner  { display: inline-block; }
.btn-generate.loading .btn-label { display: none; }
@keyframes spin { to { transform: rotate(360deg); } }
```

**JavaScript:**
```js
function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    btn.disabled = loading;
    btn.classList.toggle('loading', loading);
}
```

Called as `setLoading('office_gen_btn', true)` before fetch, and `setLoading('office_gen_btn', false)` in `.finally()`.

---

## 6. Select All / Deselect All for Recipients

### Problem
The "To" (recipients) sections contain 18+ checkboxes. Selecting all relevant designations required many individual clicks.

### Solution

Added a small button bar above each checkbox list:

```html
<div class="select-all-bar">
    <button type="button" class="btn-sel" onclick="selectAll('office_to_content')">✔ Select All</button>
    <button type="button" class="btn-sel" onclick="deselectAll('office_to_content')">✘ Deselect All</button>
</div>
```

**JavaScript:**
```js
function selectAll(sectionId) {
    document.querySelectorAll(`#${sectionId} input[type="checkbox"]`).forEach(cb => cb.checked = true);
    showToast('All recipients selected ✔');
}
function deselectAll(sectionId) {
    document.querySelectorAll(`#${sectionId} input[type="checkbox"]`).forEach(cb => cb.checked = false);
    showToast('All recipients deselected ✘');
}
```

Added to sections: `office_to_content`, `circular_to_content`, `policy_to_content`.

---

## 7. Toast Notifications

### Problem
`alert()` dialogs block the entire browser tab, require a manual click to dismiss, and look unprofessional.

### Solution

Replaced all `alert()` calls with a lightweight CSS toast notification anchored to the bottom-centre of the screen.

**HTML (once, inside `.main-container`):**
```html
<div id="toastMsg" class="toast-msg"></div>
```

**CSS:**
```css
.toast-msg {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%) translateY(60px);
    background: #2c3e50;
    color: white;
    padding: 10px 24px;
    border-radius: 20px;
    font-size: 14px;
    opacity: 0;
    transition: all 0.3s;
    z-index: 9999;
    pointer-events: none;
}
.toast-msg.show {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}
```

**JavaScript:**
```js
function showToast(msg, duration = 2000) {
    const t = document.getElementById('toastMsg');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), duration);
}
```

---

## 8. localStorage Form Persistence

### Problem
If a user accidentally navigated away or refreshed the page mid-way through filling out a form, all typed data was lost.

### Solution

All 6 text areas auto-save to `localStorage` on every `input` event and are restored on `DOMContentLoaded`.

**Fields persisted:**

| Key | Textarea |
|-----|----------|
| `form_office_body_prompt` | Office Order prompt |
| `form_office_body` | Office Order body |
| `form_circular_body_prompt` | Circular prompt |
| `form_circular_body` | Circular body |
| `form_policy_body_prompt` | Policy prompt |
| `form_policy_body` | Policy body |

**Save on input:**
```js
document.querySelectorAll('textarea').forEach(ta => {
    ta.addEventListener('input', saveFormData);
});
```

**Restore on load:**
```js
function restoreFormData() {
    LS_FIELDS.forEach(id => {
        const el = document.getElementById(id);
        const saved = localStorage.getItem('form_' + id);
        if (el && saved) {
            el.value = saved;
            // Also update word/char counters
        }
    });
}
```

**Clear on submit** (so old data doesn't pollute the next session):
```js
form.addEventListener('submit', function () {
    clearFormStorage('office'); // or 'circular' / 'policy'
});
```

---

## 9. Copy Body Button (Result Pages)

### Problem
There was no way to quickly copy the generated body text for use in other applications (email, internal systems, etc.) without manually selecting and copying.

### Solution

Added a **📋 Copy Body** button to the action bar on all three result pages.

**Files changed:**
- `result_office_order.html`
- `result_circular.html`
- `result_policy.html`

**HTML:**
```html
<button class="btn btn-warning btn-lg" onclick="copyBody()" style="color:#212529;">
    📋 Copy Body
</button>
```

**JavaScript (same in all three result pages):**
```js
function copyBody() {
    const bodyEl = document.getElementById(
        currentVersion === 'original' ? 'originalBody' : 'regeneratedBody'
    );
    const text = bodyEl.innerText || bodyEl.textContent;
    navigator.clipboard.writeText(text.trim()).then(() => {
        const btn = event.currentTarget;
        const orig = btn.innerHTML;
        btn.innerHTML = '✅ Copied!';
        setTimeout(() => btn.innerHTML = orig, 2000);
    });
}
```

Copies whichever version (original or regenerated) is currently active. Button label temporarily changes to **✅ Copied!** for 2 seconds as confirmation.

---

## 10. Print Button (Result Pages)

### Problem
The `@media print` CSS was already in place (hiding buttons, shadows, backgrounds for a clean printout) but there was no Print button in the UI. Users had to use `Ctrl+P` or browser menu.

### Solution

Added a **🖨️ Print** button alongside the existing action buttons on all three result pages.

```html
<button class="btn btn-info btn-lg" onclick="window.print()" style="color:#212529;">
    🖨️ Print
</button>
```

This triggers the browser's native print dialog. Combined with the existing `@media print` rules, the output is a clean document preview with:
- No action buttons
- No regenerate section
- No version toggle bar
- White background, no box-shadows

---

## Files Changed

| File | Changes |
|------|---------|
| `templates/generator/home.html` | Default English, auto-date, disabled PO button, char counters, spinners, select-all, toast, localStorage |
| `templates/generator/result_office_order.html` | Copy Body button, Print button, fixed `regenerateBody()` (missing `prompt`/`lang` vars), `copyBody()` function |
| `templates/generator/result_circular.html` | Copy Body button, Print button, `copyBody()` function |
| `templates/generator/result_policy.html` | Copy Body button, Print button, `copyBody()` function |

---

## Summary

These enhancements require **zero backend changes** — all improvements are pure frontend (HTML/CSS/JS). They are backwards-compatible and do not affect existing API endpoints, session handling, or AI service logic.

