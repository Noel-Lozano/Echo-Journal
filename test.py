from app.api.genAI_api import generate_evaluation, build_prompt
from app.api.openfood_api import fetch_product_by_barcode


if __name__ == "__main__":
    barcode = "5449000054227"

    product = fetch_product_by_barcode(barcode)
    # print(f"Product data for barcode {barcode}: {product}")
    prompt = build_prompt(product)
    print(f"Prompt for Generative AI:\n{prompt}")