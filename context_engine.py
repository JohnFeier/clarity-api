import openai
import os
import json
from dotenv import load_dotenv

print("🧪 context_engine.py loaded...", flush=True)

load_dotenv()
print("🔑 .env loaded", flush=True)

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print("✅ OpenAI API key set", flush=True)
except Exception as e:
    print("❌ Failed to set OpenAI API key:", str(e), flush=True)

def generate_deepinsight_statement(variables):
    """
    Given a list of 2–3 user terms, this function forms 3-tiered conceptual prisms:
    Tier 1 = pairs (A∩B, B∩C, A∩C)
    Tier 2 = double pairs (ABBC, BCAC)
    Tier 3 = full triple (ABBCBCAC)
    """
    if not isinstance(variables, list) or len(variables) < 2:
        return {
            "summary_3": "Please enter at least two terms.",
            "summary_2": "",
            "summary_1": ""
        }

    variables = [v.strip().lower() for v in variables if v.strip()]
    A, B, C = (variables + ["", "", ""])[:3]  # 


    AB = f"{A} ∩ {B}"
    BC = f"{B} ∩ {C}"
    AC = f"{A} ∩ {C}"
    ABBC = f"{AB} ∩ {BC}"
    BCAC = f"{BC} ∩ {AC}"
    ABBCBCAC = f"{ABBC} ∩ {BCAC}"

    return {
        "summary_3": f"**Tier 1 – Specific Context**\n{AB}, {BC}, {AC}",
        "summary_2": f"**Tier 2 – Connecting Context**\n{ABBC}, {BCAC}",
        "summary_1": f"**Tier 3 – Profound Insight**\n{ABBCBCAC}"
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

        print("📤 Sending to OpenAI:\n", prompt, flush=True)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a philosophical summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )

        print("📥 OpenAI raw response:", response, flush=True)

        content = response['choices'][0]['message']['content'].strip()
        print("🧾 Extracted content:\n", content, flush=True)

        try:
            parsed = json.loads(content.replace("'", '"'))
            return {
                "summary_3": parsed.get("summary_3", "Error generating Tier 1"),
                "summary_2": parsed.get("summary_2", "Error generating Tier 2"),
                "summary_1": parsed.get("summary_1", "Error generating Tier 3")
            }
        except json.JSONDecodeError as parse_error:
            print("❌ JSON parsing error:", content, flush=True)
            return {
                "summary_3": "Error generating Tier 1",
                "summary_2": "Error generating Tier 2",
                "summary_1": "Error generating Tier 3"
            }

    except Exception as e:
        print("❌ GPT Summary Error:", str(e), flush=True)
        return {
            "summary_3": "Error generating Tier 1",
            "summary_2": "Error generating Tier 2",
            "summary_1": "Error generating Tier 3"
        }


