from flask import Blueprint, render_template
from services.ml_service import ml_service
from services.symptom_engine import (
    AGE_GROUPS,
    DURATION_CHOICES,
    HISTORY_CHOICES,
    SEVERITY_CHOICES,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    symptoms = ml_service.get_supported_symptoms()
    return render_template(
        "index.html",
        symptoms=symptoms,
        duration_choices=DURATION_CHOICES,
        severity_choices=SEVERITY_CHOICES,
        age_choices=AGE_GROUPS,
        history_choices=HISTORY_CHOICES,
    )


@main_bp.route("/about")
def about():
    return render_template("pages/about.html")


@main_bp.route("/privacy")
def privacy():
    return render_template("pages/privacy.html")


@main_bp.route("/disclaimer")
def disclaimer():
    return render_template("pages/disclaimer.html")
