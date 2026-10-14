# ML methodology and limitations

## Saved model (`model.pkl`)

- Type: `sklearn.ensemble.RandomForestClassifier`
- Features: 132 binary symptom columns, saved order beginning `itching`, `skin_rash`, … ending `yellow_crust_ooze`
- Classes: 41 prognosis labels (including `GERD`, `Common Cold`, `Heart attack`, …)
- The pickle is never retrained by this app.

## Inference

Selected names are mapped onto that exact feature list. A one-row pandas DataFrame with those column names is passed to `predict_proba`. Website ranking for complete training rows must match direct `model.predict` on the same vector.

## Confidence guard

If the top probability is below 0.15, the UI reports that there is not enough information to assess reliably. Further medical assessment may still be appropriate. Triage banners are still shown.

## Limitations (plain language)

- Training.csv is a clean teaching table, not clinic notes.
- Duplicate rows exist in the file.
- There is no age, gender, or history column in the table (those fields are used only by triage/UI).
- Holdout accuracy of `model.pkl` on a split of the same file is optimistic.
- Output is a possible explanation, not a diagnosis and not a validated probability.
