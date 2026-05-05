import openai
import os
from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# 1. IMPORT YOUR ENGINES
from context_engine import run_clarity_funnel
from radiant_clarity_engine import run_engines, RADIANT_SIGNATURES

# 2. INITIALIZE APP & LOAD API KEY
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

# 5. THE MAIN PROCESS ROUTE
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

        # --- STEP 1: Run the Logic Funnel (Clarity) ---
        funnel_results = run_clarity_funnel(variables)
        
        # --- STEP 2: Format strings for the Frontend ---
        # We extract the specific syntheses from the nested dictionaries
        t1_combined = f"Intersections: {funnel_results['tier_1']['ab']} | {funnel_results['tier_1']['bc']} | {funnel_results['tier_1']['ac']}"
        t2_combined = f"Syntheses: {funnel_results['tier_2']['abbc']} and {funnel_results['tier_2']['bcac']}"
        proto_idea = funnel_results.get("tier_3", "Synthesis incomplete.")
        
        # --- STEP 3: Run the Radiance Engine ---
        noun1, noun2, noun3 = [v.strip() for v in variables[:3]]
        selected_signature = RADIANT_SIGNATURES[0] 
        
        # We execute the poetic interpretation based on the nouns
        radiance_data = run_engines(noun1, noun2, noun3, selected_signature)
        radiance_output = radiance_data.get("Radiance", "Radiance insight pending.")

        # --- STEP 4: SEND TO FRONTEND ---
        # These keys now match the summary_1, 2, 3 pattern in results.html
        return jsonify({
            "summary_1": t1_combined,  
            "summary_2": t2_combined,  
            "summary_3": proto_idea,   
            "radiance": radiance_output 
        }), 200

    except Exception as e:
        print(f"🔥 Error occurred: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 6. START THE SERVER
if __name__ == "__main__":
    app.run(debug=True)