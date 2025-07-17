import os
from flask import session
from google import genai
from google.genai import types
from app.models.profile import Profile

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY is not set in the environment variables.")

client = genai.Client(api_key=GENAI_API_KEY)

system_message = types.GenerateContentConfig(system_instruction="You are an evaluator for food product health and sustainability.")

def get_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        return profile.text
    return None

def build_prompt(product, user_id=None):
    return f"""
    You are an evaluator for food product health and sustainability.

    Below is a JSON dump from Open Food Facts, containing data on ingredients, nutrition, and environmental impact:
    {product.get("product", {})}

    Here is the user's profile text, which may provide additional context for evaluation:
    {get_profile(user_id) or "No profile text available."}

    Your task is to output **exactly three lines**, without lines in between, formatted as follows:

    1. One line containing at most a few detailed but concise sentences, stating the pros of the product for the user given the profile text. Mention what parts are relevant to the user and why they are beneficial.
    2. One line containing at most a few detailed but concise sentences, stating the cons of the product for the user given the profile text. Mention what parts are relevant to the user and why they are detrimental.
    3. A single number (0-100) that represents the product's overall healthiness for the user, given the profile text.

    If there is no meaningful pro or con, leave the line empty — but always output three lines only, without lines in between. Do not add any commentary or explanation before or after.
    """


def generate_evaluation(product, user_id=None):
    prompt = build_prompt(product, user_id)
    if not product.get("success", False):
        return f"Error fetching product: {product.get('error', 'Unknown error')}"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            config=system_message,
            contents=prompt,
        )
        lines = response.text.splitlines()
        print(f"Generated response: {response.text}")
        return {
            "product_name": product.get("product", {}).get("product_name", "Unknown"),
            "eco_score": product.get("product", {}).get("ecoscore_score", "N/A"),
            "health_score": lines[2].strip(),
            "pros": lines[0].strip(),
            "cons": lines[1].strip()
        }
    
    except Exception as e:
        return f"Error generating evaluation: {str(e)}"
