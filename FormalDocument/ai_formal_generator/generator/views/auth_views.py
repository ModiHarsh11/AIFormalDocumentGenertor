"""Authentication views: register, login (via Django built-in), logout, profile."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect

from generator.models import UserProfile


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_view(request):
    """New user registration."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        first_name  = request.POST.get("first_name", "").strip()
        last_name   = request.POST.get("last_name", "").strip()
        username    = request.POST.get("username", "").strip()
        email       = request.POST.get("email", "").strip()
        department  = request.POST.get("department", "").strip()
        designation = request.POST.get("designation", "").strip()
        password1   = request.POST.get("password1", "")
        password2   = request.POST.get("password2", "")

        errors = []
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append("Username already taken. Choose another.")
        if not email:
            errors.append("Email is required.")
        elif User.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")
        if len(password1) < 8:
            errors.append("Password must be at least 8 characters.")
        if password1 != password2:
            errors.append("Passwords do not match.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "generator/register.html", {"post": request.POST})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )
        # Create or update profile
        UserProfile.objects.update_or_create(
            user=user,
            defaults={"department": department, "designation": designation},
        )
        login(request, user)
        messages.success(request, f"Welcome, {user.get_full_name() or username}! Your account has been created.")
        return redirect("dashboard")

    return render(request, "generator/register.html", {})


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def login_view(request):
    """User login with username/password."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or "dashboard"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "generator/login.html", {"username": username})

    return render(request, "generator/login.html", {"next": request.GET.get("next", "")})


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    """View and update user profile."""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        action = request.POST.get("action", "profile")

        if action == "profile":
            user.first_name  = request.POST.get("first_name", "").strip()
            user.last_name   = request.POST.get("last_name", "").strip()
            user.email       = request.POST.get("email", "").strip()
            user.save()
            profile.department  = request.POST.get("department", "").strip()
            profile.designation = request.POST.get("designation", "").strip()
            profile.save()
            messages.success(request, "Profile updated successfully.")

        elif action == "password":
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, "Password changed successfully.")
            else:
                for field_errors in form.errors.values():
                    for err in field_errors:
                        messages.error(request, err)

        return redirect("profile")

    from generator.models import GeneratedDocument
    doc_count = GeneratedDocument.objects.filter(user=user, is_deleted=False).count()
    return render(request, "generator/profile.html", {
        "profile": profile,
        "doc_count": doc_count,
    })
