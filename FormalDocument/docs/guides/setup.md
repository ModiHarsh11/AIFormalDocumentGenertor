# 🛠️ Local Development Setup

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or higher |
| pip | Latest |
| Git | Any |
| Gemini API Key | Required — get from [Google AI Studio](https://aistudio.google.com) |

---

## Step 1 — Clone the Repository

```bash
git clone <repository-url>
cd FormalDocument
```

---

## Step 2 — Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows PowerShell
.\venv\Scripts\activate

# Activate — Windows CMD
venv\Scripts\activate.bat

# Activate — Linux/macOS
source venv/bin/activate
```

> **Note:** The project already includes a `finale_BISAG-N/` virtual environment directory. You can activate that directly:
> ```powershell
> .\finale_BISAG-N\Scripts\activate
> ```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

Or from within the `ai_formal_generator` directory:
```bash
pip install -r ai_formal_generator/requirements.txt
```

### Key packages installed:
| Package | Purpose |
|---|---|
| `django` | Web framework |
| `google-genai` | Gemini AI SDK (new, maintained) |
| `langchain` | `PromptTemplate` abstraction |
| `weasyprint` | PDF generation from HTML |
| `python-docx` | DOCX document generation |
| `PyPDF2` | PDF read/write |
| `fonttools` | Devanagari font rendering |
| `python-dotenv` | `.env` file support |

---

## Step 4 — Configure Environment Variables

Copy the provided template:

```bash
cp .env.example .env
```

Edit `.env` and fill in at minimum:

```env
GEMINI_API_KEY=your-api-key-here
```

The development settings use sensible defaults for all other variables.
See [`guides/environment_variables.md`](environment_variables.md) for the full list.


---

## Step 5 — Run Migrations

```bash
cd ai_formal_generator
python manage.py migrate
```

---

## Step 6 — Start the Development Server

```bash
python manage.py runserver
```

Open: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Project Structure After Setup

```
FormalDocument/
├── docs/                        ← Documentation (you are here)
├── requirements.txt
└── ai_formal_generator/
    ├── manage.py
    ├── .env                     ← Create this (not committed)
    ├── db.sqlite3
    ├── office_order.json
    ├── circular.json
    ├── policy.json
    ├── ai_formal_generator/     ← Django settings package
    └── generator/               ← Main app
```

---

## Verifying the Setup

Navigate to `http://127.0.0.1:8000/` — you should see the document type selector (home page).

Try generating an Office Order body:
1. Select **Office Order**
2. Enter a topic
3. Select language (English or Hindi)
4. Click **Generate Body**

If you see generated text appear in the body field, the AI layer is working correctly.

---

## Common Issues

### `GEMINI_API_KEY is not configured`
The API key is missing. Set `GEMINI_API_KEY` in your `.env` file (see Step 4).

### WeasyPrint PDF errors on Windows
WeasyPrint requires GTK libraries on Windows. If you see font/PDF errors, ensure you have [GTK for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer) installed, or use WSL.

### Hindi text not rendering in PDF
Ensure `NotoSansDevanagari-Regular.ttf` and `NotoSansDevanagari-Bold.ttf` are present in `static/generator/fonts/`.

### `No module named 'google.genai'`
Run `pip install google-genai`. The old `google-generativeai` package is different.

