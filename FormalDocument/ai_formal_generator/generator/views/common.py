"""Shared view helpers and the home page view."""

import json
import logging
import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from generator.constants import DESIGNATION_MAP
from generator.services import generate_body as svc_generate_body
from generator.services import regenerate_body as svc_regenerate_body
from generator.services import translate_subject_to_hindi as svc_translate_subject_to_hindi

logger = logging.getLogger(__name__)
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# ---------------------------------------------------------------------------
# Load JSON data files (read once at module import)
# ---------------------------------------------------------------------------
_DATA_DIR: Path = Path(settings.BASE_DIR) / "generator" / "data"


def _load(filename: str) -> dict:
    path = _DATA_DIR / filename
    with path.open(encoding="utf-8") as f:
        return json.load(f)


OFFICE_ORDER: dict = _load("office_order.json")
CIRCULAR: dict     = _load("circular.json")
POLICY: dict       = _load("policy.json")
ADVERTISEMENT: dict = _load("advertisement.json")


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def format_date_ddmmyyyy(date_str: str) -> str:
    """Convert ``YYYY-MM-DD`` → ``DD-MM-YYYY``."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    except (ValueError, TypeError):
        return date_str

def format_date_ddmmmyyyy(date_str: str) -> str:
    """Convert `YYYY-MM-DD` to `DD-MMM-YYYY` (month in uppercase)."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%b-%Y").upper()
    except (ValueError, TypeError):
        return date_str

def maybe_translate_subject(subject: str, language: str) -> str:
    """Translate subject to Hindi only when Hindi output is selected."""
    subject = (subject or "").strip()
    if language != "hi" or not subject:
        return subject
    if _DEVANAGARI_RE.search(subject):
        return subject
    try:
        translated = svc_translate_subject_to_hindi(subject).strip()
        return translated or subject
    except RuntimeError as exc:
        logger.warning("Subject translation skipped: %s", exc)
        return subject
    except Exception:
        logger.exception("Unexpected subject translation failure.")
        return subject


# ---------------------------------------------------------------------------
# Save generated document to database
# ---------------------------------------------------------------------------

def save_document_to_db(
    *,
    user,
    document_type: str,
    language: str,
    reference_id: str = "",
    date_raw: str = "",
    subject: str = "",
    body_prompt: str = "",
    body: str = "",
    from_position: str = "",
    to_data: list | None = None,
    extra_data: dict | None = None,
):
    """Create and persist a GeneratedDocument record.  Returns the saved instance."""
    from generator.models import GeneratedDocument
    doc = GeneratedDocument(
        user=user if (user and user.is_authenticated) else None,
        document_type=document_type,
        language=language,
        reference_id=reference_id,
        date_raw=date_raw,
        subject=subject,
        body_prompt=body_prompt,
        body=body,
        from_position=from_position,
        to_data=to_data or [],
        extra_data=extra_data or {},
    )
    doc.save()
    return doc


# ---------------------------------------------------------------------------
# Shared AI body generation / regeneration handlers
# ---------------------------------------------------------------------------

@login_required
def handle_generate_body(request, document_type: str, view_name: str) -> HttpResponse:
    """Shared handler for all generate-body POST endpoints."""
    prompt = request.POST.get("body_prompt", "").strip()
    lang   = request.POST.get("language", "en")
    try:
        body = svc_generate_body(document_type, prompt, lang)
        return HttpResponse(body)
    except RuntimeError as exc:
        logger.warning("%s failed: %s", view_name, exc)
        return HttpResponse(str(exc), status=503)
    except Exception:
        logger.exception("Unexpected error in %s", view_name)
        return HttpResponse("Unexpected error. Please try again.", status=500)


@login_required
def handle_regenerate_body(request, document_type: str, view_name: str) -> HttpResponse:
    """Shared handler for all regenerate-body POST endpoints."""
    regenerate_prompt = request.POST.get("regenerate_prompt", "").strip()
    previous_prompt   = request.POST.get("previous_prompt", "").strip()
    previous_body     = request.POST.get("previous_body", "").strip()
    lang              = request.POST.get("language", "en")
    try:
        body = svc_regenerate_body(
            document_type,
            topic=previous_prompt,
            previous_body=previous_body,
            refinement_prompt=regenerate_prompt,
            language=lang,
        )
        return HttpResponse(body)
    except RuntimeError as exc:
        logger.warning("%s failed: %s", view_name, exc)
        return HttpResponse(str(exc), status=503)
    except Exception:
        logger.exception("Unexpected error in %s", view_name)
        return HttpResponse("Unexpected error. Please try again.", status=500)


def handle_update_body(request, session_key: str):
    """Shared handler for all update-body POST endpoints."""
    from django.http import JsonResponse

    new_body = request.POST.get("body", "")
    doc_id   = request.POST.get("doc_id")

    # Update DB record if doc_id present
    if doc_id:
        try:
            from generator.models import GeneratedDocument
            doc = GeneratedDocument.objects.get(id=doc_id, is_deleted=False)
            if doc.user == request.user or request.user.is_staff:
                doc.body = new_body
                doc.version += 1
                doc.save(update_fields=["body", "version", "updated_at"])
        except Exception:
            pass

    if session_key in request.session:
        request.session[session_key]["body"] = new_body
        request.session.modified = True
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)


# ---------------------------------------------------------------------------
# Shared logo / DOCX / PDF helpers
# ---------------------------------------------------------------------------

_LOGO_RELATIVE = os.path.join("static", "generator", "bisag_logo.png")


def get_logo_path() -> str | None:
    path = os.path.join(settings.BASE_DIR, _LOGO_RELATIVE)
    return path if os.path.exists(path) else None


def get_logo_file_uri() -> str | None:
    path = get_logo_path()
    if path:
        return f"file:///{path.replace(chr(92), '/')}"
    return None


def make_docx_response(doc, filename: str) -> HttpResponse:
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    response = HttpResponse(
        buf,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ---------------------------------------------------------------------------
# Home view
# ---------------------------------------------------------------------------

def home(request):
    return render(request, "generator/home.html", {
        "designations": DESIGNATION_MAP.keys(),
        "people": CIRCULAR["people"],
        "advertisement_data": ADVERTISEMENT,
    })
