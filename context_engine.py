import os
import openai
from taxonomy_engine import lookup_nouns, log_interaction

openai.api_key = os.getenv("OPENAI_API_KEY")


def _format_coordinate_brief(noun_profiles):
    lines = []
    for item in noun_profiles:
        domain_str = ", ".join(item["domains"])
        bridge_note = " [multi-domain bridge noun — navigate its competing neighborhoods]" if item["is_bridge"] else ""
        lines.append(f"- {item['noun']} -> Domain(s): {domain_str}{bridge_note}")
    return "\n".join(lines)


def get_synthesis(prompt, max_tokens=220):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Clarity, the analytical synthesis engine of Context Finder. "
                        "You reason inside a structured 31-domain semantic map (the Nominal Universe). "
                        "Use each noun's assigned domain coordinates to escape clichés and uncover non-obvious structural connections. "
                        "Write crisp, objective, insightful prose without fluff."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"[Clarity Engine Error]: {e}")
        return "Connection pending..."


def run_clarity_funnel(noun1, noun2=None, noun3=None):
    # Support both run_clarity_funnel(["a", "b", "c"]) and run_clarity_funnel("a", "b", "c")
    if isinstance(noun1, (list, tuple)):
        if len(noun1) < 3:
            raise ValueError("run_clarity_funnel requires 3 nouns.")
        nouns = list(noun1[:3])
    else:
        if noun2 is None or noun3 is None:
            raise ValueError("run_clarity_funnel requires 3 nouns.")
        nouns = [noun1, noun2, noun3]

    profiles = lookup_nouns(nouns)
    p1, p2, p3 = profiles[0], profiles[1], profiles[2]
    coord_brief = _format_coordinate_brief(profiles)

    # Tier 1: Pairwise intersections grounded in Kumu domain neighborhoods (3–4 sentences)
    tier_1_prompt = (
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"In 3 concise sentences, map the pairwise intersections between:\n"
        f"1) '{p1['noun']}' ({', '.join(p1['domains'])}) and '{p2['noun']}' ({', '.join(p2['domains'])})\n"
        f"2) '{p2['noun']}' ({', '.join(p2['domains'])}) and '{p3['noun']}' ({', '.join(p3['domains'])})\n"
        f"3) '{p1['noun']}' ({', '.join(p1['domains'])}) and '{p3['noun']}' ({', '.join(p3['domains'])})\n"
        "Show how their domain neighborhoods collide."
    )
    tier_1 = get_synthesis(tier_1_prompt, max_tokens=220)

    # Tier 2: Converging tension across all three domains (2 sentences)
    tier_2_prompt = (
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Pairwise Intersections:\n{tier_1}\n\n"
        "Distill this into exactly 2 sentences that reveal the central structural tension or hidden dynamic "
        "where all three domains converge."
    )
    tier_2 = get_synthesis(tier_2_prompt, max_tokens=140)

    # Tier 3: Final crystalline synthesis — shortest and sharpest (1 sentence, ideal for Radiance)
    tier_3_prompt = (
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Converging Tension:\n{tier_2}\n\n"
        "Synthesize this into ONE single, vivid, memorable sentence (under 28 words) that captures the deepest "
        "universal truth connecting all three concepts."
    )
    tier_3 = get_synthesis(tier_3_prompt, max_tokens=75)

    # Log the three-noun and domain collision into interactions.db
    log_interaction(profiles, tier_1, tier_2, tier_3)

    return {
        "tier_1": tier_1,
        "tier_2": tier_2,
        "tier_3": tier_3,
        "taxonomy": profiles
    }
