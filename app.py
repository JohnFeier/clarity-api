from flask import Flask, request, jsonify
from context_engine import rewrite_summary_with_gpt, generate_deepinsight_statement

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Clarity API is running."})

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        variables = data.get('variables', [])
        if not variables:
            return jsonify({"error": "No variables provided."}), 400

        results = generate_deepinsight_statement(variables)
        summary = rewrite_summary_with_gpt(results)

        return jsonify({
            "summary_3": summary["summary_3"],
            "summary_2": summary["summary_2"],
            "summary_1": summary["summary_1"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
