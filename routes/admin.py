from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session
from extensions import db
from models.user import User
from models.assessment import Assessment
from models.audit import AuditLog
from auth.routes import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("")
@admin_bp.route("/")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_assessments = Assessment.query.count()
    total_audits = AuditLog.query.count()

    users = User.query.order_by(db.desc(User.created_at)).all()
    recent_audits = AuditLog.query.order_by(db.desc(AuditLog.timestamp)).limit(20).all()

    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_assessments=total_assessments,
        total_audits=total_audits,
        users=users,
        recent_audits=recent_audits,
        current_admin_id=session.get("user_id")
    )


@admin_bp.route("/user/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    if user_id == session.get("user_id"):
        flash("You cannot deactivate your own administrator account.", "error")
        return redirect(url_for("admin.dashboard"))

    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.dashboard"))

    user.is_active = not user.is_active
    db.session.commit()

    status_str = "activated" if user.is_active else "deactivated"
    audit = AuditLog(
        user_id=session.get("user_id"),
        event_type="ADMIN_TOGGLE_USER",
        ip_address=request.remote_addr,
        details=f"Admin {session.get('user_email')} {status_str} user {user.email}"
    )
    db.session.add(audit)
    db.session.commit()

    flash(f"User {user.email} has been {status_str}.", "success")
    return redirect(url_for("admin.dashboard"))
