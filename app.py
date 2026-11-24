import openai
import os
from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# 1. IMPORT YOUR ENGINES
# Ensure these filenames match exactly: context_engine.py and radiant_clarity_engine.py
from context_engine import run_clarity_funnel
from radiant_clarity_engine import run_radiance_engine, RADIANT_SIGNATURES

# 2. INITIALIZE APP & LOAD API KEY
app = Flask(__name__, static_folder='static', template_folder='templates')
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 3. SECURITY (CORS)
# This prevents the "Blocked by CORS policy" errors you saw earlier
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
    return response

print("🚀 Flask app starting with Logic Funnel engine...", flush=True)

# 4. PAGE ROUTES
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
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200

    try:
        data = request.get_json(force=True)
        variables = data.get('variables', [])
        
        if not variables or len(variables) < 3:
            return jsonify({"error": "Three nouns are required."}), 400

        # --- STEP 1: Run the Logic Funnel (from context_engine.py) ---
        funnel_results = run_clarity_funnel(variables)

        # --- STEP 2: Format strings for the Frontend ---
        # We combine the intersections so they fit into the 3-Tier display
        t1_combined = f"Intersections: {funnel_results['tier_1']['ab']} | {funnel_results['tier_1']['bc']} | {funnel_results['tier_1']['ac']}"
        t2_combined = f"Syntheses: {funnel_results['tier_2']['abbc']} and {funnel_results['tier_2']['bcac']}"
        proto_idea = funnel_results.get("tier_3", "Synthesis incomplete.")

        # --- STEP 3: Run the Radiance Engine (from radiant_clarity_engine.py) ---
        noun1, noun2, noun3 = [v.strip() for v in variables[:3]]
        selected_signature = RADIANT_SIGNATURES[0] # Defaulting to 'Mirror of Becoming'
        radiance_output = run_radiance_engine(noun1, noun2, noun3, selected_signature)

        # --- STEP 4: SEND TO FRONTEND ---
        # These keys match the localStorage.getItem calls in your HTML
        return jsonify({
            "summary_1": t1_combined,
            "summary_2": t2_combined,
            "summary_3": proto_idea,
            "radiance": radiance_output
        }), 200

    except Exception as e:
        print(f"🔥 Error occurred: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 6. IMAGE GENERATION ROUTE
# This handles the "Visualize Insight" button click
@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'A cosmic visualization of clarity')
        
        response = openai.Image.create(
            model="gpt-image-2",
            prompt=f"A cinematic, high-detail metaphysical visualization of: {prompt}",
            n=1,
            size="1024x1024"
        )
        image_data = response['data'][0]
        if 'url' in image_data and image_data['url']:
            image_url = image_data['url']
        else:
            image_url = f"data:image/png;base64,{image_data['b64_json']}"
        return jsonify({"image_url": image_url})
    except Exception as e:
        print(f"🔥 Image Error: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 7. START THE SERVER
if __name__ == "__main__":
    # Use the port Render expects (10000) or default to 5000 for local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
