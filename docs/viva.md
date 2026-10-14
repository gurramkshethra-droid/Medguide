# Viva Q&A (short)

**What problem does this solve?** Common symptoms were mapping poorly onto frightening unrelated classes. We fixed feature-order DataFrame mapping, a 3-symptom minimum, a 15% weak-score guard, and triage before ML.

**Is this a diagnosis?** No. Labels are possible explanations.

**Why SQLite?** Local PBL storage. Tables `users`, `assessments`, `audit_logs`. History is saved only with consent.

**Why OSM?** Nominatim geocode + Overpass amenities within 5 km, no API key. Missing tags show “Not listed”. Hardcoded Hyderabad fallback lists were removed because they made every failed search look like the same hospitals.

**Is there a skin model?** No. The page is a Skin Health Guide. Photo analysis is future scope.

**How is the model evaluated?** `/evaluation` computes test accuracy, top-3 accuracy, 5-fold CV, a confusion-matrix image, and a drop-1–2-symptom robustness check from Training.csv + model.pkl without rewriting the pickle.
