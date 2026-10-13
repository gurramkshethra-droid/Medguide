import os
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

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
            logger.error(f"Model file not found at {self.model_path}")
            return

        try:
            with open(self.model_path, "rb") as f:
                saved = pickle.load(f)

            if isinstance(saved, dict):
                self.model = saved.get("model")
                self.symptoms = saved.get("features", [])
            else:
                self.model, self.symptoms = saved
            
            logger.info(
                f"Symptom model successfully loaded. "
                f"Total features: {len(self.symptoms)}, Classes: {len(self.model.classes_) if self.model else 0}"
            )
        except Exception as e:
            logger.error(f"Failed to load symptom model: {e}")
            self.model = None
            self.symptoms = []

    @property
    def is_loaded(self) -> bool:
        return self.model is not None and len(self.symptoms) > 0

    def get_supported_symptoms(self):
        return list(self.symptoms)

    def predict(self, chosen_symptoms, top_k=3):
        if not self.is_loaded:
            raise RuntimeError("Symptom model is not available or failed to load.")

        if not isinstance(chosen_symptoms, (list, set)) or len(chosen_symptoms) == 0:
            raise ValueError("Please select at least one symptom.")

        # Validate symptoms against supported list
        invalid = [s for s in chosen_symptoms if s not in self.symptoms]
        if invalid:
            raise ValueError(f"Invalid symptom(s) provided: {', '.join(invalid[:5])}")

        # Construct vector with exact feature names DataFrame to eliminate sklearn warnings
        feature_vector = pd.DataFrame(
            [[1 if s in chosen_symptoms else 0 for s in self.symptoms]],
            columns=self.symptoms
        )

        probabilities = self.model.predict_proba(feature_vector)[0]
        top_indices = np.argsort(probabilities)[::-1][:top_k]

        results = [
            {
                "disease": str(self.model.classes_[i]),
                "confidence": round(float(probabilities[i]) * 100, 1)
            }
            for i in top_indices
        ]

        return {
            "results": results,
            "selected_symptoms": list(chosen_symptoms),
            "urgency": (
                "Model output is educational only. Seek medical advice. "
                "For an emergency, contact local emergency services immediately."
            ),
            "disclaimer": (
                "Not a diagnosis. Scores are statistical model estimates, "
                "not clinically validated probabilities of disease."
            )
        }

# Global singleton
ml_service = SymptomMLService()
