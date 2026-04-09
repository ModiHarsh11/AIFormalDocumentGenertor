from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import DocumentLog, GeneratedDocument, UserProfile


# ---------------------------------------------------------------------------
# Inline profile in User admin
# ---------------------------------------------------------------------------
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ("department", "designation")


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "doc_count")

    def doc_count(self, obj):
        return obj.generated_documents.filter(is_deleted=False).count()
    doc_count.short_description = "Docs Generated"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ---------------------------------------------------------------------------
# Legacy DocumentLog admin
# ---------------------------------------------------------------------------
@admin.register(DocumentLog)
class DocumentLogAdmin(admin.ModelAdmin):
    list_display = ("document_type", "language", "reference_id", "created_at")
    search_fields = ("reference_id", "content")
    list_filter = ("document_type", "language", "created_at")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


# ---------------------------------------------------------------------------
# GeneratedDocument admin (primary)
# ---------------------------------------------------------------------------
@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number",
        "document_type_badge",
        "user",
        "language",
        "subject_short",
        "from_position",
        "version",
        "download_count",
        "created_at",
        "is_deleted",
    )
    list_filter = ("document_type", "language", "is_deleted", "created_at")
    search_fields = ("serial_number", "reference_id", "subject", "body", "user__username", "user__email")
    readonly_fields = (
        "serial_number",
        "version",
        "download_count",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        ("Identity", {
            "fields": ("serial_number", "user", "document_type", "language", "is_deleted"),
        }),
        ("Document Fields", {
            "fields": (
                "reference_id", "date_raw", "subject", "from_position",
                "to_data", "body_prompt", "body", "extra_data",
            ),
        }),
        ("Metrics", {
            "fields": ("version", "download_count", "created_at", "updated_at"),
        }),
    )

    def document_type_badge(self, obj):
        colors = {"office": "#2c3e50", "circular": "#1a5276", "policy": "#145a32"}
        color = colors.get(obj.document_type, "#555")
        return format_html(
            '<span style="padding:2px 8px;border-radius:3px;color:white;background:{};font-size:11px">{}</span>',
            color,
            obj.get_document_type_display(),
        )
    document_type_badge.short_description = "Type"

    def subject_short(self, obj):
        s = obj.subject or ""
        return s[:60] + "…" if len(s) > 60 else s
    subject_short.short_description = "Subject"
