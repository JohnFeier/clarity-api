from flask import Flask, request, jsonify
from context_engine import rewrite_summary_with_gpt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allows frontend to call this API from Firebase

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
