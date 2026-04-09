import datetime

from django.conf import settings
from django.db import models, transaction


# ---------------------------------------------------------------------------
# DocumentLog — legacy audit table (kept for backward compatibility)
# ---------------------------------------------------------------------------
class DocumentLog(models.Model):
    """Audit log for generated documents (legacy table, preserved)."""

    DOCUMENT_TYPES = [
        ("Office Order", "Office Order"),
        ("Circular", "Circular"),
        ("Policy", "Policy"),
        ("Notice", "Notice"),
        ("Other", "Other"),
    ]

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "हिंदी (Hindi)"),
    ]

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, db_index=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")
    reference_id = models.CharField(max_length=100, db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Document Log (Legacy)"

    def __str__(self):
        return f"{self.document_type} | {self.reference_id}"


# ---------------------------------------------------------------------------
# GeneratedDocument — primary document store (new)
# ---------------------------------------------------------------------------
class GeneratedDocument(models.Model):
    """Full record of every document generated, with all editable fields."""

    DOC_TYPE_CHOICES = [
        ("office", "Office Order"),
        ("circular", "Circular"),
        ("policy", "Policy"),
    ]

    DOC_TYPE_PREFIX = {
        "office": "OO",
        "circular": "CIR",
        "policy": "POL",
    }

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "हिंदी (Hindi)"),
    ]

    # ── Identity ────────────────────────────────────────────────────────────
    serial_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-assigned unique serial: BISAG-OO-YYYY-NNNNN",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_documents",
    )
    document_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, db_index=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")

    # ── Editable form fields (stored individually) ───────────────────────
    reference_id = models.CharField(
        max_length=300, blank=True,
        help_text="Reference / file number shown on document",
    )
    date_raw = models.CharField(
        max_length=20, blank=True,
        help_text="Date in YYYY-MM-DD format",
    )
    subject = models.TextField(blank=True)
    body_prompt = models.TextField(blank=True, help_text="AI generation prompt text")
    body = models.TextField(blank=True, help_text="Generated document body text")
    from_position = models.CharField(max_length=200, blank=True)
    # to_data stores raw IDs (circular) or designation keys (office/policy)
    to_data = models.JSONField(default=list, blank=True)
    # extra_data holds document-type-specific fields (e.g. attached_pdf_name)
    extra_data = models.JSONField(default=dict, blank=True)

    # ── Lifecycle & metrics ──────────────────────────────────────────────
    version = models.PositiveIntegerField(
        default=1,
        help_text="Increments each time the document is edited",
    )
    download_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Generated Document"
        verbose_name_plural = "Generated Documents"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["document_type", "-created_at"]),
            models.Index(fields=["serial_number"]),
        ]

    def __str__(self):
        return f"{self.serial_number} — {self.get_document_type_display()}"

    # ── Serial number generation ─────────────────────────────────────────
    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = self._generate_serial()
        super().save(*args, **kwargs)

    def _generate_serial(self) -> str:
        prefix = self.DOC_TYPE_PREFIX.get(self.document_type, "DOC")
        year = datetime.date.today().year
        with transaction.atomic():
            count = (
                GeneratedDocument.objects
                .filter(document_type=self.document_type, created_at__year=year)
                .count()
                + 1
            )
        return f"BISAG-{prefix}-{year}-{count:05d}"

    # ── Convenience properties ───────────────────────────────────────────
    @property
    def type_label(self) -> str:
        return self.get_document_type_display()

    @property
    def language_label(self) -> str:
        return dict(self.LANGUAGE_CHOICES).get(self.language, self.language)


# ---------------------------------------------------------------------------
# UserProfile — optional extra user data
# ---------------------------------------------------------------------------
class UserProfile(models.Model):
    """Additional profile information linked 1:1 to Django User."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    department = models.CharField(max_length=200, blank=True)
    designation = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "User Profile"

    def __str__(self):
        return f"Profile of {self.user.username}"
