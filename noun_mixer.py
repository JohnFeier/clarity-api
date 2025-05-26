from flask import Flask, request, jsonify
import os

app = Flask(__name__)

INFO_MESSAGE = (
    "Note: For best results, input a list of nouns.\n"
    "The engine works through circular adjacency, comparing each noun to its neighbor.\n"
    "It returns only what is shared — commonalities only."
)

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

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    variables = data.get("variables", [])
    result = noun_mixer(variables)
    return jsonify({
        "message": INFO_MESSAGE,
        "synthesis": result
    })

if __name__ == "__main__":
    print("🟡 DEBUG: Entered __main__ block")
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ Clarity engine is running on port {port}...")
    app.run(host="0.0.0.0", port=port)

