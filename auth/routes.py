from flask import (
    render_template, request, redirect, url_for,
    session, flash, abort, jsonify
)
from functools import wraps
import re
from datetime import datetime, timezone

from auth import auth_bp
from extensions import db, limiter
from models.user import User
from models.assessment import Assessment
from models.audit import AuditLog

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "info")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "info")
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "admin":
            abort(403, description="Administrator access required.")
        return view(*args, **kwargs)
    return wrapped

@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def register():
    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        consent = request.form.get("consent_save_history") == "on"

        if not name or len(name) > 80:
            flash("Enter a name with 1–80 characters.", "error")
            return render_template("register.html")

        if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return render_template("register.html")

        if len(password) > 128:
            flash("Password is too long.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        # Crucial security invariant: All registrations default strictly to "user" role
        new_user = User(
            name=name,
            email=email,
            role="user",
            consent_save_history=consent
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

            audit = AuditLog(
                user_id=new_user.id,
                event_type="REGISTER",
                ip_address=request.remote_addr,
                details=f"New user registered: {email}"
            )
            db.session.add(audit)
            db.session.commit()

            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("register.html")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("15 per minute")
def login():
    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact support.", "error")
                return render_template("login.html")

            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            session["user_role"] = user.role

            audit = AuditLog(
                user_id=user.id,
                event_type="LOGIN_SUCCESS",
                ip_address=request.remote_addr,
                details=f"User logged in: {email}"
            )
            db.session.add(audit)
            db.session.commit()

            flash("Welcome back!", "success")
            return redirect(url_for("auth.dashboard"))

        # Generic error message to prevent account enumeration
        audit = AuditLog(
            user_id=user.id if user else None,
            event_type="LOGIN_FAILED",
            ip_address=request.remote_addr,
            details=f"Failed login attempt for: {email}"
        )
        db.session.add(audit)
        db.session.commit()

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    recent_assessments = user.assessments.order_by(
        db.desc(Assessment.created_at)
    ).limit(5).all()

    total_assessments_count = user.assessments.count()

    return render_template(
        "dashboard.html",
        name=user.name,
        email=user.email,
        role=user.role,
        consent_save_history=user.consent_save_history,
        assessments=recent_assessments,
        total_assessments=total_assessments_count
    )


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
@limiter.limit("20 per minute")
def profile():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "update_info":
            name = request.form.get("name", "").strip()
            consent = request.form.get("consent_save_history") == "on"

            if not name or len(name) > 80:
                flash("Name must be between 1 and 80 characters.", "error")
                return redirect(url_for("auth.profile"))

            user.name = name
            user.consent_save_history = consent
            db.session.commit()

            session["user_name"] = user.name
            flash("Profile information and privacy preferences updated successfully.", "success")
            return redirect(url_for("auth.profile"))

        elif action == "change_password":
            current_pass = request.form.get("current_password", "")
            new_pass = request.form.get("new_password", "")
            confirm_pass = request.form.get("confirm_password", "")

            if not user.check_password(current_pass):
                flash("Current password is incorrect.", "error")
                return redirect(url_for("auth.profile"))

            if len(new_pass) < 8:
                flash("New password must contain at least 8 characters.", "error")
                return redirect(url_for("auth.profile"))

            if new_pass != confirm_pass:
                flash("New passwords do not match.", "error")
                return redirect(url_for("auth.profile"))

            user.set_password(new_pass)
            db.session.commit()

            audit = AuditLog(
                user_id=user.id,
                event_type="PASSWORD_CHANGE",
                ip_address=request.remote_addr,
                details="Password changed successfully"
            )
            db.session.add(audit)
            db.session.commit()

            flash("Password updated successfully.", "success")
            return redirect(url_for("auth.profile"))

    return render_template(
        "profile.html",
        user=user,
        name=user.name,
        email=user.email,
        role=user.role,
        consent_save_history=user.consent_save_history,
        created_at=user.created_at
    )


@auth_bp.route("/profile/delete-account", methods=["POST"])
@login_required
def delete_account():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    password = request.form.get("password", "")
    if not user.check_password(password):
        flash("Password verification failed. Account deletion cancelled.", "error")
        return redirect(url_for("auth.profile"))

    audit = AuditLog(
        user_id=user.id,
        event_type="ACCOUNT_DELETED",
        ip_address=request.remote_addr,
        details=f"User account deleted: {user.email}"
    )
    db.session.add(audit)

    # Delete user and all associated data
    db.session.delete(user)
    db.session.commit()

    session.clear()
    flash("Your account and all associated assessment records have been deleted.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/history", methods=["GET"])
@login_required
def history():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    assessments = user.assessments.order_by(
        db.desc(Assessment.created_at)
    ).all()

    return render_template(
        "history.html",
        name=user.name,
        consent_save_history=user.consent_save_history,
        assessments=assessments
    )


@auth_bp.route("/history/<int:assessment_id>/delete", methods=["POST"])
@login_required
def delete_assessment(assessment_id):
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        flash("Assessment record not found.", "error")
        return redirect(url_for("auth.history"))

    # Strict server-side ownership verification: User can only delete their own record
    if assessment.user_id != session["user_id"]:
        abort(403, description="You do not have permission to delete this assessment.")

    db.session.delete(assessment)
    db.session.commit()

    flash("Assessment record deleted.", "success")
    return redirect(url_for("auth.history"))


@auth_bp.route("/history/clear-all", methods=["POST"])
@login_required
def clear_all_history():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    deleted_count = user.assessments.count()
    user.assessments.delete()
    db.session.commit()

    flash(f"Successfully deleted {deleted_count} assessment records.", "success")
    return redirect(url_for("auth.history"))


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    user_id = session.get("user_id")
    audit = AuditLog(
        user_id=user_id,
        event_type="LOGOUT",
        ip_address=request.remote_addr,
        details="User logged out"
    )
    db.session.add(audit)
    db.session.commit()

    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))
