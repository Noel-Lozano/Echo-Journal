from flask import Blueprint, redirect, url_for, session
from flask_dance.contrib.google import google
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return '<a href="/login/google">Login with Google</a>'

@auth_bp.route('/login/google/authorized')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info from Google", 400

    info = resp.json()
    google_id = info["id"]
    email = info["email"]
    name = info.get("name")

    # Check if user exists
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User(google_id=google_id, email=email, name=name)
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    return f"Welcome, {user.name or user.email}!"

@auth_bp.route('/debug-token')
def debug_token():
    if not google.authorized:
        return "Not authorized with Google."
    return f"Token: {google.token}"

