from flask import Flask, request, jsonify
from noun_mixer import noun_mixer

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
    print("\u2705 Clarity engine is running...")
    app.run(debug=True)
