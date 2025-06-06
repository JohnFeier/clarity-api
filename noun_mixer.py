import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(find_dotenv())

# Set up the OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")
client = OpenAI(api_key=api_key)

# Predefined conceptual categories
CATEGORIES = {
    "Parenting": ["mother", "father", "child", "baby", "unwed", "parent"],
    "Substance": ["cannabis", "alcohol", "cocaine", "drug", "weed"],
    "Culture": ["music", "art", "film", "social", "distortion", "punk"],
    # Add more categories as needed
}

def assign_categories_with_ai(terms):
    results = []
    for term in terms:
        try:
            prompt = (
                f"What is the best high-level category for the term '{term}'?\n"
                f"Choose from: {', '.join(CATEGORIES.keys())}.\n"
                "Respond with only the category name."
            )
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You categorize terms by their general concept."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            category = response.choices[0].message.content.strip()
            results.append((category, term))
        except Exception as e:
            print("Error categorizing nouns:", str(e))
            results.append(("Other", term))
    return results

def collect_other_categories(categorized_list):
    return [term for cat, term in categorized_list if cat == "Other"]
