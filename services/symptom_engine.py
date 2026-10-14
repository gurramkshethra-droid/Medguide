"""
Symptom analysis engine.

Pipeline order:
1. Map browser labels onto the saved model feature names
2. Red-flag triage on the mapped inputs (never overridden by ML)
3. Require at least MIN_SYMPTOMS before ranking
4. Direct model inference (pandas DataFrame, saved column order)
5. Attach training-profile match / unreported typical symptoms
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

from services.health_data import health_service
from services.ml_service import WEAK_TOP_PROBABILITY
from services.triage import EMERGENCY, assess_triage

MIN_SYMPTOMS = 3

# High-stakes labels must not appear unless a distinctive marker is present.
HIGH_STAKES_REQUIRED = {
    "Heart attack": {"chest_pain", "sweating", "breathlessness"},
    "Paralysis (brain hemorrhage)": {"weakness_of_one_body_side", "altered_sensorium"},
    "Hypoglycemia": {
        "sweating",
        "anxiety",
        "irritability",
        "palpitations",
        "increased_hunger",
        "slurred_speech",
        "drying_and_tingling_lips",
    },
    "AIDS": {"extra_marital_contacts", "patches_in_throat", "muscle_wasting"},
}

HISTORY_CHOICES = {
    "none": "None reported",
    "diabetes": "Diabetes",
    "hypertension": "High blood pressure",
    "heart_disease": "Heart disease",
    "asthma": "Asthma",
    "immunosuppression": "Weakened immune system",
    "pregnancy": "Pregnancy",
}

AGE_GROUPS = {
    "child": "Child (under 12)",
    "teen": "Teen (12–17)",
    "adult": "Adult (18–64)",
    "older_adult": "Older adult (65+)",
}

DURATION_CHOICES = {
    "less_than_a_day": "Less than a day",
    "1_to_3_days": "1–3 days",
    "4_to_7_days": "4–7 days",
    "more_than_a_week": "More than a week",
    "more_than_a_month": "More than a month",
}

SEVERITY_CHOICES = {
    "mild": "Mild",
    "moderate": "Moderate",
    "severe": "Severe",
}


class SymptomAnalysisEngine:
    def __init__(self, training_path=None):
        base_dir = Path(__file__).resolve().parent.parent
        if training_path is None:
            training_path = base_dir / "Training.csv"
        self.training_path = Path(training_path)
        self.profiles = {}
        self.idf = {}
        self._load_profiles()

    def _load_profiles(self):
        if not self.training_path.exists():
            self.profiles = {}
            self.idf = {}
            return

        df = pd.read_csv(self.training_path)
        df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
        if "prognosis" not in df.columns:
            return

        df["prognosis"] = df["prognosis"].astype(str).str.strip()
        symptom_cols = [c for c in df.columns if c != "prognosis"]
        df_count = defaultdict(int)
        profiles = {}

        for disease, group in df.groupby("prognosis"):
            freqs = group[symptom_cols].mean()
            profile = {
                str(col): float(val)
                for col, val in freqs.items()
                if float(val) > 0.05
            }
            profiles[disease] = profile
            for symptom, freq in profile.items():
                if freq >= 0.2:
                    df_count[symptom] += 1

        n_diseases = max(len(profiles), 1)
        self.profiles = profiles
        self.idf = {
            symptom: math.log((1 + n_diseases) / (1 + count)) + 1.0
            for symptom, count in df_count.items()
        }

    @staticmethod
    def normalize_symptom(name, known_symptoms):
        raw = str(name or "").strip()
        if not raw:
            return None
        known = set(known_symptoms)
        if raw in known:
            return raw

        key = raw.lower().replace("-", "_").replace(" ", "_")
        key = re.sub(r"_+", "_", key).strip("_")
        if key in known:
            return key

        compact = re.sub(r"[^a-z0-9]", "", key)
        for symptom in known_symptoms:
            if re.sub(r"[^a-z0-9]", "", str(symptom).lower()) == compact:
                return symptom
        return None

    def map_symptoms(self, chosen_symptoms, known_symptoms):
        mapped = []
        invalid = []
        seen = set()
        for item in chosen_symptoms:
            resolved = self.normalize_symptom(item, known_symptoms)
            if resolved is None:
                invalid.append(str(item))
                continue
            if resolved not in seen:
                mapped.append(resolved)
                seen.add(resolved)
        return mapped, invalid

    def match_details(self, disease, selected):
        profile = self.profiles.get(disease, {})
        selected_set = set(selected)
        matched = [s for s in selected if profile.get(s, 0) >= 0.15]
        typical = [
            s for s, freq in sorted(profile.items(), key=lambda kv: kv[1], reverse=True)
            if freq >= 0.5
        ]
        unreported = [s for s in typical if s not in selected_set]
        return {
            "matched": matched,
            "unreported_typical": unreported[:8],
            "overlap": round(len(matched) / max(len(selected), 1), 3),
        }

    def _has_profile_support(self, disease, selected):
        profile = self.profiles.get(disease, {})
        return any(profile.get(s, 0) >= 0.05 for s in selected)

    def _next_steps(self, safety, specialty):
        if safety["level"] == "emergency":
            return [
                "Call local emergency services now (112 / 911 / 108) if symptoms are severe or rapidly worsening.",
                "Do not drive yourself if you have chest pain, one-sided weakness, or confusion.",
                "Bring a list of medicines and known conditions for the emergency team.",
            ]
        if safety["level"] == "urgent":
            return [
                f"Contact a clinician today, ideally in {specialty or 'general practice'} or urgent care.",
                "If new emergency signs appear (severe chest pain, one-sided weakness, trouble breathing), call emergency services.",
                "Avoid delaying care because an educational score looks low or high.",
            ]
        return [
            "Use the self-care steps below if you are otherwise well.",
            f"See a {specialty or 'general practice'} clinician if symptoms last, worsen, or you are unsure.",
            "Re-check sooner if warning signs develop.",
        ]

    def _format_result(self, disease, probability, selected):
        info = health_service.get_condition_by_key(disease) or {}
        detail = self.match_details(disease, selected)
        overlap = detail["overlap"]
        match_quality = "limited"
        if overlap >= 0.67 and len(selected) >= MIN_SYMPTOMS:
            match_quality = "good"
        elif overlap >= 0.34:
            match_quality = "moderate"

        return {
            "disease": disease,
            "title": info.get("title", disease),
            "slug": info.get("slug", ""),
            "specialty": info.get("specialty", "General Practice"),
            "confidence": round(float(probability) * 100, 1),
            "probability": float(probability),
            "match_quality": match_quality,
            "matched_symptoms": [s.replace("_", " ") for s in detail["matched"]],
            "unreported_typical_symptoms": [
                s.replace("_", " ") for s in detail["unreported_typical"]
            ],
            "description": info.get("description", ""),
            "self_care": info.get("homecare") or info.get("self_care", [])[:4],
            "warning_signs": info.get("warning_signs", [])[:4],
            "sources": info.get("sources", [])[:2],
        }

    def analyze(self, ml_service, chosen_symptoms, top_k=3, context=None):
        context = context or {}
        if not ml_service.is_loaded:
            raise RuntimeError("Symptom model is not available or failed to load.")

        known = ml_service.get_supported_symptoms()
        mapped, invalid = self.map_symptoms(chosen_symptoms, known)
        if invalid:
            raise ValueError(f"Invalid symptom(s) provided: {', '.join(invalid[:5])}")
        if not mapped:
            raise ValueError("Please select at least one symptom.")

        duration = context.get("duration") or "1_to_3_days"
        severity = context.get("severity") or "moderate"
        age_group = context.get("age_group") or "adult"
        history = context.get("history") or []
        if isinstance(history, str):
            history = [history] if history and history != "none" else []
        history = [h for h in history if h in HISTORY_CHOICES and h != "none"]

        safety = assess_triage(
            mapped, severity=severity, age_group=age_group, history=history
        )

        context_view = {
            "duration": DURATION_CHOICES.get(duration, duration),
            "severity": SEVERITY_CHOICES.get(severity, severity),
            "age_group": AGE_GROUPS.get(age_group, age_group),
            "history": [HISTORY_CHOICES[h] for h in history] or ["None reported"],
        }
        disclaimer = (
            "Illustrative educational assessment — not an actual medical diagnosis or "
            "prediction of disease. Model scores are not clinically validated probabilities."
        )

        insufficient = {
            "results": [],
            "selected_symptoms": mapped,
            "context": context_view,
            "safety": safety,
            "guidance": {
                "possible_explanations": [],
                "uncertainty": [],
                "self_care": [],
                "warning_signs": safety["warning_flags"][:6],
                "next_steps": self._next_steps(safety, "general practice"),
                "recommended_specialty": "General Practice",
            },
            "urgency": safety["summary"],
            "disclaimer": disclaimer,
            "low_confidence": False,
            "needs_more_symptoms": False,
        }

        if len(mapped) < MIN_SYMPTOMS:
            insufficient["needs_more_symptoms"] = True
            insufficient["status"] = "needs_more_symptoms"
            insufficient["message"] = (
                f"Add more symptoms (at least {MIN_SYMPTOMS}) before an educational ranking can be shown."
            )
            insufficient["guidance"]["uncertainty"] = [
                insufficient["message"],
                "Further medical assessment or testing may be appropriate even without a ranking.",
            ]
            return insufficient

        ml_raw = ml_service.predict(mapped, top_k=len(ml_service.model.classes_))
        ranked = []
        selected_set = set(mapped)
        for item in ml_raw["results"]:
            disease = item["disease"]
            required = HIGH_STAKES_REQUIRED.get(disease)
            if required and selected_set.isdisjoint(required):
                continue
            if not self._has_profile_support(disease, mapped):
                continue
            ranked.append(item)

        if not ranked:
            # Keep the raw ML order if profile support cannot be computed.
            ranked = list(ml_raw["results"])

        top = ranked[: max(top_k, 1)]
        results = [
            self._format_result(item["disease"], item["probability"], mapped)
            for item in top
        ]

        top_probability = float(ml_raw.get("top_probability") or 0.0)
        low_confidence = top_probability < WEAK_TOP_PROBABILITY
        top_item = results[0] if results else {}
        specialty = top_item.get("specialty", "General Practice")

        uncertainty = []
        if low_confidence:
            uncertainty.append(
                "Not enough information to assess reliably. The top model class is below "
                f"the {int(WEAK_TOP_PROBABILITY * 100)}% support threshold."
            )
            uncertainty.append(
                "Further medical assessment or testing may be appropriate. "
                "Serious conditions are not ruled out."
            )
        if safety["level"] != EMERGENCY:
            uncertainty.append(
                "This ranking is educational, not a diagnosis. Clinicians use examination "
                "and tests that this tool cannot perform."
            )

        self_care = top_item.get("self_care") or [
            "Rest, drink fluids if you can, and watch for new warning signs.",
            "Ask a pharmacist about over-the-counter options; this tool does not name products or doses.",
        ]
        if safety["level"] == EMERGENCY:
            self_care = [
                "Do not rely on home remedies while emergency signs are present.",
                "Stay with someone if possible while you seek emergency help.",
            ]

        warning_signs = list(
            dict.fromkeys(safety["warning_flags"] + (top_item.get("warning_signs") or []))
        )
        next_steps = self._next_steps(safety, specialty)
        if low_confidence:
            results_for_display = results
            message = "Not enough information to assess reliably."
        else:
            results_for_display = results
            message = None

        return {
            "results": results_for_display,
            "selected_symptoms": mapped,
            "context": context_view,
            "safety": safety,
            "guidance": {
                "possible_explanations": results_for_display,
                "uncertainty": uncertainty,
                "self_care": self_care,
                "warning_signs": warning_signs[:6],
                "next_steps": next_steps,
                "recommended_specialty": specialty,
            },
            "urgency": safety["summary"],
            "disclaimer": disclaimer,
            "low_confidence": low_confidence,
            "needs_more_symptoms": False,
            "status": "low_confidence" if low_confidence else "ok",
            "message": message,
            "ml_top_disease": ml_raw["results"][0]["disease"] if ml_raw["results"] else None,
            "ml_top_probability": top_probability,
            "weak_threshold": WEAK_TOP_PROBABILITY,
        }


symptom_engine = SymptomAnalysisEngine()
