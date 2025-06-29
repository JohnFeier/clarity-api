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
CORS(app, origins=["https://clarity-28d13.web.app"])


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
        openai.api_key = IMAGE_API_KEY

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


# Entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
