from flask import Blueprint, request, render_template, session, redirect, url_for
from app.api.openfood_api import fetch_product_by_barcode
from app.api.genAI_api import generate_evaluation
from app.models.pantry import Pantry
from app import db

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search():
    barcode = request.args.get("barcode")
    result = error = None

    if barcode:
        try:
            product = fetch_product_by_barcode(barcode)
            result = generate_evaluation(product, session.get("user_id"))
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template("search.html", result=result, error=error)

@search_bp.route("/search/add-to-pantry", methods=["POST"])
def add_to_pantry():
    if "user_id" not in session:
        return "Not logged in", 401

    pantry_item = Pantry(
        user_id=session["user_id"],
        product_name=request.form.get("product_name"),
        eco_score=request.form.get("eco_score"),
        score=request.form.get("health_score"),
        pros=request.form.get("pros"),
        cons=request.form.get("cons")
    )
    db.session.add(pantry_item)
    db.session.commit()

    return redirect(url_for("search.search"))
