import openai
import os
from typing import List, Tuple

openai.api_key = os.environ.get("OPENAI_API_KEY")

NounTriplet = Tuple[str, str, str]

# --- Radiant Signatures ---
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

# --- Preprocessing ---
def preprocess_nouns(a: str, b: str, c: str):
    pairs = [(a, b), (b, c), (a, c)]
    triplet = (a, b, c)
    return pairs, triplet

# --- Clarity Logic (stub) ---
def literal_intersection(noun_pair: Tuple[str, str]) -> str:
    return f"Intersection of '{noun_pair[0]}' and '{noun_pair[1]}'"

def synthesize_clarity_summary(a_b, b_c, a_c, abc) -> dict:
    return {
        "Tier 1": abc,
        "Tier 2": [a_b, b_c, a_c],
        "Tier 3": f"Broader context from A+B+C: {abc}"
    }

def clarity_engine(pairs: List[Tuple[str, str]], triplet: NounTriplet) -> dict:
    a_b = literal_intersection(pairs[0])
    b_c = literal_intersection(pairs[1])
    a_c = literal_intersection(pairs[2])
    abc = literal_intersection(triplet)
    return synthesize_clarity_summary(a_b, b_c, a_c, abc)

# --- Radiance Logic ---
def synthesize_radiant_insight(triplet: NounTriplet, signature: dict) -> dict:
    prompt = f"""
Interpret the relationship between the concepts **{triplet[0]}**, **{triplet[1]}**, and **{triplet[2]}**
using the following interpretive lens:

- Perspective: {signature['perspective']}
- Time Orientation: {signature['time']}
- Agency: {signature['agency']}
- Scale: {signature['scale']}
- Emotional Tone: {signature['emotion']}
- Modality: {signature['modality']}
- Reasoning Style: {signature['logic']}

Speak poetically, metaphorically, or archetypally. Structure your output in three tiers:
1. A one-line metaphor
2. An expanded reflection
3. A philosophical implication
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a poetic philosopher."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=300
        )
        full_output = response['choices'][0]['message']['content']
        return {
            "Signature Name": signature.get("name", "Unnamed Signature"),
            "Prompt Used": prompt,
            "Radiant Output": full_output.strip()
        }

    except Exception as e:
        print("🔥 Error in Radiance GPT call:", str(e), flush=True)
        return {
            "error": "Radiance failed to generate insight.",
            "exception": str(e)
        }

def radiance_engine(triplet: NounTriplet, signature: dict) -> dict:
    return synthesize_radiant_insight(triplet, signature)

# --- Run Both Engines ---
def run_engines(a: str, b: str, c: str, signature: dict) -> dict:
    pairs, triplet = preprocess_nouns(a, b, c)
    clarity_output = clarity_engine(pairs, triplet)
    radiance_output = radiance_engine(triplet, signature)
    return {
        "Clarity": clarity_output,
        "Radiance": radiance_output
    }



