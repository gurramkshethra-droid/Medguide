from flask import Blueprint, render_template, request, jsonify, flash
from services.skin_service import skin_service
from extensions import limiter

skin_bp = Blueprint("skin", __name__)

@skin_bp.route("/skin-analysis", methods=["GET", "POST"])
@limiter.limit("15 per minute")
def skin_analysis_page():
    result_data = None

    if request.method == "POST":
        file = request.files.get("skin_image")
        if not file or file.filename == "":
            flash("Please choose an image file (PNG, JPG, or WEBP) to analyze.", "error")
        else:
            result_data = skin_service.analyze_skin_image(file)
            if result_data.get("status") == "validation_error":
                flash(result_data.get("error", "Invalid file uploaded."), "error")
                result_data = None

    return render_template(
        "skin/analysis.html",
        result=result_data
    )

@skin_bp.route("/api/skin/analyze", methods=["POST"])
@limiter.limit("15 per minute")
def api_skin_analyze():
    file = request.files.get("skin_image")
    if not file or file.filename == "":
        return jsonify(error="No image file provided."), 400

    result = skin_service.analyze_skin_image(file)
    if result.get("status") == "validation_error":
        return jsonify(error=result.get("error")), 400

    return jsonify(result)
