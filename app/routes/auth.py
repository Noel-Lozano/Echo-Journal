from flask import Blueprint, request, session, redirect, render_template
from app.models.users import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@auth_bp.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return "Invalid credentials!"

    session["user_id"] = user.id
    return redirect("/dashboard")

@auth_bp.route("/signup", methods=["GET"])
def signup_form():
    return render_template("signup.html")

@auth_bp.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]

    if User.query.filter_by(username=username).first():
        return "User already exists! Please Login."

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    return redirect("/dashboard")

@auth_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    user = db.session.get(User, session["user_id"])
    return render_template("dashboard.html", username=user.username)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")