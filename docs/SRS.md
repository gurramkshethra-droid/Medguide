# Software requirements specification (student PBL)

## Purpose

Educational symptom guidance and care navigation. Not clinical decision support.

## Functional requirements

- FR1 User can select multiple symptoms, duration, severity, age group, history.
- FR2 System maps labels onto `model.pkl` feature names in saved order.
- FR3 System refuses a ranking with fewer than 3 symptoms (`add more symptoms`).
- FR4 Triage runs before ML. Emergency/urgent banners are not overridden.
- FR5 Weak top-class probability (< 0.15) shows “not enough information to assess reliably”.
- FR6 Results show top 3 possible explanations, matched symptoms, typical unreported symptoms.
- FR7 Follow-up yes/no questions re-run ranking and show the change.
- FR8 Care finder uses Nominatim + Overpass; missing OSM tags display “Not listed”.
- FR9 Skin page is a health guide only.
- FR10 Each model class has a `/conditions/<slug>` guide including `/conditions/gerd`.
- FR11 `/evaluation` reports numbers computed from Training.csv and model.pkl.
- FR12 Register/login/logout; history saved only with consent; users see only their rows.

## Non-functional

- CSRF on HTML forms; password hashing; secrets via environment; `.env` gitignored.
- Rate limits on predict and finder APIs.
- No medicine doses or named prescriptions in guidance.

## Weak-confidence threshold

`WEAK_TOP_PROBABILITY = 0.15` in `services/ml_service.py`. If the saved Random Forest’s top class probability is below 15%, the UI states the ranking is not reliable. This is not a clinical cut-off.
