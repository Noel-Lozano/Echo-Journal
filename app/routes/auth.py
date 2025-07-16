from flask import Blueprint, request, session, redirect
from app.models.users import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET"])
def login_form():
    return """
        <form action="/login" method="post">
            <input name="username" placeholder="username" required><br>
            <input name="password" placeholder="password" type="password" required><br>
            <button type="submit">Login / Signup</button>
        </form>
    """

@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return f"Welcome, {username}! Account created with user_id={user.id}"

    if not user.check_password(password):
        return "Wrong password!"

    session["user_id"] = user.id
    return f"Logged in as {username} (user_id={user.id})"
