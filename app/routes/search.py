from flask import Blueprint, request, render_template_string, session, redirect, url_for
from app.api.openfood_api import fetch_product_by_barcode
from app.api.genAI_api import generate_evaluation
from app.models.pantry import Pantry
from app import db

search_bp = Blueprint("search", __name__)

HTML_TEMPLATE = """
<!doctype html>
<title>Product Evaluation</title>
<h2>Barcode Search</h2>
<form method="GET" action="/search">
    <input type="text" name="barcode" placeholder="Enter barcode" required>
    <button type="submit">Submit</button>
</form>

{% if result %}
    <h3>Result</h3>
    <ul>
        <li><strong>Product Name:</strong> {{ result.product_name }}</li>
        <li><strong>Eco Score:</strong> {{ result.eco_score }}</li>
        <li><strong>Score:</strong> {{ result.score }}</li>
        <li><strong>Pros:</strong> {{ result.pros }}</li>
        <li><strong>Cons:</strong> {{ result.cons }}</li>
    </ul>
    <form method="POST" action="/search/add-to-pantry">
        <input type="hidden" name="product_name" value="{{ result.product_name }}">
        <input type="hidden" name="eco_score" value="{{ result.eco_score }}">
        <input type="hidden" name="score" value="{{ result.score }}">
        <input type="hidden" name="pros" value="{{ result.pros }}">
        <input type="hidden" name="cons" value="{{ result.cons }}">
        <button type="submit">Add to Pantry</button>
    </form>
{% elif error %}
    <p style="color: red;">{{ error }}</p>
{% endif %}
"""

@search_bp.route("/search", methods=["GET"])
def search():
    barcode = request.args.get("barcode")
    result = error = None

    if barcode:
        try:
            product = fetch_product_by_barcode(barcode)
            result = generate_evaluation(product)
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template_string(HTML_TEMPLATE, result=result, error=error)

@search_bp.route("/search/add-to-pantry", methods=["POST"])
def add_to_pantry():
    if "user_id" not in session:
        return "Not logged in", 401

    pantry_item = Pantry(
        user_id=session["user_id"],
        product_name=request.form.get("product_name"),
        eco_score=request.form.get("eco_score"),
        score=request.form.get("score"),
        pros=request.form.get("pros"),
        cons=request.form.get("cons")
    )
    db.session.add(pantry_item)
    db.session.commit()

    return redirect(url_for("search.search"))
