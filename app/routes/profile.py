from flask import Blueprint, render_template, render_template_string, request, session, jsonify
from app.models.profile import Profile
from app.models.users import User
from app import db
from datetime import datetime

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return "Not logged in", 401

    profile = Profile.query.filter_by(user_id=user_id).first()
    user = User.query.get(user_id)

    if request.method == "POST":
        data = request.get_json()
        text = data.get("text", "")
        photo = data.get("photo")
        preferences = data.get("preferences")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        updated = False
        if profile:
            profile.text = text
            if photo is not None:
                profile.photo = photo
            if preferences is not None:
                profile.preferences = preferences
            if first_name is not None:
                profile.first_name = first_name
            if last_name is not None:
                profile.last_name = last_name
            updated = True
        else:
            profile = Profile(
                user_id=user_id,
                text=text,
                date_joined=datetime.now(datetime.UTC),
                photo=photo if photo is not None else None,
                preferences=preferences if preferences is not None else {},
                first_name=first_name,
                last_name=last_name
            )
            db.session.add(profile)
            updated = True
        if username is not None and user:
            user.username = username
            updated = True
        if updated:
            db.session.commit()
        return jsonify({"status": "success"})

    return render_template("private_profile.html", user=user, profile=profile)

@profile_bp.route("/settings", methods=["GET"])
def settings():
    if "user_id" not in session:
        return "Not logged in", 401
    user = User.query.get(session["user_id"])
    return render_template("private_settings.html", user=user)

@profile_bp.route("/settings/change-password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return {"success": False, "error": "Not logged in."}, 401
    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    if not current_password or not new_password:
        return {"success": False, "error": "All fields are required."}, 400
    user = User.query.get(session["user_id"])
    if not user or not user.check_password(current_password):
        return {"success": False, "error": "Current password is incorrect."}, 400
    user.set_password(new_password)
    db.session.commit()
    return {"success": True}
