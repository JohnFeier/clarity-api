from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
from context_engine import rewrite_summary_with_gpt, generate_deepinsight_statement

# Set template directory and initialize Flask app
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)

# ✅ Enable CORS globally for the frontend origin
CORS(app,
     origins=["https://clarity-28d13.web.app"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"],
     supports_credentials=True)


# Load environment variables
load_dotenv()
TEXT_API_KEY = os.getenv("OPENAI_KEY_TEXT")
IMAGE_API_KEY = os.getenv("OPENAI_KEY_IMAGE")

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

from flask import make_response

@app.route('/generate-image', methods=['POST'])
def generate_image():
    # Handle CORS preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response, 200

    try:
        print(f"🔍 API key present: {bool(os.environ.get('OPENAI_KEY_IMAGE'))}", flush=True)
        print("👁️‍🗨️ ENV OPENAI_KEY_IMAGE:", os.environ.get("OPENAI_KEY_IMAGE"), flush=True)
        openai.api_key = os.environ.get("OPENAI_KEY_IMAGE")

        data = request.get_json(force=True)
        prompt = data.get('prompt', '')

        if not prompt:
            response = jsonify({"error": "No prompt provided."})
            response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
            return response, 400

        print("🎨 Generating image for prompt:", prompt, flush=True)

        response_data = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response_data['data'][0]['url']
        print("🖼️ Image URL:", image_url, flush=True)

        response = jsonify({'image_url': image_url})
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 200

    except Exception as e:
        print("🔥 Error generating image:", str(e), flush=True)
        response = jsonify({"error": "Failed to generate image."})
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 500

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
        openai.api_key = TEXT_API_KEY

        data = request.get_json(force=True)
        print("📥 Received data from frontend:", data, flush=True)

        variables = data.get('variables', [])
        if not variables:
            print("❌ No variables provided.", flush=True)
            response = jsonify({"error": "No variables provided."})
            response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
            return response, 400

        results = generate_deepinsight_statement(variables)
        print("🧠 Deep Insight Structure:", results, flush=True)

        summary = rewrite_summary_with_gpt(results)
        print("🎯 Final GPT Summary:", summary, flush=True)

        response = jsonify({
            "summary_3": summary.get("summary_3", "Error generating 3-sentence summary."),
            "summary_2": summary.get("summary_2", "Error generating 2-sentence summary."),
            "summary_1": summary.get("summary_1", "Error generating 1-sentence summary.")
        })
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 200

    except Exception as e:
        print("🔥 Exception occurred in /process route:", str(e), flush=True)
        response = jsonify({"error": "Internal server error."})
        response.headers["Access-Control-Allow-Origin"] = "https://clarity-28d13.web.app"
        return response, 500


# Entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
