import openai
import os
from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# 1. IMPORT YOUR ENGINES
from context_engine import run_clarity_funnel
from radiant_clarity_engine import run_engines, RADIANT_SIGNATURES

# 2. INITIALIZE APP & LOAD API KEY
import os
app = Flask(__name__, static_folder='static', template_folder='templates')
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 3. SECURITY (CORS) - This allows your frontend to talk to this backend
CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
    return response

print("🚀 Flask app starting with Logic Funnel engine...", flush=True)

# 4. PAGE ROUTES - These show your HTML files
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/results")
def results():
    return render_template("results.html")

# 5. THE MAIN PROCESS ROUTE - This handles the "Process" button
@app.route('/process', methods=['POST', 'OPTIONS'])
def process():
    # Handle the browser's security "handshake" (OPTIONS)
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200

    try:
        # Get data from the frontend
        data = request.get_json(force=True)
        variables = data.get('variables', [])
        
        if not variables or len(variables) < 3:
            return jsonify({"error": "Three nouns are required."}), 400

        # Run the Logic Funnel (Clarity)
        funnel_results = run_clarity_funnel(variables)
        proto_idea = funnel_results.get("tier_3", "Synthesis incomplete.")
        
        # Run the Radiance Engine
        noun1, noun2, noun3 = [v.strip() for v in variables[:3]]
        selected_signature = RADIANT_SIGNATURES[0] 
        radiant_output = run_engines(noun1, noun2, noun3, selected_signature)["Radiance"]

        # Send the results back to the website
        return jsonify({
            "summary_1": proto_idea,
            "tier_1": funnel_results.get("tier_1"),
            "tier_2": funnel_results.get("tier_2"),
            "radiance": radiant_output
        }), 200

    except Exception as e:
        print(f"🔥 Error occurred: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 6. START THE SERVER
if __name__ == "__main__":
    app.run(debug=True)