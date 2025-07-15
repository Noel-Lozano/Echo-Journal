import os
import google.generativeai as genai

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY is not set in the environment variables.")

genai.configure(api_key=GENAI_API_KEY)

def build_prompt(product):
    """
    Build the prompt for the Generative AI model for evaluating a food product.

    Args:
        product (dict): The product data containing details like name, brands, ingredients, etc.

    Returns:
        str: The constructed prompt for the Generative AI model.
    """
    return f"""
    You are a helpful nutrition and sustainability assistant.

    Analyze the following food product and provide a detailed evaluation:
    - Name: {product.get("name", "Unknown")}
    - Brand: {product.get("brands", "Unknown")}
    - Nutrition Score: {product.get("nutriscore_grade", "Unknown")}
    - Eco Score: {product.get("ecoscore_grade", "Unknown")}
    - Ingredients: {product.get("ingredients_text", "Not provided")}

    Generate the following:
    1. A list of **pros** of consuming this product (health and environmental benefits).
    2. A list of **cons** or concerns (e.g., unhealthy ingredients, environmental impact, allergens, poor sustainability).
    3. An **overall evaluation** or score (A-F) with a one-sentence reason.

    Keep the tone informative and format clearly with bullet points for pros and cons.
    """

def generate_evaluation(product):
    """ generate an evaluation for a food product using Generative AI """
    prompt = build_prompt(product)

    try:
        model = genai.Model("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text 
    
    except Exception as e:
        return f"Error generating evaluation: {str(e)}"
