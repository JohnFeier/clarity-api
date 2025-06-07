from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_deepinsight_statement(variables):
    if not isinstance(variables, list) or len(variables) < 2:
        return {
            "summary_3": "Please enter at least two terms.",
            "summary_2": "",
            "summary_1": ""
        }

    variables = [v.strip().lower() for v in variables if v.strip()]
    A, B, C = variables + ["", "", ""]  # pad for safety

    tier1 = [f"{A} ∩ {B}", f"{B} ∩ {C}", f"{A} ∩ {C}"]
    tier2 = [f"{A} ∩ {B} ∩ {C}"]
    tier3 = f"{A} ∩ {B} ∩ {C}"

    return {
        "summary_3": f"**Tier 1 – Specific Context**\n{', '.join(tier1)}",
        "summary_2": f"**Tier 2 – Connecting Context**\n{', '.join(tier2)}",
        "summary_1": f"**Tier 3 – Profound Insight**\n{tier3}"
    }

def rewrite_summary_with_gpt(deep_contexts):
    try:
        prompt = (
            "Rewrite the following context layers as poetic but insightful summaries. Keep Tier 1 specific, "
            "Tier 2 general, and Tier 3 philosophical or profound.\n\n"
            f"Tier 1: {deep_contexts['summary_3']}\n"
            f"Tier 2: {deep_contexts['summary_2']}\n"
            f"Tier 3: {deep_contexts['summary_1']}\n\n"
            "Respond in JSON:\n"
            "{ 'summary_3': '...', 'summary_2': '...', 'summary_1': '...' }"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a philosophical summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()
        return eval(content)  # assuming OpenAI returns clean JSON

    except Exception as e:
        print("❌ GPT Summary Error:", str(e))
        return {
            "summary_3": "Error generating Tier 1",
            "summary_2": "Error generating Tier 2",
            "summary_1": "Error generating Tier 3"
        }
