# Running Migrations & First-Time Setup

## Why Migrations Haven't Run Yet

The Neon PostgreSQL server (`ep-winter-hall-a1y923vf-pooler.ap-southeast-1.aws.neon.tech`) is
blocked by the corporate network DNS. The fix is simple: run these commands **from a network that
can reach the internet** (mobile hotspot, home Wi-Fi, or after adding `8.8.8.8` as a DNS server in
Windows Network Settings → IPv4).

---

## Step 1 — Run Migrations

```bash
cd FormalDocument/ai_formal_generator

# Windows system Python (the venv is broken — use system Python directly)
python manage.py migrate --settings=ai_formal_generator.settings.development
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, generator, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying generator.0004_alter_documentlog_options_userprofile_and_more... OK
```

---

## Step 2 — Create Admin Superuser

```bash
python manage.py createsuperuser --settings=ai_formal_generator.settings.development
```

Enter any username/email/password you want. This account gets access to `/admin/`.

---

## Step 3 — Run the Server

```bash
python manage.py runserver --settings=ai_formal_generator.settings.development
```

Then open:
- **Home / Document Generator:** http://127.0.0.1:8000/
- **Login:** http://127.0.0.1:8000/login/
- **Register:** http://127.0.0.1:8000/register/
- **Dashboard:** http://127.0.0.1:8000/dashboard/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `django.db.utils.OperationalError: could not translate host name` | DNS blocked — switch network / fix DNS |
| `ModuleNotFoundError: No module named 'psycopg2'` | Run `pip install psycopg2-binary` |
| `ModuleNotFoundError: No module named 'dj_database_url'` | Run `pip install dj-database-url` |
| `ModuleNotFoundError: No module named 'crispy_forms'` | Run `pip install crispy-forms crispy-bootstrap5` |
| `django.core.exceptions.ImproperlyConfigured` about Django 4.2 | Run `pip install "django>=4.2.26,<4.3"` |
