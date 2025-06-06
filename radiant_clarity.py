from flask import Flask, request, jsonify
from noun_mixer import assign_categories
import json
import os

app = Flask(__name__)

# Load clarity memory map from file
CLARITY_MAP_FILE = os.path.join(os.path.dirname(__file__), 'clarity_map.json')
if os.path.exists(CLARITY_MAP_FILE):
    with open(CLARITY_MAP_FILE, 'r') as f:
        clarity_memory = json.load(f)
else:
    clarity_memory = {}

def synthesize_phrase(category_a, category_b):
    key = f"{category_a}+{category_b}"
    if key in clarity_memory:
        return clarity_memory[key]['summary']
    elif category_a == category_b:
        return f"Deepening {category_a.lower()}"
    return f"{category_a} shaped by {category_b.lower()}"

def generate_tiers(categories):
    tier_1 = []
    tier_2 = []
    tier_3 = []
    core_four = []

    # Tier 1: All 13x13 = 169 combinations
    for a in categories:
        for b in categories:
            phrase = synthesize_phrase(a, b)
            tier_1.append(phrase)

    # Tier 2: Filtered ~42
    seen = set()
    for phrase in tier_1:
        if phrase not in seen:
            seen.add(phrase)
            tier_2.append(phrase)
        if len(tier_2) >= 42:
            break

    # Tier 3: Refined ~11
    tier_3 = [tier_2[i] for i in range(0, len(tier_2), 4)][:11]

    # Core Four: Final distilled truths ~4
    core_four = tier_3[:4]

    return {
        'Tier One Context': tier_1,
        'Tier Two Context': tier_2,
        'Tier Three Context': tier_3,
        'Core Four': core_four
    }

@app.route('/process', methods=['POST'])
def process_input():
    data = request.get_json()
    input_nouns = data.get('nouns', [])
    clarity_mode = data.get('clarity_mode', 'tiered')  # default mode

    if not input_nouns or not isinstance(input_nouns, list):
        return jsonify({'error': 'Please provide a list of input nouns.'}), 400

    categorized = assign_categories(input_nouns)
    categories = [cat for cat, _ in categorized]

    if clarity_mode == 'insight_braid' and len(categories) >= 4:
        pair1_key = f"{categories[0]}+{categories[1]}"
        pair2_key = f"{categories[2]}+{categories[3]}"
        pair1 = clarity_memory.get(pair1_key, {}).get('summary', synthesize_phrase(categories[0], categories[1]))
        pair2 = clarity_memory.get(pair2_key, {}).get('summary', synthesize_phrase(categories[2], categories[3]))
        braided = f"The insight of '{pair1}' overlaps with '{pair2}' in how perception refines intention."
        return jsonify({
            'Insight Braid': braided,
            'Component Pairs': [pair1, pair2],
            'New Path': pair1_key not in clarity_memory or pair2_key not in clarity_memory
        })

    elif clarity_mode == 'silent':
        tiers = generate_tiers(categories)
        return jsonify({'Silent Insight': tiers['Core Four'][0], 'New Path': False})

    elif clarity_mode == 'radial' and len(categories) >= 2:
        spiral = []
        for i in range(len(categories)):
            a = categories[i]
            b = categories[(i + 1) % len(categories)]
            phrase = synthesize_phrase(a, b)
            spiral.append(phrase)
        return jsonify({'Radial Spiral': spiral})

    else:
        tiers = generate_tiers(categories)
        return jsonify(tiers)

if __name__ == '__main__':
    app.run(debug=True)
