from flask import Blueprint, request, jsonify, session
import json
from extensions import db, csrf, limiter
from services.ml_service import ml_service
from services.symptom_engine import symptom_engine, MIN_SYMPTOMS
from services.followup import (
    apply_answers,
    ranking_delta,
    suggest_followup_questions,
)
from models.user import User
from models.assessment import Assessment

symptom_bp = Blueprint("symptom", __name__)

ALLOWED_DURATION = {
    "less_than_a_day", "1_to_3_days", "4_to_7_days", "more_than_a_week", "more_than_a_month"
}
ALLOWED_SEVERITY = {"mild", "moderate", "severe"}
ALLOWED_AGE = {"child", "teen", "adult", "older_adult"}
ALLOWED_HISTORY = {
    "none", "diabetes", "hypertension", "heart_disease", "asthma", "immunosuppression", "pregnancy"
}


def _parse_context(data):
    history = data.get("history", [])
    if isinstance(history, str):
        history = [history]
    if not isinstance(history, list):
        history = []
    history = [h for h in history if h in ALLOWED_HISTORY and h != "none"]
    return {
        "duration": data.get("duration") if data.get("duration") in ALLOWED_DURATION else "1_to_3_days",
        "severity": data.get("severity") if data.get("severity") in ALLOWED_SEVERITY else "moderate",
        "age_group": data.get("age_group") if data.get("age_group") in ALLOWED_AGE else "adult",
        "history": history,
        "location": (data.get("location") or "").strip()[:120],
    }


def _run_analysis(chosen, context):
    return symptom_engine.analyze(
        ml_service,
        chosen,
        top_k=3,
        context=context,
    )


def _maybe_save(assessment, chosen):
    user_id = session.get("user_id")
    if not user_id or not assessment.get("results"):
        return
    user = db.session.get(User, user_id)
    if not user or not user.consent_save_history:
        return
    top_prediction = assessment["results"][0]
    new_assessment = Assessment(
        user_id=user.id,
        symptoms_json=json.dumps(assessment.get("selected_symptoms", chosen)),
        top_disease=top_prediction.get("title", top_prediction.get("disease", "Unknown")),
        confidence=top_prediction.get("confidence", 0.0),
        results_json=json.dumps(assessment["results"]),
    )
    try:
        db.session.add(new_assessment)
        db.session.commit()
    except Exception:
        db.session.rollback()


def _response_payload(assessment, context, extra=None):
    safety = assessment.get("safety") or {}
    payload = {
        "results": assessment["results"],
        "urgency": assessment["urgency"],
        "disclaimer": assessment["disclaimer"],
        "safety": safety,
        "guidance": assessment.get("guidance"),
        "context": assessment.get("context"),
        "selected_symptoms": assessment.get("selected_symptoms"),
        "location": context["location"],
        "status": assessment.get("status", "ok"),
        "message": assessment.get("message"),
        "low_confidence": assessment.get("low_confidence", False),
        "needs_more_symptoms": assessment.get("needs_more_symptoms", False),
        "min_symptoms": MIN_SYMPTOMS,
        "followup_questions": assessment.get("followup_questions") or [],
    }
    if safety.get("level") == "emergency":
        payload["emergency_alert"] = (
            "Emergency warning signs were identified from the symptoms you entered. "
            "If you have sudden severe chest pain, one-sided weakness, trouble speaking, "
            "or loss of consciousness, call emergency services (112 / 911 / 108) immediately. "
            "Ordinary self-care guidance should wait until you are safe."
        )
    if extra:
        payload.update(extra)
    return payload


@symptom_bp.route("/predict", methods=["POST"])
@csrf.exempt
@limiter.limit("30 per minute")
def predict():
    data = request.get_json(silent=True) or {}
    chosen = data.get("symptoms", [])

    if not isinstance(chosen, list) or not chosen:
        return jsonify(error="Please select at least one symptom."), 400

    context = _parse_context(data)
    try:
        assessment = _run_analysis(chosen, context)
    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except RuntimeError:
        return jsonify(error="Symptom analysis service is currently unavailable."), 503
    except Exception:
        return jsonify(error="An internal error occurred during analysis."), 500

    questions = suggest_followup_questions(
        symptom_engine,
        assessment.get("selected_symptoms") or [],
        [item["disease"] for item in assessment.get("results") or []],
        count=3,
    )
    assessment["followup_questions"] = questions
    _maybe_save(assessment, chosen)
    return jsonify(_response_payload(assessment, context))


@symptom_bp.route("/predict/follow-up", methods=["POST"])
@csrf.exempt
@limiter.limit("30 per minute")
def predict_followup():
    data = request.get_json(silent=True) or {}
    chosen = data.get("symptoms", [])
    answers = data.get("answers", {})
    if not isinstance(chosen, list) or not chosen:
        return jsonify(error="Please select at least one symptom."), 400

    context = _parse_context(data)
    try:
        first = _run_analysis(chosen, context)
        updated, applied = apply_answers(first.get("selected_symptoms") or chosen, answers)
        second = _run_analysis(updated, context)
    except ValueError as ve:
        return jsonify(error=str(ve)), 400
    except RuntimeError:
        return jsonify(error="Symptom analysis service is currently unavailable."), 503

    delta = ranking_delta(first.get("results"), second.get("results"))
    questions = suggest_followup_questions(
        symptom_engine,
        second.get("selected_symptoms") or [],
        [item["disease"] for item in second.get("results") or []],
        count=3,
    )
    second["followup_questions"] = questions
    _maybe_save(second, updated)
    return jsonify(
        _response_payload(
            second,
            context,
            extra={
                "previous_results": first.get("results"),
                "ranking_change": delta,
                "applied_answers": applied,
            },
        )
    )
