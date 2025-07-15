from flask import Blueprint, request, jsonify
from app.api.openfood_api import fetch_product_by_barcode
from app.api.genAI_api import generate_evaluation

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["GET"])
def search_product():
    barcode = request.args.get("barcode")
    if not barcode:
        return jsonify({"error": "Barcode parameter is required"}), 400
    
    result = fetch_product_by_barcode(barcode)
    if not result["success"]:
        return jsonify({"error": result["error"]}), 404
    
    product = result["product"]

    product_clean = {
        "name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", "Unknown"),
        "nutriscore": product.get("nutriscore_grade", "Unknown"),
        "ecoscore": product.get("ecoscore_grade", "Unknown"),
        "ingredients": product.get("ingredients_text", ""),
        
    }

    ai_evaluation = generate_evaluation(product_clean)
    return jsonify({
        **product_clean, #unpacks the dictionary, same thing as writing the dictionary for product_clean
        "image": product.get("image_front_url", ""),
        "evaluation": ai_evaluation
    })