from app.models.pantry import Pantry
from flask import render_template, Blueprint, session


pantry_bp = Blueprint("pantry", __name__)


@pantry_bp.route("/pantry")
def show_pantry():
    user_id = session.get("user_id")

    if not user_id:
        return "Unauthorized", 401
    
    eco_sort = Pantry.query.filter_by(user_id=user_id).order_by(Pantry.eco_score.desc()).all()
    grade_sort = Pantry.query.filter_by(user_id=user_id).order_by(Pantry.score.desc()).all()

    return render_template("pantry.html", eco_sort=eco_sort, grade_sort=grade_sort)
