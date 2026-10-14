"""
Adaptive yes/no follow-up questions.

Questions are symptoms that best separate the current top candidate diseases
using Training.csv symptom frequency profiles.
"""

from __future__ import annotations

YES_VALUES = {"yes", "y", "true", "1"}
NO_VALUES = {"no", "n", "false", "0"}


def _label(symptom):
    return str(symptom).replace("_", " ")


def suggest_followup_questions(engine, selected_symptoms, top_diseases, count=3):
    selected = set(selected_symptoms)
    diseases = [str(d) for d in top_diseases[:3] if d]
    if len(diseases) < 2:
        return []

    scores = {}
    for disease in diseases:
        profile = engine.profiles.get(disease, {})
        for symptom, freq in profile.items():
            if symptom in selected or freq < 0.4:
                continue
            others = [
                engine.profiles.get(other, {}).get(symptom, 0.0)
                for other in diseases
                if other != disease
            ]
            if not others:
                continue
            mean_other = sum(others) / len(others)
            separation = abs(freq - mean_other)
            if separation < 0.35:
                continue
            prev = scores.get(symptom)
            if prev is None or separation > prev["separation"]:
                scores[symptom] = {
                    "symptom": symptom,
                    "label": _label(symptom),
                    "question": f"Do you also have {_label(symptom)}?",
                    "separation": round(separation, 3),
                    "more_typical_of": disease,
                }

    ranked = sorted(scores.values(), key=lambda item: item["separation"], reverse=True)
    return ranked[:count]


def apply_answers(selected_symptoms, answers):
    """
    answers: dict mapping symptom feature name -> yes/no.
    Invalid values raise ValueError.
    """
    updated = list(selected_symptoms)
    seen = set(updated)
    applied = {}

    if not isinstance(answers, dict):
        raise ValueError("Follow-up answers must be an object of symptom: yes/no pairs.")

    for raw_key, raw_value in answers.items():
        key = str(raw_key).strip()
        value = str(raw_value).strip().lower()
        if value not in YES_VALUES and value not in NO_VALUES:
            raise ValueError(
                f"Invalid answer for '{key}'. Please answer yes or no."
            )
        is_yes = value in YES_VALUES
        applied[key] = "yes" if is_yes else "no"
        if is_yes and key not in seen:
            updated.append(key)
            seen.add(key)

    return updated, applied


def ranking_delta(previous_results, new_results):
    prev = [item.get("disease") for item in previous_results or []]
    new = [item.get("disease") for item in new_results or []]
    changes = []
    for index, disease in enumerate(new):
        if disease in prev:
            old_index = prev.index(disease)
            if old_index != index:
                changes.append(
                    {
                        "disease": disease,
                        "from": old_index + 1,
                        "to": index + 1,
                    }
                )
        else:
            changes.append({"disease": disease, "from": None, "to": index + 1})
    dropped = [d for d in prev if d not in new]
    for disease in dropped:
        changes.append({"disease": disease, "from": prev.index(disease) + 1, "to": None})
    return {
        "previous": prev,
        "current": new,
        "changed": prev != new,
        "moves": changes,
    }
