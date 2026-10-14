# MediGuide AI

Flask + scikit-learn student project. Educational only — not a diagnosis.

## Run on Windows

```bat
cd c:\Users\gurra\Downloads\mediguide-ai-project\mediguide-ai
python -m pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5001

SQLite file: `mediguide.db` (existing records are kept). Copy `.env.example` to `.env` to set `SECRET_KEY`.

Tests: `python -m pytest tests -q`

Full write-up: `docs/`
