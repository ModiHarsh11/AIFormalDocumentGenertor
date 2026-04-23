from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ── Auth ─────────────────────────────────────────────────────────────────
    path("login/",    views.login_view,    name="login"),
    path("logout/",   views.logout_view,   name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/",  views.profile_view,  name="profile"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="generator/password_reset_form.html",
            email_template_name="generator/password_reset_email.txt",
            subject_template_name="generator/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="generator/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="generator/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="generator/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # ── Dashboard & document management ─────────────────────────────────────
    path("dashboard/",                       views.dashboard,        name="dashboard"),
    path("documents/<int:doc_id>/",          views.document_view,    name="document_view"),
    path("documents/<int:doc_id>/edit/",     views.document_edit,    name="document_edit"),
    path("documents/<int:doc_id>/delete/",   views.document_delete,  name="document_delete"),
    path("documents/<int:doc_id>/pdf/",      views.download_doc_pdf,  name="download_doc_pdf"),
    path("documents/<int:doc_id>/docx/",     views.download_doc_docx, name="download_doc_docx"),

    # ── Home page with integrated selector ──────────────────────────────────
    path("", views.home, name="home"),
    path("office-order/", views.home, name="home_office"),
    path("circular/",     views.home, name="home_circular"),
    path("policy/",       views.home, name="home_policy"),

    # ── OFFICE ORDER ─────────────────────────────────────────────────────────
    path("generate-body/",    views.generate_body,          name="generate_body"),
    path("regenerate-body/",  views.regenerate_office_body, name="regenerate_office_body"),
    path("update-body/",      views.update_office_body,     name="update_office_body"),
    path("result/",           views.result_office_order,    name="result"),
    path("download/pdf/",     views.download_pdf,           name="download_pdf"),
    path("download/docx/",    views.download_docx,          name="download_docx"),

    # ── CIRCULAR ─────────────────────────────────────────────────────────────
    path("circular/generate-body/",   views.generate_circular_body,   name="generate_circular_body"),
    path("circular/regenerate-body/", views.regenerate_circular_body, name="regenerate_circular_body"),
    path("circular/update-body/",     views.update_circular_body,     name="update_circular_body"),
    path("circular/result/",          views.result_circular,          name="result_circular"),
    path("circular/pdf/",             views.download_circular_pdf,    name="download_circular_pdf"),
    path("circular/docx/",            views.download_circular_docx,   name="download_circular_docx"),

    # ── POLICY ───────────────────────────────────────────────────────────────
    path("policy/generate-body/",   views.generate_policy_body,   name="generate_policy_body"),
    path("policy/regenerate-body/", views.regenerate_policy_body, name="regenerate_policy_body"),
    path("policy/update-body/",     views.update_policy_body,     name="update_policy_body"),
    path("policy/result/",          views.result_policy,          name="result_policy"),
    path("policy/pdf/",             views.download_policy_pdf,    name="download_policy_pdf"),
    path("policy/docx/",            views.download_policy_docx,   name="download_policy_docx"),

    # ── ADVERTISEMENT ───────────────────────────────────────────────────────
    path("advertisement/",          views.home,                       name="home_advertisement"),
    path("advertisement/result/",   views.result_advertisement,       name="result_advertisement"),
    path("advertisement/pdf/",      views.download_advertisement_pdf,  name="download_advertisement_pdf"),
    path("advertisement/docx/",     views.download_advertisement_docx, name="download_advertisement_docx"),
]
