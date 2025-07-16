import os
import google.generativeai as genai

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY is not set in the environment variables.")

genai.configure(api_key=GENAI_API_KEY)

def build_prompt(product):
    return f"""
    You are a helpful nutrition and sustainability assistant.

    Here is data about the user:

    What follows is a dump of a food product's data from Open Food Facts.
    It contains information about the product's ingredients, nutritional values, and environmental impact.

    Generate a response with the following structure:
    1. The first line is a score (A-F) based on the product's healthiness for the user specifically.
    2. The next six lines are pros and cons of the product:
       - Pros: List the top 3 positive aspects of the product.
       - Cons: List the top 3 negative aspects of the product.
    3. If you have less than 3 pros or cons, leave those lines blank. However there should always be 6 lines after the score.

    {product.get("product", {})}
    """

def generate_evaluation(product):
    prompt = build_prompt(product)
    if not product.get("success", False):
        return f"Error fetching product: {product.get('error', 'Unknown error')}"

    try:
        model = genai.Model("gemini-2.0-flash-lite")
        response = model.generate_content(prompt)
        lines = response.text.splitlines()
        return {
            "eco_score": product.get("product", {}).get("ecoscore_score", "N/A"),
            "score": lines[0].strip(),
            "pros": [line.strip() for line in lines[1:4]],
            "cons": [line.strip() for line in lines[4:7]]
        }
    
    except Exception as e:
        return f"Error generating evaluation: {str(e)}"
