import os
import openai
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

openai.api_key = api_key

def assign_categories_with_ai(nouns):
    """
    Uses GPT to categorize each noun into one of 13 predefined categories.
    Falls back to "Other" if categorization is unclear.
    Returns a list of tuples: (category, noun)
    """
    predefined_categories = [
        "Emotion", "Desire", "Sensation", "Imagination", "Intuition",
        "Will", "Attention", "Thought", "Memory", "Language",
        "Identity", "Decision-making", "Problem-solving"
    ]

    prompt = (
        "You are an AI classifier. Given a list of nouns, assign each to one of these 13 categories: "
        + ", ".join(predefined_categories) + ".\n"
        "If a noun cannot clearly fit into any, categorize it as 'Other'.\n"
        "Respond with a JSON list of tuples in the form: [\"Category\", \"Noun\"].\n"
        f"Nouns: {', '.join(nouns)}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        results = eval(content) if content.startswith("[") else []
        return results
    except Exception as e:
        print(f"Error categorizing nouns: {e}")
        return [("Error", noun) for noun in nouns]

# Optional: Utility function to filter 'Other' results for review
def collect_other_categories(results):
    return [noun for category, noun in results if category == "Other"]

