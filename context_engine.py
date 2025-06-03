# context_engine.py — clean version

import re
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Load environment variables
dotenv_path = find_dotenv(raise_error_if_not_found=False)
if dotenv_path:
    print(f"DEBUG: Loaded .env from {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print("DEBUG: .env not found")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

client = OpenAI(api_key=api_key)
def noun_mixer(variables):
    """
    Given a list of variables (nouns), compares each adjacent pair
    and returns a synthesized result based only on commonalities.
    """
    if not isinstance(variables, list) or len(variables) < 2:
        return "Please provide at least two variables."

    result = []
    for i in range(len(variables)):
        a = variables[i]
        b = variables[(i + 1) % len(variables)]  # Circular adjacency
        common = find_common_substring(a, b)
        if common:
            result.append(common)

    return " ".join(result) if result else "No commonalities found."

def find_common_substring(a, b):
    longest = ""
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            substr = a[i:j]
            if substr in b and len(substr) > len(longest):
                longest = substr
    return longest.strip()

def generate_prompt(levels):
    context = f"{levels['level1']}, {levels['level2']}, {levels['level3']}"
    return (
        "Please summarize the following context into three levels:\n"
        "Level 1: 3-sentence version\n"
        "Level 2: 2-sentence version\n"
        "Level 3: 1-sentence version\n\n"
        f"Context: {context}"
    )

def strip_html(text):
    if text:
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', text)).strip()
    return ""

def rewrite_summary_with_gpt(levels):
    prompt = generate_prompt(levels)
    response = client.chat.completions.create(
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
    """
    Generates a deep insight statement from a list of noun variables
    using circular adjacency and commonality extraction.
    """
    raw = noun_mixer(variables)
    return {"level1": raw, "level2": raw, "level3": raw}
from flask import Flask, request, jsonify
from noun_mixer import assign_categories

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_input():
    data = request.get_json()
    input_nouns = data.get('nouns', [])
    clarity_mode = data.get('clarity_mode', 'tiered')

    if not input_nouns or not isinstance(input_nouns, list):
        return jsonify({'error': 'Please provide a list of input nouns.'}), 400

    # Placeholder logic — update to call your insight generation functions
    results = generate_deepinsight_statement(input_nouns)
    return jsonify(results)


