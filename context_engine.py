import re
import os
from openai import OpenAI  # Only if you're still using GPT features

# .env loading logic has been removed for minimalist purity

# --- OpenAI Client Initialization ---
openai_api_key_from_env = os.environ.get("OPENAI_API_KEY")


def strip_html(text):
    if text:
        text = re.sub(r'<[^>]+>', '', text)
        return re.sub(r'\s+', ' ', text).strip()
    return ""

def generate_prompt(levels):
    context = f"{levels['level1']}, {levels['level2']}, {levels['level3']}"
    return (
        "Please summarize the following context into three levels:\n"
        "Level 1: 3-sentence version\n"
        "Level 2: 2-sentence version\n"
        "Level 3: 1-sentence version\n\n"
        f"Context: {context}"
    )

def rewrite_summary_with_gpt(levels):
    prompt = generate_prompt(levels)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    match1 = re.search(r"Level 1:\s*(.+?)\nLevel 2:", content, re.DOTALL)
    match2 = re.search(r"Level 2:\s*(.+?)\nLevel 3:", content, re.DOTALL)
    match3 = re.search(r"Level 3:\s*(.+)", content, re.DOTALL)

    return {
        "summary_3": strip_html(match1.group(1)) if match1 else "Could not parse Level 1",
        "summary_2": strip_html(match2.group(1)) if match2 else "Could not parse Level 2",
        "summary_1": strip_html(match3.group(1)) if match3 else "Could not parse Level 3"
    }
if __name__ == "__main__":
    print("🟡 DEBUG: Entered __main__ block")
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ Clarity engine is running on port {port}...")
    app.run(host="0.0.0.0", port=port)
