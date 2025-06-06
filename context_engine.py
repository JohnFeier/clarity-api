import os
import re
import openai
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, jsonify
from noun_mixer import assign_categories_with_ai, collect_other_categories

# Load environment variables
load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

openai.api_key = api_key

app = Flask(__name__)

def strip_html(text):
    if text:
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text)).strip()
    return ""
def generate_prompt(levels):
    context = f"{levels['level1']}, {levels['level2']}, {levels['level3']}"
    return (
        "You are an AI trained to detect conceptual overlap between abstract or socially relevant ideas.\n"
        "Given three input terms, do not analyze them individually. Instead, synthesize a shared meaning or theme that unites all three.\n"
        "Avoid generic abstractions like 'essence' or 'reflection'. Focus on concrete, real-world or psychologically meaningful commonalities.\n"
        "This is part of a system to help people explore hidden layers of meaning in everyday life.\n\n"
        f"Input terms: {context}\n\n"
        "Respond with exactly three tiers:\n"
        "Level 1: A deep 3-sentence explanation of what unites these concepts.\n"
        "Level 2: A sharper 2-sentence summary.\n"
        "Level 3: A one-sentence insight that captures the shared truth.\n\n"
        "Example of style: If the words were 'protest', 'art', and 'therapy', a good Level 3 might be: 'All three are channels for transforming inner tension into outward expression.'\n\n"
        "Now generate your three-tier output."
    )
def rewrite_summary_with_gpt(levels):
    prompt = generate_prompt(levels)
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    content = response.choices[0].message.content.strip()

    match1 = re.search(r"Level 1:\s*(.+?)\nLevel 2:", content, re.DOTALL)
    match2 = re.search(r"Level 2:\s*(.+?)\nLevel 3:", content, re.DOTALL)
    match3 = re.search(r"Level 3:\s*(.+)", content, re.DOTALL)

    return {
        "summary_3": strip_html(match1.group(1)) if match1 else "Could not parse Level 1",
        "summary_2": strip_html(match2.group(1)) if match2 else "Could not parse Level 2",
        "summary_1": strip_html(match3.group(1)) if match3 else "Could not parse Level 3"
    }

def generate_deepinsight_statement(variables):
    categorized = assign_categories_with_ai(variables)
    other = collect_other_categories(categorized)
    print("DEBUG - 'Other' category terms:", other)

    just_nouns = [noun for _, noun in categorized]
    combined = " ".join(just_nouns)

    return {
        "level1": combined,
        "level2": combined,
        "level3": combined
    }

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        variables = data.get('variables', [])
        if not variables:
            return jsonify({"error": "No variables provided."}), 400

        levels = generate_deepinsight_statement(variables)
        summary = rewrite_summary_with_gpt(levels)

        return jsonify({
            "summary_3": summary.get("summary_3", "Error generating 3-sentence summary."),
            "summary_2": summary.get("summary_2", "Error generating 2-sentence summary."),
            "summary_1": summary.get("summary_1", "Error generating 1-sentence summary.")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


