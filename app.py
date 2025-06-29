from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from context_engine import rewrite_summary_with_gpt, generate_deepinsight_statement
import openai
import os
from dotenv import load_dotenv

# Set template directory and initialize Flask app
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)


# Enable CORS for frontend origin
CORS(app, resources={r"/*": {"origins": "https://clarity-28d13.web.app"}})

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

@app.route('/generate-image', methods=['POST', 'OPTIONS'])
def generate_image():
    if request.method == 'OPTIONS':
        # CORS preflight - return OK with headers (handled by Flask-CORS already)
        return '', 200

    try:
        openai.api_key = IMAGE_API_KEY

        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "No prompt provided."}), 400

        print("🎨 Generating image for prompt:", prompt, flush=True)

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response['data'][0]['url']
        print("🖼️ Image URL:", image_url, flush=True)
        return jsonify({'image_url': image_url})

    except Exception as e:
        print("🔥 Error generating image:", str(e), flush=True)
        return jsonify({"error": "Failed to generate image."}), 500

# 🌟 Radiance Image Generator Route
@app.route('/generate-image', methods=['POST', 'OPTIONS'])
def generate_image():
    try:
        openai.api_key = IMAGE_API_KEY

        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "No prompt provided."}), 400

        print("🎨 Generating image for prompt:", prompt, flush=True)

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response['data'][0]['url']
        print("🖼️ Image URL:", image_url, flush=True)
        return jsonify({'image_url': image_url})

    except Exception as e:
        print("🔥 Error generating image:", str(e), flush=True)
        return jsonify({"error": "Failed to generate image."}), 500

# Entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
