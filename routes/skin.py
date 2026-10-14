from flask import Blueprint, render_template, redirect, url_for
from services.skin_service import ABCDE_CRITERIA, FUTURE_SCOPE_NOTE, WHEN_TO_SEE_DERMATOLOGIST

skin_bp = Blueprint("skin", __name__)


@skin_bp.route("/skin-health")
def skin_guide():
    return render_template(
        "skin/guide.html",
        abcde=ABCDE_CRITERIA,
        when_to_see=WHEN_TO_SEE_DERMATOLOGIST,
        future_scope=FUTURE_SCOPE_NOTE,
    )


@skin_bp.route("/skin-analysis")
def skin_analysis_redirect():
    return redirect(url_for("skin.skin_guide"), code=301)
