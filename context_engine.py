import os
import re
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from noun_mixer import assign_categories_with_ai, collect_other_categories

# Load environment variables
load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

client = OpenAI(api_key=api_key)

def strip_html(text):
    if text:
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text)).strip()
    return ""

def rewrite_summary_with_gpt(input_string):
    prompt = f"""
You are a context synthesis engine trained to extract insight from patterns.

Given the following terms:
{input_string}

Organize your response into three tiers:

**Tier 1 – Specific Context**  
List the concrete overlaps or issues these terms highlight. Think in terms of lived experience, law, psychology, social patterns, or cultural markers. Be precise and grounded.

**Tier 2 – Connecting Context**  
Describe the invisible thread—what structures, tensions, or transitions do these terms point to? How does the specific become the general?

**Tier 3 – Profound Insight**  
End with a distilled insight or truth that emerges from these connections. Make it resonant and reflective—but never poetic fluff. Stay sharp.

Avoid metaphysical language. This is for serious, clear-headed use by AI and humans alike.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You synthesize insights from term clusters into structured tiers of context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.6
        )
        rewritten = response.choices[0].message.content.strip()
        sections = rewritten.split("\n\n")
        return {
            "summary_3": sections[0] if len(sections) > 0 else "",
            "summary_2": sections[1] if len(sections) > 1 else "",
            "summary_1": sections[2] if len(sections) > 2 else "",
        }

    except Exception as e:
        return {
            "summary_3": f"Error generating summary: {str(e)}",
            "summary_2": "",
            "summary_1": ""
        }

def generate_deepinsight_statement(variables):
    categorized = assign_categories_with_ai(variables)
    other = collect_other_categories(categorized)
    print("DEBUG - 'Other' category terms:", other)

    just_nouns = [noun for _, noun in categorized]
    combined = " ".join(just_nouns)

    return combined
