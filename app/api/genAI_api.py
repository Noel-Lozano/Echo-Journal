import os
from google import genai
from google.genai import types

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY is not set in the environment variables.")

client = genai.Client(api_key=GENAI_API_KEY)

system_message = types.GenerateContentConfig(system_instruction="You are an evaluator for food product health and sustainability.")

def build_prompt(product):
    return f"""
    You are an evaluator for food product health and sustainability.

    Below is a JSON dump from Open Food Facts, containing data on ingredients, nutrition, and environmental impact:

    {product.get("product", {})}

    Your task is to output **exactly three lines**, formatted as follows:

    1. A single letter (A–F) that represents the product's overall healthiness for the average consumer.
    2. One concise sentence stating the pros of the product. No prefixes or labels.
    3. One concise sentence stating the cons of the product. No prefixes or labels.

    If there is no meaningful pro or con, leave the line empty — but always output three lines only. Do not add any commentary or explanation before or after.
    """


def generate_evaluation(product):
    prompt = build_prompt(product)
    if not product.get("success", False):
        return f"Error fetching product: {product.get('error', 'Unknown error')}"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            config=system_message,
            contents=prompt,
        )
        lines = response.text.splitlines()
        print(f"Generated response: {lines}")
        return {
            "product_name": product.get("product", {}).get("product_name", "Unknown"),
            "eco_score": product.get("product", {}).get("ecoscore_score", "N/A"),
            "score": lines[0].strip(),
            "pros": lines[1].strip(),
            "cons": lines[2].strip()
        }
    
    except Exception as e:
        return f"Error generating evaluation: {str(e)}"
