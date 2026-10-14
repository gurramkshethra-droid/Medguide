"""
Evaluate the saved model.pkl against Training.csv without retraining model.pkl.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, confusion_matrix, top_k_accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from services.ml_service import ml_service

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static" / "evaluation"
MATRIX_PATH = STATIC_DIR / "confusion_matrix.png"


class EvaluationService:
    def __init__(self):
        self._cache = None

    def _load_frame(self):
        path = Path(__file__).resolve().parent.parent / "Training.csv"
        df = pd.read_csv(path)
        df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
        y = df["prognosis"].astype(str)
        features = list(ml_service.symptoms)
        missing = [c for c in features if c not in df.columns]
        if missing:
            raise RuntimeError(f"Training.csv is missing saved model features: {missing[:5]}")
        X = df[features]
        return X, y, features

    def _robustness_top3(self, model, X, y, rng):
        dropped = X.copy()
        for idx in dropped.index:
            positives = [c for c in dropped.columns if dropped.at[idx, c] == 1]
            if len(positives) <= 2:
                continue
            drop_n = 1 if len(positives) == 3 else int(rng.integers(1, 3))
            chosen = rng.choice(positives, size=min(drop_n, len(positives) - 1), replace=False)
            for col in chosen:
                dropped.at[idx, col] = 0
        proba = model.predict_proba(dropped)
        return float(top_k_accuracy_score(y, proba, k=3, labels=model.classes_))

    def compute(self, force=False):
        if self._cache and not force:
            return self._cache
        if not ml_service.is_loaded:
            raise RuntimeError("model.pkl is not loaded.")

        X, y, features = self._load_frame()
        n_rows = int(len(X))
        n_duplicates = int(X.assign(prognosis=y).duplicated().sum())
        n_classes = int(y.nunique())

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Evaluate the saved fitted model (not retrained) on a holdout split of Training.csv.
        # Because the published pickle was trained on this same file, holdout accuracy is
        # optimistic and is reported with that limitation.
        saved = ml_service.model
        test_pred = saved.predict(X_test)
        test_proba = saved.predict_proba(X_test)
        test_accuracy = float(accuracy_score(y_test, test_pred))
        top3_accuracy = float(
            top_k_accuracy_score(y_test, test_proba, k=3, labels=saved.classes_)
        )

        cv_model = clone(saved)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(cv_model, X, y, cv=cv, scoring="accuracy")
        cv_mean = float(cv_scores.mean())
        cv_std = float(cv_scores.std())

        rng = np.random.default_rng(42)
        robustness_top3 = self._robustness_top3(saved, X_test, y_test, rng)

        labels = list(saved.classes_)
        matrix = confusion_matrix(y_test, test_pred, labels=labels)
        self._write_matrix_image(matrix, labels)

        payload = {
            "n_rows": n_rows,
            "n_features": len(features),
            "n_classes": n_classes,
            "n_duplicate_rows": n_duplicates,
            "test_size": int(len(X_test)),
            "test_accuracy": round(test_accuracy, 4),
            "top3_accuracy": round(top3_accuracy, 4),
            "cv_folds": 5,
            "cv_accuracy_mean": round(cv_mean, 4),
            "cv_accuracy_std": round(cv_std, 4),
            "cv_scores": [round(float(s), 4) for s in cv_scores],
            "robustness_drop_1_or_2_top3_accuracy": round(robustness_top3, 4),
            "confusion_matrix_image": "/static/evaluation/confusion_matrix.png",
            "model_type": type(saved).__name__,
            "limitations": [
                "Training.csv is a clean, labelled teaching dataset, not messy clinic notes.",
                f"{n_duplicates} duplicate rows were counted in Training.csv.",
                "The table has no age, gender, duration, or medical-history columns.",
                "Holdout metrics evaluate model.pkl on a split of the same file it was trained on, so they are optimistic.",
                "5-fold cross-validation fits cloned estimators and does not modify model.pkl.",
                "Scores are not clinically validated probabilities of disease.",
            ],
        }
        self._cache = payload
        return payload

    def _write_matrix_image(self, matrix, labels):
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 10))
        im = ax.imshow(matrix, interpolation="nearest", cmap="Blues")
        ax.set_title("Confusion matrix (holdout split of Training.csv)")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        ticks = range(len(labels))
        ax.set_xticks(list(ticks))
        ax.set_yticks(list(ticks))
        ax.set_xticklabels(labels, rotation=90, fontsize=7)
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlabel("Predicted class")
        ax.set_ylabel("True class")
        fig.tight_layout()
        fig.savefig(MATRIX_PATH, dpi=120)
        plt.close(fig)


evaluation_service = EvaluationService()
