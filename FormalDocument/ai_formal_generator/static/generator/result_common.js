/**
 * Shared JavaScript for all result preview pages (Office Order, Circular, Policy).
 *
 * Requires the hosting page to define these globals BEFORE loading this script:
 *   - window.RESULT_CONFIG.updateBodyUrl   (Django {% url %} for update-body)
 *   - window.RESULT_CONFIG.regenerateUrl   (Django {% url %} for regenerate-body)
 *   - window.RESULT_CONFIG.csrfToken       (Django {{ csrf_token }})
 *   - window.RESULT_CONFIG.originalBody    ({{ body|escapejs }})
 *   - window.RESULT_CONFIG.previousPrompt  ({{ body_prompt|escapejs }})
 *   - window.RESULT_CONFIG.language        ({{ language }})
 */

let currentVersion = 'original';
let originalBody = window.RESULT_CONFIG.originalBody;
let regeneratedBody = '';
const previousPrompt = window.RESULT_CONFIG.previousPrompt;
const csrfToken = window.RESULT_CONFIG.csrfToken;

// ── Download overlay ─────────────────────────────────────────────────────────
function startDownload(url, msg) {
    const overlay = document.getElementById('downloadOverlay');
    document.getElementById('overlayMsg').textContent = msg;
    overlay.style.display = 'flex';
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = url;
    document.body.appendChild(iframe);
    iframe.onload = function () {
        setTimeout(() => { overlay.style.display = 'none'; }, 1500);
    };
    setTimeout(() => { overlay.style.display = 'none'; }, 30000);
}

// ── Version toggle (original ↔ regenerated) ──────────────────────────────────
function switchVersion(version) {
    currentVersion = version;
    const originalDiv = document.getElementById('originalBody');
    const regeneratedDiv = document.getElementById('regeneratedBody');
    const toggleButtons = document.querySelectorAll('.btn-toggle');

    if (version === 'original') {
        originalDiv.classList.remove('hidden');
        regeneratedDiv.classList.add('hidden');
        toggleButtons[0].classList.add('active');
        toggleButtons[1].classList.remove('active');
        updateSessionBody(originalBody);
    } else {
        originalDiv.classList.add('hidden');
        regeneratedDiv.classList.remove('hidden');
        toggleButtons[0].classList.remove('active');
        toggleButtons[1].classList.add('active');
        updateSessionBody(regeneratedBody);
    }
}

// ── Persist selected body version to Django session ──────────────────────────
function updateSessionBody(bodyContent) {
    const formData = new FormData();
    formData.append('body', bodyContent);
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(window.RESULT_CONFIG.updateBodyUrl, {
        method: 'POST',
        body: formData
    });
}

// ── Copy body to clipboard ───────────────────────────────────────────────────
function copyBody() {
    const bodyEl = document.getElementById(currentVersion === 'original' ? 'originalBody' : 'regeneratedBody');
    const text = bodyEl.innerText || bodyEl.textContent;
    navigator.clipboard.writeText(text.trim()).then(() => {
        const btn = event.currentTarget;
        const orig = btn.innerHTML;
        btn.innerHTML = '✅ Copied!';
        setTimeout(() => btn.innerHTML = orig, 2000);
    });
}

// ── AI Regeneration ──────────────────────────────────────────────────────────
function regenerateBody() {
    const prompt = document.getElementById('regeneratePrompt').value.trim();
    const lang = window.RESULT_CONFIG.language;
    const status = document.getElementById('regenerateStatus');

    if (!prompt) {
        alert('Please enter a regeneration prompt! / कृपया पुनर्जनन संकेत दर्ज करें!');
        return;
    }

    status.textContent = '⏳ Regenerating... / पुनर्जनित कर रहे हैं...';
    status.style.color = '#ffc107';

    const formData = new FormData();
    formData.append('regenerate_prompt', prompt);
    formData.append('previous_prompt', previousPrompt);
    formData.append('previous_body', originalBody);
    formData.append('language', lang);
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(window.RESULT_CONFIG.regenerateUrl, {
        method: 'POST',
        body: formData
    })
    .then(res => res.text().then(text => ({ ok: res.ok, statusCode: res.status, text })))
    .then(({ ok, statusCode, text }) => {
        if (!ok) {
            status.textContent = '✗ Error! / त्रुटि!';
            status.style.color = '#dc3545';
            alert('❌ ' + (text || `Error ${statusCode}. Please try again.`));
            return;
        }
        regeneratedBody = text;

        const regeneratedDiv = document.getElementById('regeneratedBody');
        regeneratedDiv.innerHTML = text.replace(/\n/g, '<br>');

        document.getElementById('versionToggle').classList.remove('hidden');
        switchVersion('regenerated');

        status.textContent = '✓ Successfully Regenerated! / सफलतापूर्वक पुनर्जनित!';
        status.style.color = '#28a745';

        setTimeout(() => {
            status.textContent = '';
        }, 3000);
    })
    .catch(() => {
        status.textContent = '✗ Error! / त्रुटि!';
        status.style.color = '#dc3545';
        alert('❌ No internet connection. Please check your network and try again.');
    });
}

