# MediGuide AI — project documentation

Educational Flask + scikit-learn PBL. Not a medical device and not a diagnosis.

## Abstract

MediGuide AI helps a user enter symptoms, checks warning signs first, then shows possible explanations from a saved Random Forest model (`model.pkl`) together with reviewed condition guides and nearby OpenStreetMap care listings. Photo analysis is future scope.

## Objectives

1. Map browser symptoms onto the saved model features in order.
2. Run red-flag triage before ML ranking.
3. Show top three possible explanations with matched and unreported typical symptoms.
4. Ask 2–3 follow-up questions that separate the top classes.
5. Find nearby hospitals and clinics from OpenStreetMap without inventing fields.
6. Store optional assessment history in SQLite for signed-in users who consent.

## Install and run (Windows)

```bat
cd c:\Users\gurra\Downloads\mediguide-ai-project\mediguide-ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open http://127.0.0.1:5001

Database: existing `mediguide.db` (SQLite). `db.create_all()` adds missing tables only; it does not drop records. Do not delete `model.pkl`, `Training.csv`, or `mediguide.db`.

```bat
python -m pytest tests -q
```

## Modules

| Path | Role |
|------|------|
| `app.py` | Flask factory, blueprint registration, SQLite attach |
| `config.py` | Dev / test / production settings |
| `auth/` | Register, login, logout, dashboard, history |
| `routes/symptom.py` | `/predict` and `/predict/follow-up` |
| `services/ml_service.py` | Load `model.pkl`, DataFrame in saved feature order |
| `services/triage.py` | Emergency / urgent / routine rules |
| `services/symptom_engine.py` | Mapping, min 3 symptoms, confidence guard |
| `services/followup.py` | Adaptive yes/no questions |
| `services/doctor_service.py` | Nominatim + Overpass, 5 km, cache |
| `services/health_data.py` | Condition guides + homecare |
| `services/evaluation_service.py` | Metrics from Training.csv + model.pkl |
| `models/` | User, Assessment, AuditLog |

## Future scope

- Clinically evaluated skin-image model (not the symptom model)
- Clinician messaging
- PostgreSQL deployment
