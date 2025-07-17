import os
from flask import session
from google import genai
from google.genai import types
from app.models.profile import Profile
from app.models.pantry import Pantry

GENAI_API_KEY = os.environ.get("GENAI_API_KEY")
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

    1. One line containing at most a few detailed but concise sentences, stating the pros of the product for the user given the profile text. Mention what parts are relevant to the user and why they are beneficial. Do not include any prefix like "Pros:".
    2. One line containing at most a few detailed but concise sentences, stating the cons of the product for the user given the profile text. Mention what parts are relevant to the user and why they are detrimental. Do not include any prefix like "Cons:".
    3. A single number (0-100) that represents the product's overall healthiness for the user, given the profile text.

    If there is no meaningful pro or con, leave the line empty — but always output three lines only, without lines in between. Do not add any commentary or explanation before or after.
    """


def generate_evaluation(product, user_id=None):
    prompt = build_prompt(product, user_id)
    if not product.get("success", False):
        return f"Error fetching product: {product.get('error', 'Unknown error')}"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=system_message,
            contents=prompt,
        )
        lines = response.text.splitlines()

        return {
            "product_name": product.get("product", {}).get("product_name", "Unknown"),
            "eco_score": product.get("product", {}).get("ecoscore_score", "N/A"),
            "health_score": lines[2].strip(),
            "pros": lines[0].strip(),
            "cons": lines[1].strip()
        }
    
    except Exception as e:
        return f"Error generating evaluation: {str(e)}"
    
def generate_pantry_recommendations(user_id):
    """Generate healthier recommendations for entire pantry"""

    pantry_items = Pantry.query.filter_by(user_id=user_id).all()

    if not pantry_items:
        return "No pantry items found."

    pantry_data = ""
    for item in pantry_items:
        pantry_data += f"""
    Product: {item.product_name}
    Eco Score: {item.eco_score}
    Health Score: {item.score}
    Pros: {item.pros}
    Cons: {item.cons}
    ---
    """

        profile_text = get_profile(user_id) or "No specific dietary preferences or restrictions mentioned."

        prompt = f"""
    You are a nutritionist and health expert. Based on the user's pantry contents below, provide healthier food recommendations.
    User Profile: {profile_text}
    Current Pantry Contents:
    {pantry_data}
    Please provide 4-5 specific healthier food recommendations that would improve this user's pantry. For each recommendation, format it exactly as follows and add a new line between each recommendation:
    RECOMMENDATION: [Specific product name or food category]
    REASON 1: [One specific health or sustainability benefit]
    REASON 2: [Another specific benefit related to the user's profile or pantry gaps]
    Focus on:
    - Replacing less healthy items with better alternatives
    - Adding missing nutritional components
    - Considering the user's profile and dietary needs
    - Suggesting specific brands or types when possible
    Keep each reason to one concise sentence.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are a nutritionist providing personalized food recommendations."
            ),
            contents=prompt,
        )
        return response.text

    except Exception as e:
        return f"Error generating recommendations: {str(e)}"
