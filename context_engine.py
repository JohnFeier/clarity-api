import os
import openai
from taxonomy_engine import VERTICAL_OPERATORS, lookup_nouns, log_interaction

openai.api_key = os.getenv("OPENAI_API_KEY")


def _format_coordinate_brief(noun_profiles, roles=None):
    lines = []
    for idx, item in enumerate(noun_profiles):
        domain_str = ", ".join(item["domains"])
        role_tag = f" [{roles[idx].upper()}]" if roles and idx < len(roles) else ""
        bridge_note = " [multi-domain bridge — navigate its competing neighborhoods]" if item["is_bridge"] else ""
        lines.append(f"- {item['noun']}{role_tag} -> Domain(s): {domain_str}{bridge_note}")
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
                        "Keep horizontal noun structures strictly separate from vertical verb forces. "
                        "Use assigned domain coordinates to escape clichés and uncover non-obvious structural connections. "
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


def _detect_triad_roles(profiles):
    """Determines whether each word in the 3-word triad acts as a NOUN (horizontal) or VERB (vertical) in context."""
    words = [p["noun"] for p in profiles]
    kumu_hints = [
        f"{p['noun']} (in_kumu={p['source'] == 'kumu_taxonomy'}, domains={', '.join(p['domains'])})"
        for p in profiles
    ]
    prompt = (
        f"Triad: {words[0]}, {words[1]}, {words[2]}\n"
        f"Taxonomy metadata: {'; '.join(kumu_hints)}\n\n"
        "Classify the active grammatical role of each of the 3 words when read together as a triad.\n"
        "Rules:\n"
        "- Abstract ideas (e.g., capitalism, tradition, trust as an institution) are NOUN.\n"
        "- Words expressing an action, force, or transformation (e.g., erode, betray, accelerate, or 'trust' used as an action between two nouns) are VERB.\n"
        "Output ONLY three comma-separated labels from {NOUN, VERB} in exact order (e.g., NOUN, NOUN, VERB)."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Output only three comma-separated labels: NOUN or VERB."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=20
        )
        raw = response.choices[0].message["content"].strip().upper()
        parts = [p.strip() for p in raw.split(",") if p.strip() in {"NOUN", "VERB"}]
        if len(parts) == 3:
            return parts
    except Exception as e:
        print(f"[Clarity Role Detection Error]: {e}")
    return ["NOUN", "NOUN", "NOUN"]


def _classify_vertical_operators(coord_brief, tier_3, verb_hints=None):
    """Classifies the collision's dominant force-vectors into Primary and Secondary Vertical Verb Operators."""
    ops_list = ", ".join(VERTICAL_OPERATORS)
    hint_line = (
        f"Explicit Input Verb Operator(s): {', '.join(verb_hints)} (align operators closely with these forces).\n"
        if verb_hints else ""
    )
    prompt = (
        f"Coordinates:\n{coord_brief}\n\n"
        f"{hint_line}"
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


def _run_triangulation_funnel(profiles, roles):
    """3-Noun Mode: Horizontal intersection across 3 domains, followed by emergent vertical operator tagging."""
    a, b, c = profiles[0], profiles[1], profiles[2]
    coord_brief = _format_coordinate_brief(profiles, roles)

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

    tier_3 = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Convergent Synthesis 1: {abbc}\nConvergent Synthesis 2: {bcac}\n\n"
        "Synthesize this into ONE single, vivid, memorable sentence (under 28 words) that captures the deepest "
        "universal truth connecting all three concepts.",
        max_tokens=80
    )

    primary_op, secondary_op = _classify_vertical_operators(coord_brief, tier_3)
    return ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op


def _run_operator_funnel(profiles, roles):
    """2-Noun + 1-Verb Mode: Horizontal arithmetic (N1 ± N2) followed by Vertical Operator transformation ((N1, N2) ×/÷ V)."""
    noun_profiles = [p for p, r in zip(profiles, roles) if r == "NOUN"]
    verb_profiles = [p for p, r in zip(profiles, roles) if r == "VERB"]

    n1, n2 = noun_profiles[0], noun_profiles[1]
    v = verb_profiles[0]
    coord_brief = _format_coordinate_brief(profiles, roles)

    ab = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Horizontal Addition ({n1['noun']} + {n2['noun']}): In ONE concise sentence (under 22 words), identify what "
        f"'{n1['noun']}' ({', '.join(n1['domains'])}) and '{n2['noun']}' ({', '.join(n2['domains'])}) share structurally.",
        max_tokens=70
    )
    bc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Horizontal Subtraction ({n1['noun']} - {n2['noun']}): In ONE concise sentence (under 22 words), identify the "
        f"core structural difference or tension separating '{n1['noun']}' and '{n2['noun']}'.",
        max_tokens=70
    )
    ac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Vertical Operation (({n1['noun']}, {n2['noun']}) acted upon by '{v['noun']}'): In ONE concise sentence (under 22 words), "
        f"explain how the action '{v['noun']}' transforms, amplifies, or fractures the relationship between '{n1['noun']}' and '{n2['noun']}'.",
        max_tokens=70
    )

    abbc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Shared Ground (N1 + N2): {ab}\nVertical Force ({v['noun']}): {ac}\n\n"
        f"In ONE sharp sentence (under 24 words), show how '{v['noun']}' alters the shared ground between '{n1['noun']}' and '{n2['noun']}'.",
        max_tokens=80
    )
    bcac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Structural Gap (N1 - N2): {bc}\nVertical Force ({v['noun']}): {ac}\n\n"
        f"In ONE sharp sentence (under 24 words), show how '{v['noun']}' widens or resolves the gap between '{n1['noun']}' and '{n2['noun']}'.",
        max_tokens=80
    )

    tier_3 = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Transformation 1: {abbc}\nTransformation 2: {bcac}\n\n"
        "Synthesize this into ONE single, vivid, memorable sentence (under 28 words) capturing the exact reality event "
        f"produced when '{v['noun']}' acts upon '{n1['noun']}' and '{n2['noun']}'.",
        max_tokens=80
    )

    primary_op, secondary_op = _classify_vertical_operators(coord_brief, tier_3, verb_hints=[v["noun"]])
    return ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op


def _run_dual_operator_funnel(profiles, roles):
    """1-Noun + 2-Verb Mode: Two vertical forces (V1, V2) acting simultaneously on a single horizontal anchor (N1)."""
    n1 = [p for p, r in zip(profiles, roles) if r == "NOUN"][0]
    verbs = [p for p, r in zip(profiles, roles) if r == "VERB"]
    v1, v2 = verbs[0], verbs[1]
    coord_brief = _format_coordinate_brief(profiles, roles)

    ab = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Force 1 on Anchor ({n1['noun']} × {v1['noun']}): In ONE concise sentence (under 22 words), explain what happens "
        f"when '{v1['noun']}' acts directly upon '{n1['noun']}' ({', '.join(n1['domains'])}).",
        max_tokens=70
    )
    bc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Force 2 on Anchor ({n1['noun']} × {v2['noun']}): In ONE concise sentence (under 22 words), explain what happens "
        f"when '{v2['noun']}' acts directly upon '{n1['noun']}' ({', '.join(n1['domains'])}).",
        max_tokens=70
    )
    ac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Operator Collision ({v1['noun']} vs. {v2['noun']}): In ONE concise sentence (under 22 words), reveal whether "
        f"'{v1['noun']}' and '{v2['noun']}' reinforce, sequence, or counteract each other as forces.",
        max_tokens=70
    )

    abbc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Action 1: {ab}\nAction 2: {bc}\n\n"
        f"In ONE sharp sentence (under 24 words), synthesize the push-and-pull created when both forces act on '{n1['noun']}'.",
        max_tokens=80
    )
    bcac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Action 2: {bc}\nForce Dynamic: {ac}\n\n"
        f"In ONE sharp sentence (under 24 words), show which force dominates '{n1['noun']}' over time and why.",
        max_tokens=80
    )

    tier_3 = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Resulting Dynamic 1: {abbc}\nResulting Dynamic 2: {bcac}\n\n"
        "Synthesize this into ONE single, vivid, memorable sentence (under 28 words) capturing the fate of "
        f"'{n1['noun']}' caught between '{v1['noun']}' and '{v2['noun']}'.",
        max_tokens=80
    )

    primary_op, secondary_op = _classify_vertical_operators(coord_brief, tier_3, verb_hints=[v1["noun"], v2["noun"]])
    return ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op


def _run_pure_dynamics_funnel(profiles, roles):
    """3-Verb Mode: Maps pure transformation mechanics across three vertical forces (V1, V2, V3)."""
    v1, v2, v3 = profiles[0], profiles[1], profiles[2]
    coord_brief = _format_coordinate_brief(profiles, roles)

    ab = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Force Pairing 1 ({v1['noun']} × {v2['noun']}): In ONE concise sentence (under 22 words), explain how the action "
        f"'{v1['noun']}' triggers, amplifies, or resists '{v2['noun']}'.",
        max_tokens=70
    )
    bc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Force Pairing 2 ({v2['noun']} × {v3['noun']}): In ONE concise sentence (under 22 words), explain how the action "
        f"'{v2['noun']}' leads into, collides with, or resolves into '{v3['noun']}'.",
        max_tokens=70
    )
    ac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Arc from '{v1['noun']}' to '{v3['noun']}': In ONE concise sentence (under 22 words), reveal the structural shift "
        f"between initiating with '{v1['noun']}' and arriving at '{v3['noun']}'.",
        max_tokens=70
    )

    abbc = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"First Transition: {ab}\nSecond Transition: {bc}\n\n"
        "In ONE sharp sentence (under 24 words), identify the causal chain or feedback loop linking all three actions.",
        max_tokens=80
    )
    bcac = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Second Transition: {bc}\nOverall Arc: {ac}\n\n"
        "In ONE sharp sentence (under 24 words), identify the deeper law of change governing this three-step dynamic.",
        max_tokens=80
    )

    tier_3 = get_synthesis(
        f"Semantic Map Coordinates:\n{coord_brief}\n\n"
        f"Causal Chain: {abbc}\nGoverning Law: {bcac}\n\n"
        "Synthesize this into ONE single, vivid, memorable sentence (under 28 words) expressing the universal cycle "
        f"defined by '{v1['noun']}', '{v2['noun']}', and '{v3['noun']}'.",
        max_tokens=80
    )

    primary_op, secondary_op = _classify_vertical_operators(
        coord_brief, tier_3, verb_hints=[v1["noun"], v2["noun"], v3["noun"]]
    )
    return ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op


def run_clarity_funnel(noun1, noun2=None, noun3=None):
    # Support both run_clarity_funnel(["a", "b", "c"]) and run_clarity_funnel("a", "b", "c")
    if isinstance(noun1, (list, tuple)):
        if len(noun1) < 3:
            raise ValueError("run_clarity_funnel requires 3 words.")
        nouns = [str(v).strip() for v in noun1[:3]]
    else:
        if noun2 is None or noun3 is None:
            raise ValueError("run_clarity_funnel requires 3 words.")
        nouns = [str(noun1).strip(), str(noun2).strip(), str(noun3).strip()]

    profiles = lookup_nouns(nouns)
    roles = _detect_triad_roles(profiles)
    verb_count = roles.count("VERB")

    if verb_count == 0:
        funnel_mode = "triangulation"
        ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op = _run_triangulation_funnel(profiles, roles)
    elif verb_count == 1:
        funnel_mode = "operator"
        ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op = _run_operator_funnel(profiles, roles)
    elif verb_count == 2:
        funnel_mode = "dual_operator"
        ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op = _run_dual_operator_funnel(profiles, roles)
    else:
        funnel_mode = "pure_dynamics"
        ab, bc, ac, abbc, bcac, tier_3, primary_op, secondary_op = _run_pure_dynamics_funnel(profiles, roles)

    # Log the (X, Y) coordinate and funnel_mode into interactions.db
    tier_1_log = f"[{funnel_mode.upper()}] AB: {ab} | BC: {bc} | AC: {ac}"
    tier_2_log = f"[{funnel_mode.upper()}] ABBC: {abbc} | BCAC: {bcac}"
    log_interaction(
        profiles,
        tier_1_log,
        tier_2_log,
        tier_3,
        primary_operator=primary_op,
        secondary_operator=secondary_op,
        funnel_mode=funnel_mode
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
        "funnel_mode": funnel_mode,
        "roles": roles,
        "taxonomy": profiles,
        "operators": {
            "primary": primary_op,
            "secondary": secondary_op
        }
    }
