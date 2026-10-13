from flask import Blueprint, render_template, request, abort
from services.health_data import health_service

conditions_bp = Blueprint("conditions", __name__, url_prefix="/conditions")

@conditions_bp.route("")
@conditions_bp.route("/")
def list_conditions():
    query = request.args.get("q", "").strip()
    results = health_service.search_conditions(query)
    return render_template(
        "conditions/list.html",
        conditions=results,
        query=query,
        total_count=len(results)
    )

@conditions_bp.route("/<slug>")
def condition_detail(slug):
    condition = health_service.get_condition_by_slug(slug)
    if not condition:
        abort(404, description=f"The health condition guide '{slug}' could not be found.")
    
    is_emergency = health_service.is_emergency_condition(condition.get("model_key"))
    return render_template(
        "conditions/detail.html",
        condition=condition,
        is_emergency=is_emergency
    )
