import openai
import os
from flask import Flask, request, jsonify, make_response, render_template, Response
from flask_cors import CORS
from dotenv import load_dotenv

# 1. IMPORT YOUR ENGINES
# Ensure these filenames match exactly: context_engine.py, radiant_clarity_engine.py, and taxonomy_engine.py
from context_engine import run_clarity_funnel
from radiant_clarity_engine import run_radiance_engine, get_signature_for_operator
from taxonomy_engine import export_ledger_csv

# 2. INITIALIZE APP & LOAD API KEY
app = Flask(__name__, static_folder='static', template_folder='templates')
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 3. SECURITY (CORS)
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
            return jsonify({"error": "Three words are required."}), 400

        # --- STEP 1: Run the Logic Funnel (from context_engine.py) ---
        funnel_results = run_clarity_funnel(variables)

        # --- STEP 2: Format strings for the Frontend ---
        t1_combined = f"Intersections: {funnel_results['tier_1']['ab']} | {funnel_results['tier_1']['bc']} | {funnel_results['tier_1']['ac']}"
        t2_combined = f"Syntheses: {funnel_results['tier_2']['abbc']} and {funnel_results['tier_2']['bcac']}"
        proto_idea = funnel_results.get("tier_3", "Synthesis incomplete.")

        # --- STEP 3: Run the Radiance Engine using the Operator-Matched Lens ---
        noun1, noun2, noun3 = [v.strip() for v in variables[:3]]
        operators = funnel_results.get("operators", {})
        primary_op = operators.get("primary", "FORGE")
        secondary_op = operators.get("secondary", "")
        selected_signature = get_signature_for_operator(primary_op)

        radiance_output = run_radiance_engine(
            noun1, noun2, noun3, selected_signature, secondary_operator=secondary_op
        )

        # --- STEP 4: SEND TO FRONTEND ---
        return jsonify({
            "summary_1": t1_combined,
            "summary_2": t2_combined,
            "summary_3": proto_idea,
            "radiance": radiance_output,
            "radiance_lens": selected_signature["name"],
            "funnel_mode": funnel_results.get("funnel_mode", "triangulation"),
            "operators": operators
        }), 200

    except Exception as e:
        print(f"🔥 Error occurred: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 6. IMAGE GENERATION ROUTE
@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json(force=True)
        core_prompt = data.get('prompt', 'A cosmic visualization of clarity')
        radiance_lens = data.get('radiance_lens', '')
        primary_operator = data.get('primary_operator', '')

        styled_prompt = build_radiance_image_prompt(
            core_synthesis=core_prompt,
            lens_name=radiance_lens,
            primary_operator=primary_operator,
        )
        
        response = openai.Image.create(
            model="gpt-image-2",
            prompt=styled_prompt,
            n=1,
            size="1024x1024"
        )
        image_data = response['data'][0]
        if 'url' in image_data and image_data['url']:
            image_url = image_data['url']
        else:
            image_url = f"data:image/png;base64,{image_data['b64_json']}"
        return jsonify({
            "image_url": image_url,
            "applied_lens": radiance_lens or primary_operator or "Mirror of Becoming"
        })
    except Exception as e:
        print(f"🔥 Image Error: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 6B. BLUESKY REPLY GENERATOR (LINK-FREE, <300 CHARS)
@app.route('/bluesky-reply', methods=['POST'])
def bluesky_reply():
    try:
        data = request.get_json(force=True)
        tier_3 = (data.get('tier_3') or '').strip()
        if not tier_3 or tier_3 == "No result found.":
            return jsonify({"error": "No synthesis available to distill."}), 400

        prompt = (
            f"Core Synthesis:\n{tier_3}\n\n"
            "Rewrite this synthesis as a single, insightful, conversational reply for Bluesky.\n"
            "Strict rules:\n"
            "- Maximum 260 characters total (must stay strictly under 300 characters).\n"
            "- NO URLs, NO links, NO hashtags, NO emojis, and NO mention of Context Finder.\n"
            "- Sound like a thoughtful human observer offering a crisp reframing—not an AI summary.\n"
            "- Output ONLY the reply text."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You write crisp, incisive micro-insights under 260 characters with zero links or hashtags."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75,
            max_tokens=100
        )

        reply_text = response.choices[0].message["content"].strip().strip('"')
        # Hard safety cap under 300 characters
        if len(reply_text) > 295:
            reply_text = reply_text[:292].rsplit(" ", 1)[0] + "..."

        return jsonify({
            "reply": reply_text,
            "char_count": len(reply_text)
        }), 200

    except Exception as e:
        print(f"🔥 Bluesky reply error: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 7. LEDGER EXPORT ROUTES
@app.route('/export-ledger', methods=['GET'])
def export_ledger():
    try:
        csv_data = export_ledger_csv(table="interactions")
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=context_finder_ledger.csv"}
        )
    except Exception as e:
        print(f"🔥 Ledger export error: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/export-candidates', methods=['GET'])
def export_candidates():
    try:
        csv_data = export_ledger_csv(table="candidates")
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=context_finder_candidates.csv"}
        )
    except Exception as e:
        print(f"🔥 Candidate export error: {str(e)}", flush=True)
        return jsonify({"error": str(e)}), 500

# 8. START THE SERVER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
