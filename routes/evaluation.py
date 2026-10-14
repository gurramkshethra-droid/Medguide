from flask import Blueprint, render_template, abort
from services.evaluation_service import evaluation_service

evaluation_bp = Blueprint("evaluation", __name__)


@evaluation_bp.route("/evaluation")
def evaluation_page():
    try:
        metrics = evaluation_service.compute()
    except Exception:
        abort(500, description="Model evaluation could not be computed from Training.csv and model.pkl.")
    return render_template("evaluation.html", metrics=metrics)
