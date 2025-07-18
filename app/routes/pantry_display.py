from app.models.pantry import Pantry
from flask import render_template, Blueprint, session, jsonify
from sqlalchemy import cast, Integer
from app.api.genAI_api import generate_pantry_recommendations
from app.models.users import User

pantry_bp = Blueprint("pantry", __name__)

@pantry_bp.route("/pantry")
def show_pantry():
    user_id = session.get("user_id")

    if not user_id:
        return "Unauthorized", 401
    user = User.query.get(user_id)
    eco_sort = Pantry.query.filter_by(user_id=user_id).order_by(cast(Pantry.eco_score, Integer).desc()).all()
    grade_sort = Pantry.query.filter_by(user_id=user_id).order_by(cast(Pantry.score, Integer).desc()).all()
    
    # Generate recommendations on page load
    recommendations = "No recommendations available."

    return render_template("private_pantry.html", 
                         eco_sort=eco_sort, 
                         grade_sort=grade_sort,
                         recommendations=recommendations,
                         user=user)

@pantry_bp.route("/pantry/generate_recommendations", methods=["POST"])
def generate_recommendations():
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    recommendations = generate_pantry_recommendations(user_id)
    
    return jsonify({"recommendations": recommendations})