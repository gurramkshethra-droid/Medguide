import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# If the top class probability is below this, the ranking is treated as too weak
# to present as a reliable assessment. Documented in /evaluation and docs/.
WEAK_TOP_PROBABILITY = 0.15


class SymptomMLService:
    def __init__(self, model_path=None):
        if model_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            model_path = base_dir / "model.pkl"
        self.model_path = Path(model_path)
        self.model = None
        self.symptoms = []
        self._load_model()

    def _load_model(self):
        if not self.model_path.exists():
            logger.error("Model file not found at %s", self.model_path)
            return

        try:
            import pickle

            with open(self.model_path, "rb") as f:
                saved = pickle.load(f)

            if isinstance(saved, dict):
                self.model = saved.get("model")
                self.symptoms = list(saved.get("features", []))
            else:
                self.model, features = saved
                self.symptoms = list(features)

            logger.info(
                "Symptom model loaded. Features: %s, Classes: %s",
                len(self.symptoms),
                len(self.model.classes_) if self.model is not None else 0,
            )
        except Exception as exc:
            logger.error("Failed to load symptom model: %s", exc)
            self.model = None
            self.symptoms = []

    @property
    def is_loaded(self) -> bool:
        return self.model is not None and len(self.symptoms) > 0

    def get_supported_symptoms(self):
        return list(self.symptoms)

    def get_classes(self):
        if not self.is_loaded:
            return []
        return [str(c) for c in self.model.classes_]

    def build_feature_frame(self, chosen_symptoms):
        """
        Map selected symptom names onto the saved feature list, in the exact
        saved order, as a one-row pandas DataFrame with those column names.
        """
        if not self.is_loaded:
            raise RuntimeError("Symptom model is not available or failed to load.")

        chosen_set = set(chosen_symptoms)
        values = [1 if name in chosen_set else 0 for name in self.symptoms]
        return pd.DataFrame([values], columns=self.symptoms)

    def predict_proba_vector(self, chosen_symptoms):
        frame = self.build_feature_frame(chosen_symptoms)
        probabilities = self.model.predict_proba(frame)[0]
        return frame, probabilities

    def predict(self, chosen_symptoms, top_k=3):
        if not self.is_loaded:
            raise RuntimeError("Symptom model is not available or failed to load.")

        if not isinstance(chosen_symptoms, (list, set, tuple)) or len(chosen_symptoms) == 0:
            raise ValueError("Please select at least one symptom.")

        _frame, probabilities = self.predict_proba_vector(list(chosen_symptoms))
        top_k = max(int(top_k), 1)
        top_indices = np.argsort(probabilities)[::-1][:top_k]
        top_probability = float(np.max(probabilities))

        results = [
            {
                "disease": str(self.model.classes_[i]),
                "confidence": round(float(probabilities[i]) * 100, 1),
                "probability": float(probabilities[i]),
            }
            for i in top_indices
        ]

        return {
            "results": results,
            "selected_symptoms": list(chosen_symptoms),
            "top_probability": top_probability,
            "low_confidence": top_probability < WEAK_TOP_PROBABILITY,
            "weak_threshold": WEAK_TOP_PROBABILITY,
            "urgency": (
                "Model output is educational only. Seek medical advice. "
                "For an emergency, contact local emergency services immediately."
            ),
            "disclaimer": (
                "Not a diagnosis. Scores are statistical model estimates, "
                "not clinically validated probabilities of disease."
            ),
        }


ml_service = SymptomMLService()
