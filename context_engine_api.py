from flask import Flask, request, jsonify
from flask_cors import CORS
from context_engine import rewrite_summary_with_gpt

app = Flask(__name__)

# ✅ Set CORS for Firebase domain only
CORS(app, resources={r"/process": {"origins": "https://clarity-28d13.web.app"}})



@app.route("/process", methods=["POST"])
def process():
    data = request.json
    summaries = rewrite_summary_with_gpt({
        "level1": data.get("variable1", ""),
        "level2": data.get("variable2", ""),
        "level3": data.get("variable3", "")
    })
    return jsonify(summaries)

if __name__ == "__main__":
    app.run()
