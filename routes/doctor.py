from flask import Blueprint, render_template, request, jsonify
from services.doctor_service import doctor_service
from extensions import limiter, csrf

doctor_bp = Blueprint("doctor", __name__)

@doctor_bp.route("/doctors", methods=["GET"])
def doctor_finder_page():
    location = request.args.get("location", "").strip()
    specialty = request.args.get("specialty", "").strip()

    results_data = None
    if location:
        results_data = doctor_service.find_doctors(location_text=location, specialty=specialty)

    return render_template(
        "doctor/finder.html",
        location=location,
        specialty=specialty,
        results_data=results_data
    )

@doctor_bp.route("/api/doctors/search", methods=["POST"])
@csrf.exempt
@limiter.limit("20 per minute")
def api_search_doctors():
    data = request.get_json(silent=True) or {}
    location_text = data.get("location", "").strip()
    specialty = data.get("specialty", "").strip()
    lat = data.get("lat")
    lon = data.get("lon")

    try:
        if lat is not None and lon is not None:
            lat = float(lat)
            lon = float(lon)
        else:
            lat = None
            lon = None
    except (ValueError, TypeError):
        lat = None
        lon = None

    result = doctor_service.find_doctors(
        location_text=location_text if not (lat and lon) else None,
        lat=lat,
        lon=lon,
        specialty=specialty
    )
    return jsonify(result)
