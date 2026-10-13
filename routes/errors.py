from flask import Blueprint, render_template, jsonify, request

errors_bp = Blueprint("errors", __name__)

@errors_bp.app_errorhandler(400)
def bad_request(error):
    if request.path.startswith("/predict") or request.is_json:
        return jsonify(error=getattr(error, "description", "Bad Request")), 400
    return render_template("errors/error.html", code=400, title="Bad Request", message=getattr(error, "description", "The request could not be processed.")), 400

@errors_bp.app_errorhandler(403)
def forbidden(error):
    if request.path.startswith("/predict") or request.is_json:
        return jsonify(error="Forbidden"), 403
    return render_template("errors/error.html", code=403, title="Access Denied", message=getattr(error, "description", "You do not have permission to view this resource.")), 403

@errors_bp.app_errorhandler(404)
def not_found(error):
    if request.path.startswith("/predict") or request.is_json:
        return jsonify(error="Resource Not Found"), 404
    return render_template("errors/error.html", code=404, title="Page Not Found", message="The requested page could not be found. Please check the URL or return to home."), 404

@errors_bp.app_errorhandler(429)
def ratelimit_handler(error):
    if request.path.startswith("/predict") or request.is_json:
        return jsonify(error="Rate limit exceeded. Please slow down your requests."), 429
    return render_template("errors/error.html", code=429, title="Too Many Requests", message="You have made too many requests in a short period. Please wait a moment and try again."), 429

@errors_bp.app_errorhandler(500)
def internal_error(error):
    if request.path.startswith("/predict") or request.is_json:
        return jsonify(error="Internal Server Error"), 500
    return render_template("errors/error.html", code=500, title="Server Error", message="An unexpected server error occurred. Our team has been notified."), 500
