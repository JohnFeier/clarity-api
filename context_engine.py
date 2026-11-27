import os
import openai
from taxonomy_engine import VERTICAL_OPERATORS, lookup_nouns, log_interaction

openai.api_key = os.getenv("OPENAI_API_KEY")


def _format_coordinate_brief(noun_profiles):
    lines = []
    for item in noun_profiles:
        domain_str = ", ".join(item["domains"])
        bridge_note = " [multi-domain bridge noun — navigate its competing neighborhoods]" if item["is_bridge"] else ""
        lines.append(f"- {item['noun']} -> Domain(s): {domain_str}{bridge_note}")
    return "\n".join(lines)


def get_synthesis(prompt, max_tokens=120):
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


def _classify_vertical_operators(coord_brief, tier_3):
    """Classifies the collision's dominant force-vectors into Primary and Secondary Vertical Verb Operators."""
    ops_list = ", ".join(VERTICAL_OPERATORS)
    prompt = (
        f"Horizontal Coordinates:\n{coord_brief}\n\n"
        f"Crystalline Synthesis:\n{tier_3}\n\n"
        f"Select the PRIMARY and SECONDARY Vertical Verb Operators from this exact list:\n{ops_list}\n\n"
        "Definitions:\n"
        "- FORGE: creation, synthesis, birth of new structure\n"
        "- ERODE: decay, dissolution, hollowing out\n"
        "- BIND: integration, alignment, trust, stabilization\n"
        "- COLLIDE: friction, disruption, acute clash\n"
        "- TRANSMIT: diffusion, exchange, amplification across boundaries\n"
        "- CONTAIN: constraint, governance, regulation, resistance\n"
        "- METABOLIZE: adaptation, reshaping, absorbing shock into evolution\n"
        "- ENDURE: continuity, cyclical recurrence, deep inertia\n\n"
        "Output ONLY two comma-separated uppercase operator names (e.g., METABOLIZE, FORGE)."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Output only two valid uppercase operator names separated by a comma."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=20
        )
        raw = response.choices[0].message["content"].strip().upper()
        parts = [p.strip() for p in raw.split(",") if p.strip() in VERTICAL_OPERATORS]
        primary = parts[0] if len(parts) >= 1 else "FORGE"
        secondary = parts[1] if len(parts) >= 2 and parts[1] != primary else ""
        return primary, secondary
    except Exception as e:
        print(f"[Clarity Operator Tagging Error]: {e}")
        return "FORGE", ""


def run_clarity_funnel(noun1, noun2=None, noun3=None):
    # Support both run_clarity_funnel(["a", "b", "c"]) and run_clarity_funnel("a", "b", "c")
    if isinstance(noun1, (list, tuple)):
        if len(noun1) < 3:
            raise ValueError("run_clarity_funnel requires 3 nouns.")
        nouns = [str(v).strip() for v in noun1[:3]]
    else:
        if noun2 is None or noun3 is None:
            raise ValueError("run_clarity_funnel requires 3 nouns.")
        nouns = [str(noun1).strip(), str(noun2).strip(), str(noun3).strip()]

    profiles = lookup_nouns(nouns)
    a, b, c = profiles[0], profiles[1], profiles[2]
    coord_brief = _format_coordinate_brief(profiles)

    # Tier 1: Pairwise intersections ('ab', 'bc', 'ac') grounded in Kumu domain neighborhoods
    ab = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"In ONE concise sentence (under 22 words), reveal the non-obvious intersection between "
        f"'{a['noun']}' ({', '.join(a['domains'])}) and '{b['noun']}' ({', '.join(b['domains'])}).",
        max_tokens=70
    )
    bc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"In ONE concise sentence (under 22 words), reveal the non-obvious intersection between "
        f"'{b['noun']}' ({', '.join(b['domains'])}) and '{c['noun']}' ({', '.join(c['domains'])}).",
        max_tokens=70
    )
    ac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"In ONE concise sentence (under 22 words), reveal the non-obvious intersection between "
        f"'{a['noun']}' ({', '.join(a['domains'])}) and '{c['noun']}' ({', '.join(c['domains'])}).",
        max_tokens=70
    )

    # Tier 2: Convergent syntheses ('abbc', 'bcac') across the overlapping pairs
    abbc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Intersection A-B: {ab}\nIntersection B-C: {bc}\n\n"
        "In ONE sharp sentence (under 24 words), synthesize the structural tension where these two intersections converge.",
        max_tokens=80
    )
    bcac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Intersection B-C: {bc}\nIntersection A-C: {ac}\n\n"
        "In ONE sharp sentence (under 24 words), synthesize the structural tension where these two intersections converge.",
        max_tokens=80
    )

    # Tier 3: Final crystalline synthesis — shortest and sharpest (1 sentence, ideal for Radiance)
    tier_3 = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Convergent Synthesis 1: {abbc}\nConvergent Synthesis 2: {bcac}\n\n"
        "Synthesize this into ONE single, vivid, memorable sentence (under 28 words) that captures the deepest "
        "universal truth connecting all three concepts.",
        max_tokens=80
    )

    # Tag the vertical force-vectors and log the full (X, Y) coordinate into interactions.db
    primary_op, secondary_op = _classify_vertical_operators(coord_brief, tier_3)
    tier_1_log = f"AB: {ab} | BC: {bc} | AC: {ac}"
    tier_2_log = f"ABBC: {abbc} | BCAC: {bcac}"
    log_interaction(
        profiles,
        tier_1_log,
        tier_2_log,
        tier_3,
        primary_operator=primary_op,
        secondary_operator=secondary_op
    )

    return {
        "tier_1": {
            "ab": ab,
            "bc": bc,
            "ac": ac
        },
        "tier_2": {
            "abbc": abbc,
            "bcac": bcac
        },
        "tier_3": tier_3,
        "taxonomy": profiles,
        "operators": {
            "primary": primary_op,
            "secondary": secondary_op
        }
    }
