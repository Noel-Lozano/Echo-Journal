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

    Your task is to output **exactly three lines**, separated by a single newline, and nothing else. The required format is:

    1. The first line: At most a few detailed but concise sentences, stating the pros of the product for the user given the profile text. Mention what parts are relevant to the user and why they are beneficial. Do NOT include any prefix like "Pros:".
    2. The second line: At most a few detailed but concise sentences, stating the cons of the product for the user given the profile text. Mention what parts are relevant to the user and why they are detrimental. Do NOT include any prefix like "Cons:".
    3. The third line: A single integer between 0 and 100 (inclusive) representing the product's overall healthiness for the user, given the profile text. This line must contain ONLY the number, with no extra text, units, or symbols.

    If there is no meaningful pro or con, leave the line empty — but always output three lines only, separated by a single newline, and nothing else. Do not add any commentary, explanation, or extra lines before or after.

    Example output:
    This product is high in fiber and low in sugar, which is beneficial for digestive health and weight management.
    Contains artificial additives and a high sodium content, which may not be suitable for people with hypertension.
    72
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

        # Parse eco_score as number or None
        raw_eco = product.get("product", {}).get("ecoscore_score", None)
        try:
            eco_score = float(raw_eco)
        except (TypeError, ValueError):
            eco_score = None

        # Parse health_score as number or None
        raw_health = lines[2].strip() if len(lines) > 2 else None
        try:
            health_score = int(raw_health)
        except (TypeError, ValueError):
            try:
                health_score = float(raw_health)
            except (TypeError, ValueError):
                health_score = None

        return {
            "product_name": product.get("product", {}).get("product_name", "Unknown"),
            "eco_score": eco_score,
            "health_score": health_score,
            "pros": lines[0].strip() if len(lines) > 0 else "",
            "cons": lines[1].strip() if len(lines) > 1 else ""
        }
    
    except Exception as e:
        return f"Error generating evaluation: {str(e)}"
    
def generate_pantry_recommendations(user_id):
    """Generate healthier recommendations for entire pantry"""

    pantry_items = Pantry.query.filter_by(user_id=user_id).all()

    if not pantry_items:
        return []

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
        Please provide 4-5 specific healthier food recommendations that would improve this user's pantry. Return your response as a JSON array, where each element is an object with two fields: 'recommendation' (the food or change to make) and 'reason' (a concise sentence explaining why, no prefix). Example:
        [
          {{"recommendation": "Add more leafy greens", "reason": "Leafy greens are high in fiber and vitamins."}},
          {{"recommendation": "Replace sugary snacks with nuts", "reason": "Nuts provide healthy fats and protein."}}
        ]
        Do not include any commentary, explanation, or text before or after the JSON. Only output the JSON array.
        Focus on:
        - Replacing less healthy items with better alternatives
        - Adding missing nutritional components
        - Considering the user's profile and dietary needs
        - Suggesting specific brands or types when possible
        """

    try:
        response = client.models.generate_content(
            model="gemma-3n-e4b-it",
            contents=prompt,
        )
        import json
        text = response.text.strip()
        # Remove markdown code block if present
        if text.startswith('```'):
            lines = text.splitlines()
            # Remove first and last line if they are code block markers
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            text = '\n'.join(lines).strip()
        try:
            recommendations = json.loads(text)
            if isinstance(recommendations, list):
                return recommendations
            else:
                return []
        except Exception:
            # fallback: return empty list if not valid JSON
            return []

    except Exception as e:
        return []
