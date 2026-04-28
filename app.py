from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Import the new Logic Funnel from your updated context_engine
from context_engine import run_clarity_funnel
# Import Radiance logic (assuming it's in your radiant_clarity_engine file)
from radiant_clarity_engine import run_engines, RADIANT_SIGNATURES

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

print("🚀 Flask app starting with Logic Funnel engine...", flush=True)

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
        if not variables or len(variables) < 3:
            print("❌ Not enough variables provided.", flush=True)
            response = jsonify({"error": "Three nouns are required for the funnel."})
            response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
            return response, 400

        # --- 💡 CLARITY: THE LOGIC FUNNEL ---
        # We pass the nouns into the funnel to get Tier 1, 2, and 3 results
        funnel_results = run_clarity_funnel(variables)
        proto_idea = funnel_results.get("tier_3", "Synthesis incomplete.")
        
        print("🧠 Logic Funnel Complete. Proto-idea:", proto_idea, flush=True)

        # --- 🌈 RADIANCE ---
        # We still use the original nouns for now, but Radiance is next for an upgrade!
        noun1, noun2, noun3 = [v.strip() for v in variables[:3]]
        selected_signature = RADIANT_SIGNATURES[0] 
        
        radiant_output = run_engines(noun1, noun2, noun3, selected_signature)["Radiance"]
        print("✨ Radiance Output generated", flush=True)

        # --- 📤 RESPONSE ---
        # We map proto_idea to 'summary_1' so your current frontend still displays it
        response = jsonify({
            "summary_1": proto_idea,
            "tier_1": funnel_results.get("tier_1"),
            "tier_2": funnel_results.get("tier_2"),
            "radiance": radiant_output
        })
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 200

    except Exception as e:
        print("🔥 Exception occurred in /process route:", str(e), flush=True)
        response = jsonify({"error": f"Internal server error: {str(e)}"})
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 500

if __name__ == "__main__":
    app.run(debug=True)
