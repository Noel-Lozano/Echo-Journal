import os
from google import genai
from google.genai import types

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY is not set in the environment variables.")

client = genai.Client(api_key=GENAI_API_KEY)

system_message = types.GenerateContentConfig(system_instruction="You are a helpful nutrition and sustainability assistant.")

def build_prompt(product):
    return f"""
    Here is data about the user:

    What follows is a dump of a food product's data from Open Food Facts.
    It contains information about the product's ingredients, nutritional values, and environmental impact.

    Generate a response with the following structure:
    1. The first line is a score (A-F) based on the product's healthiness for the user specifically.
    2. The second line is a sentence about the pros of the product. No prefix, just the sentence.
    3. The third line is a sentence about the cons of the product. No prefix, just the sentence.
    Both lines should be concise and informative. Leave the line blank if there is no information to provide, but always contain three lines.

    {product.get("product", {})}
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
        return {
            "eco_score": product.get("product", {}).get("ecoscore_score", "N/A"),
            "score": lines[0].strip(),
            "pros": lines[1].strip(),
            "cons": lines[2].strip()
        }
    
    except Exception as e:
        return f"Error generating evaluation: {str(e)}"
