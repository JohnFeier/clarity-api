from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from context_engine import rewrite_summary_with_gpt, generate_deepinsight_statement

print("🚀 Flask app starting successfully...", flush=True)

app = Flask(__name__)
CORS(app, origins=["https://clarity-28d13.web.app"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        print("📥 Received data from frontend:", data, flush=True)

        variables = data.get('variables', [])
        if not variables:
            print("❌ No variables provided.", flush=True)
            return jsonify({"error": "No variables provided."}), 400

        results = generate_deepinsight_statement(variables)
        print("🧠 Deep Insight Structure:", results, flush=True)

        summary = rewrite_summary_with_gpt(results)
        print("🎯 Final GPT Summary:", summary, flush=True)

        return jsonify({
            "summary_3": summary.get("summary_3", "Error generating 3-sentence summary."),
            "summary_2": summary.get("summary_2", "Error generating 2-sentence summary."),
            "summary_1": summary.get("summary_1", "Error generating 1-sentence summary.")
        })
    except Exception as e:
        print("🔥 Exception occurred in /process route:", str(e), flush=True)
        raise e



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
