import requests

OPENFOODFACTS_BASE_URL = "https://world.openfoodfacts.org/api/v2/product/"

def fetch_product_by_barcode(barcode):
    url = f"{OPENFOODFACTS_BASE_URL}{barcode}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == 1:
            return {
                "success": True,
                "product": data.get("product", {})
            }
        else:
            return {
                "success": False,
                "error": f"No product found for barcode {barcode}"
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"API error: {str(e)}"
        }

