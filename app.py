from flask import Flask, render_template, request, jsonify
from context_engine import rewrite_summary_with_gpt, generate_deepinsight_statement

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/results")
def results():
    return render_template("results.html")

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    variables = data.get('variables', [])
    results = generate_deepinsight_statement(variables)
    summary = rewrite_summary_with_gpt(results)
    return jsonify({"results": results, "summary": summary})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
