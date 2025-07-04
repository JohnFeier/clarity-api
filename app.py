from radiant_clarity_engine import run_engines, RADIANT_SIGNATURES
from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
from context_engine import rewrite_summary_with_gpt, generate_deepinsight_statement

# Load environment variables
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set template directory and initialize Flask app
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)

# ✅ Enable CORS globally for the frontend origin
CORS(app,
     origins=["https://clarity-28d13.web.app"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"],
     supports_credentials=True)

print("🚀 Flask app starting successfully...", flush=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route('/process', methods=['POST', 'OPTIONS'])
def process():
    # Handle CORS preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response, 200

    try:
        data = request.get_json(force=True)
        print("📥 Received data from frontend:", data, flush=True)

        variables = data.get('variables', [])
        if not variables:
            print("❌ No variables provided.", flush=True)
            response = jsonify({"error": "No variables provided."})
            response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
            return response, 400

        # 💡 Clarity
        results = generate_deepinsight_statement(variables)
        print("🧠 Deep Insight Structure:", results, flush=True)

        summary = rewrite_summary_with_gpt(results)
        print("🎯 Final GPT Summary:", summary, flush=True)

        # 🌈 Radiance
        if len(variables) >= 3:
            noun1, noun2, noun3 = variables[:3]
            selected_signature = RADIANT_SIGNATURES[0]  # Can be randomized later
            radiant_output = run_engines(noun1, noun2, noun3, selected_signature)["Radiance"]
            print("✨ Radiance Output:", radiant_output, flush=True)
        else:
            radiant_output = {"error": "Radiance requires 3 input nouns."}

        response = jsonify({
            "summary_3": summary.get("summary_3", "Error generating 3-sentence summary."),
            "summary_2": summary.get("summary_2", "Error generating 2-sentence summary."),
            "summary_1": summary.get("summary_1", "Error generating 1-sentence summary."),
            "radiance": radiant_output
        })
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 200

    except Exception as e:
        print("🔥 Exception occurred in /process route:", str(e), flush=True)
        response = jsonify({"error": "Internal server error."})
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 500

