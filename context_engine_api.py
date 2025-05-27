from flask import Flask, request, jsonify
from flask_cors import CORS
from context_engine import rewrite_summary_with_gpt

app = Flask(__name__)

# ✅ Set CORS for Firebase hosting
CORS(app, resources={r"/process": {"origins": "https://clarity-28d13.web.app"}})

@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.get_json()
        print("📦 Received POST data:", data)

        summaries = rewrite_summary_with_gpt({
            "level1": data.get("level1", ""),
            "level2": data.get("level2", ""),
            "level3": data.get("level3", "")
        })

        print("🧠 Summaries generated:", summaries)
        return jsonify(summaries)

    except Exception as e:
        print("❌ Error in /process route:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
