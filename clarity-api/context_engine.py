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


def generate_deepinsight_statement(variables):
    """
    Given a list of 2–3 user terms, this function forms a structured context model:
    Tier 1 = base pairwise intersections (A∩B, B∩C, A∩C)
    Tier 2 = composite double pairs (AB ∩ BC, BC ∩ AC)
    Tier 3 = full triple combination (AB ∩ BC ∩ AC)
    """
    if not isinstance(variables, list) or len(variables) < 2:
        return {
            "summary_3": "Please enter at least two terms.",
            "summary_2": "",
            "summary_1": ""
        }

    variables = [v.strip().lower() for v in variables if v.strip()]
    A, B, C = (variables + ["", "", ""])[:3]

    AB = f"{A} ∩ {B}"
    BC = f"{B} ∩ {C}"
    AC = f"{A} ∩ {C}"
    ABBC = f"{AB} ∩ {BC}"
    BCAC = f"{BC} ∩ {AC}"
    ABBCBCAC = f"{ABBC} ∩ {BCAC}"

    return {
        "intersection_ab": AB,
        "intersection_bc": BC,
        "intersection_ac": AC,
        "intersection_abc": ABBCBCAC
    }


def rewrite_summary_with_gpt(intersections):
    import openai
    from os import getenv
    import json

    openai.api_key = getenv("OPENAI_API_KEY")

    # Extract intersections
    ab = intersections.get("intersection_ab", "")
    bc = intersections.get("intersection_bc", "")
    ac = intersections.get("intersection_ac", "")
    abc = intersections.get("intersection_abc", "")

    prompt = f"""
Given the following intersecting concepts:
- A ∩ B: {ab}
- B ∩ C: {bc}
- A ∩ C: {ac}
- A ∩ B ∩ C: {abc}

Write three tiers of insight based on these:

Tier One Context (summary_1):
- Write exactly **three sentences**.
- Each sentence should describe one of the pairwise intersections (A∩B, B∩C, A∩C).
- Be clear, direct, and insightful.

Tier Two Context (summary_2):
- Write exactly **two sentences**.
- Each sentence should describe what happens when two of the pairwise intersections are combined.

Tier Three Context (summary_3):
- Write exactly **one sentence**.
- It should express the core insight that unites all three concepts.

Respond only with a valid JSON object using double quotes. Format it exactly like this:
{{
  "summary_1": "...",
  "summary_2": "...",
  "summary_3": "..."
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a structured assistant that writes deep but clear insights. Output only the JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=500
    )

    raw_output = response["choices"][0]["message"]["content"]

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("❌ JSON parsing failed. Raw output:", raw_output, flush=True)
        return {
            "summary_1": "Error generating Tier 1",
            "summary_2": "Error generating Tier 2",
            "summary_3": "Error generating Tier 3"
        }
