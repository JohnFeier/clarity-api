import openai
import os

# Make sure your API key is loaded
openai.api_key = os.environ.get("OPENAI_API_KEY")

def synthesize_radiant_insight(triplet: tuple, signature: dict) -> dict:
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
            model="gpt-4",  # or "gpt-3.5-turbo" if you're managing cost/speed
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