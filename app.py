from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from context_engine import rewrite_summary_with_gpt, generate_deepinsight_statement
import openai
import os
from dotenv import load_dotenv

# 🌱 Load environment variables
load_dotenv()
TEXT_API_KEY = os.getenv("OPENAI_KEY_TEXT")
IMAGE_API_KEY = os.getenv("OPENAI_KEY_IMAGE")

print("🚀 Flask app starting successfully...", flush=True)

app = Flask(__name__)
CORS(app, origins=["https://clarity-28d13.web.app"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route('/process', methods=['POST'])
def process():
    try:
        openai.api_key = TEXT_API_KEY

        data = request.get_json()
        print("📥 Received data from frontend:", data, flush=True)

        variables = data.get('variables', [])
        if not variables:
            print("❌ No variables provided.", flush=True)
            return jsonify({"error": "No variables provided."}), 400

        results = generate_deepinsight_statement(variables)
        print("🧠 Deep Insight Structure:", results, flush=True)

        summary = rewrite_summary_with_gpt(results)
        print("🎯 Final GPT Summary:", summary, flush=True)

        return jsonify({
            "summary_3": summary.get("summary_3", "Error generating 3-sentence summary."),
            "summary_2": summary.get("summary_2", "Error generating 2-sentence summary."),
            "summary_1": summary.get("summary_1", "Error generating 1-sentence summary.")
        })
    except Exception as e:
        print("🔥 Exception occurred in /process route:", str(e), flush=True)
        raise e

# 🌟 New Radiance Image Generator Route
@app.route('/generate-image', methods=['POST'])
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
