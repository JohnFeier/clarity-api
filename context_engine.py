import openai
import os
import json
from dotenv import load_dotenv

print("🧪 context_engine.py loaded...", flush=True)

# Load environment variables
load_dotenv()
print("🔑 .env loaded", flush=True)

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print("✅ OpenAI API key set", flush=True)
except Exception as e:
    print("❌ Failed to set OpenAI API key:", str(e), flush=True)


def get_synthesis(term1, term2, depth_level):
    """
    The 'Chewing' Mechanism: 
    This function makes the actual call to OpenAI for each pair.
    """
    if depth_level == 1:
        role_description = "Identify the most fundamental shared characteristic between these two nouns."
    elif depth_level == 2:
        role_description = "Synthesize these two conceptual themes into a single, deeper proto-idea."
    else:
        role_description = "Distill these proto-ideas into one final, universal 'Fundamental Force'."

    prompt = f"{role_description} Context: '{term1}' and '{term2}'. Output only one concise, profound sentence."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Using 4o for better reasoning
            messages=[
                {"role": "system", "content": "You are Clarity, the sister of logic. You strip away matter to find the underlying forces of the universe."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error in synthesis: {e}")
        return "Connection pending..."

def run_clarity_funnel(variables):
    """
    The full Logic Funnel. This replaces both old functions.
    """
    if not isinstance(variables, list) or len(variables) < 3:
        return {"error": "Three nouns are required for full synthesis."}

    # Clean the inputs
    A, B, C = [v.strip() for v in variables[:3]]

    # --- Tier 1: The Base ---
    ab = get_synthesis(A, B, 1)
    bc = get_synthesis(B, C, 1)
    ac = get_synthesis(A, C, 1)
    
    # --- Tier 2: The Bridge ---
    abbc = get_synthesis(ab, bc, 2)
    bcac = get_synthesis(bc, ac, 2)
    
    # --- Tier 3: The Proto-Idea ---
    proto_idea = get_synthesis(abbc, bcac, 3)
    
    return {
        "tier_1": {"ab": ab, "bc": bc, "ac": ac},
        "tier_2": {"abbc": abbc, "bcac": bcac},
        "tier_3": proto_idea
    }
