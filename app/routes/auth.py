from flask import Blueprint, request, session, redirect, render_template
from app.models.users import db, User
from app.models.profile import Profile
from datetime import datetime
from app.models.pantry import Pantry

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET"])
def home():
    return render_template("public_home.html")

@auth_bp.route("/login", methods=["GET"])
def login_form():
    return render_template("public_login.html")

@auth_bp.route("/check-password", methods=["POST"])
def check_password():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return {"valid": False, "error": "Missing username or password."}, 400
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return {"valid": False, "error": "Invalid username or password."}
    return {"valid": True}

@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    # Check if username exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return render_template("public_login.html", error="Username does not exist.")
    # Check password
    if not user.check_password(password):
        return render_template("public_login.html", error="Incorrect password.")

    session["user_id"] = user.id
    return redirect("/dashboard")

@auth_bp.route("/signup", methods=["GET"])
def signup_form():
    return render_template("public_signup.html")

@auth_bp.route("/signup", methods=["POST"])
def signup():
    # Deprecated: multi-step signup is now used
    return {"error": "This endpoint is deprecated. Use the multi-step signup."}, 410

@auth_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    user = db.session.get(User, session["user_id"])
    pantry_items = Pantry.query.filter_by(user_id=user.id).all()
    pantry_count = len(pantry_items)
    
    def safe_float(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None
    eco_scores = [safe_float(item.eco_score) for item in pantry_items]
    eco_scores = [score for score in eco_scores if score is not None]
    avg_eco_score = round(sum(eco_scores) / len(eco_scores), 2) if eco_scores else None
    
    scores = [safe_float(item.score) for item in pantry_items]
    scores = [score for score in scores if score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None
    
    return render_template(
        "private_dashboard.html",
        user=user,
        pantry_count=pantry_count,
        avg_eco_score=avg_eco_score,
        avg_score=avg_score
    )

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")

@auth_bp.route("/check-username", methods=["POST"])
def check_username():
    username = request.json.get("username")
    if not username:
        return {"taken": False}, 400
    exists = User.query.filter_by(username=username).first() is not None
    return {"taken": exists}

@auth_bp.route("/complete-signup", methods=["POST"])
def complete_signup():
    from app.models.profile import Profile
    from datetime import datetime
    import traceback
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    preferences = data.get("preferences")
    photo = data.get("photo")
    if not username or not password:
        return {"success": False, "error": "Missing username or password."}, 400
    if User.query.filter_by(username=username).first():
        return {"success": False, "error": "Username already exists."}, 400
    try:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        profile = Profile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            preferences=preferences,
            photo=photo,
            date_joined=datetime.utcnow()
        )
        db.session.add(profile)
        db.session.commit()
        session["user_id"] = user.id
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        print("Signup error:", e)
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}, 500