from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
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

    return render_template("private_search.html", result=result, error=error)

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

# New API endpoint for AJAX barcode search
@search_bp.route("/search/api/barcode", methods=["POST"])
def search_api_barcode():
    data = request.get_json()
    barcode = data.get("barcode")
    if not barcode:
        return jsonify({"error": "No barcode provided."}), 400
    try:
        product = fetch_product_by_barcode(barcode)
        result = generate_evaluation(product, session.get("user_id"))
        # If result is a string and contains 'Error fetching product', show a user-friendly message
        if isinstance(result, str):
            if result.startswith("Error fetching product"):
                return jsonify({"error": "Product invalid or not found."}), 404
            return jsonify({"error": result}), 500
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": "Product invalid or not found."}), 500

@search_bp.route("/search/api/add-to-pantry", methods=["POST"])
def add_to_pantry_api():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    pantry_item = Pantry(
        user_id=session["user_id"],
        product_name=data.get("product_name"),
        eco_score=data.get("eco_score"),
        score=data.get("health_score"),
        pros=data.get("pros"),
        cons=data.get("cons")
    )
    db.session.add(pantry_item)
    db.session.commit()
    return jsonify({"success": True, "message": "Element added to pantry."})
