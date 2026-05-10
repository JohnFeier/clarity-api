import openai
import os

# Initialize API Key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- Radiant Signatures (Your Interpretive Lenses) ---
RADIANT_SIGNATURES = [
    {
        "name": "Mirror of Becoming",
        "perspective": "Internal",
        "time": "Present",
        "agency": "Emergent",
        "scale": "Meso",
        "emotion": "Hope",
        "modality": "Embodied",
        "logic": "Analogical"
    },
    {
        "name": "Ecliptic Memory",
        "perspective": "Meta",
        "time": "Past",
        "agency": "Passive",
        "scale": "Macro",
        "emotion": "Longing",
        "modality": "Conceptual",
        "logic": "Metaphorical"
    },
    {
        "name": "Catalyst Loop",
        "perspective": "External",
        "time": "Future",
        "agency": "Active",
        "scale": "Micro",
        "emotion": "Excitement",
        "modality": "Visual",
        "logic": "Causal"
    }
]

def run_radiance_engine(noun1, noun2, noun3, signature):
    """
    Synthesizes three nouns into a poetic insight using a specific signature.
    """
    prompt = f"""
    Interpret the relationship between the concepts **{noun1}**, **{noun2}**, and **{noun3}** 
    using the following interpretive lens:

    - Signature: {signature['name']}
    - Perspective: {signature['perspective']}
    - Time Orientation: {signature['time']}
    - Emotional Tone: {signature['emotion']}
    - Reasoning Style: {signature['logic']}

    Speak poetically, metaphorically, or archetypally. Structure your output in three short parts:
    1. A one-line metaphor.
    2. An expanded reflection.
    3. A philosophical implication.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Fast and efficient for poetic text
            messages=[
                {"role": "system", "content": "You are a poetic philosopher and master of metaphor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=350
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"🔥 Error in Radiance Engine: {str(e)}")
        return "The radiance is currently clouded. Please try again."