from flask import Flask, request, jsonify
import os
import sys

# Ensure the current directory is in the Python path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

INFO_MESSAGE = (
    "Note: For best results, input a list of nouns.\n"
    "The engine works through circular adjacency, comparing each noun to its neighbor.\n"
    "It returns only what is shared — commonalities only."
)

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
    print(f"DEBUG: Flask app object = {app}")
    app.run(host="0.0.0.0", port=port)
