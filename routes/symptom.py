from flask import Blueprint, request, jsonify, session
import json
from extensions import db, csrf, limiter
from services.ml_service import ml_service
from services.health_data import health_service
from models.user import User
from models.assessment import Assessment

symptom_bp = Blueprint("symptom", __name__)

@symptom_bp.route("/predict", methods=["POST"])
@csrf.exempt  # Preserves exact AJAX fetch behavior from index.html
@limiter.limit("30 per minute")
def predict():
    data = request.get_json(silent=True) or {}
    chosen = data.get("symptoms", [])

    if not isinstance(chosen, list) or not chosen:
        return jsonify(error="Please select at least one symptom."), 400

    try:
        prediction_result = ml_service.predict(chosen, top_k=3)
    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except RuntimeError:
        return jsonify(error="Symptom analysis service is currently unavailable."), 503
    except Exception:
        return jsonify(error="An internal error occurred during analysis."), 500

    # Enrich each prediction with verified health service data & slugs
    has_emergency = False
    for item in prediction_result["results"]:
        disease_key = item["disease"]
        info = health_service.get_condition_by_key(disease_key)
        if info:
            item["title"] = info["title"]
            item["slug"] = info["slug"]
            item["specialty"] = info["specialty"]
        else:
            item["title"] = disease_key
            item["slug"] = ""
            item["specialty"] = "General Practice"
        
        is_em = health_service.is_emergency_condition(disease_key)
        item["is_emergency"] = is_em
        if is_em:
            has_emergency = True

    emergency_alert = None
    if has_emergency:
        emergency_alert = (
            "🚨 CRITICAL WARNING: One or more evaluated predictions indicate a time-sensitive medical emergency "
            "(such as acute cardiovascular or neurological symptoms). If you are experiencing sudden severe chest pain, "
            "unilateral weakness, difficulty speaking, or loss of consciousness, CALL EMERGENCY SERVICES (911 / 112 / 999) IMMEDIATELY."
        )

    # Privacy-conscious assessment saving: ONLY if logged in and consent explicitly granted
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
        if user and user.consent_save_history:
            top_prediction = prediction_result["results"][0] if prediction_result["results"] else {}
            new_assessment = Assessment(
                user_id=user.id,
                symptoms_json=json.dumps(chosen),
                top_disease=top_prediction.get("title", top_prediction.get("disease", "Unknown")),
                confidence=top_prediction.get("confidence", 0.0),
                results_json=json.dumps(prediction_result["results"])
            )
            try:
                db.session.add(new_assessment)
                db.session.commit()
            except Exception:
                db.session.rollback()

    response_data = {
        "results": prediction_result["results"],
        "urgency": prediction_result["urgency"],
        "disclaimer": prediction_result["disclaimer"]
    }
    if emergency_alert:
        response_data["emergency_alert"] = emergency_alert

    return jsonify(response_data)
