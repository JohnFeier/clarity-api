import openai
import os

# Initialize API Key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- Radiant Signatures (Your Interpretive Lenses, mapped to the 8 Vertical Operators) ---
RADIANT_SIGNATURES = [
    {
        "operator": "FORGE",
        "name": "Mirror of Becoming",
        "perspective": "Internal",
        "time": "Present",
        "agency": "Emergent",
        "scale": "Meso",
        "emotion": "Hope",
        "modality": "Embodied",
        "logic": "Analogical",
        "visual_motif": "Luminous gestation, molten light crystallizing into new architecture",
        "visual_style": (
            "Luminous chiaroscuro oil painting blended with sacred glasswork; warm molten gold, "
            "amber, and deep teal shadows; upward spiral composition where raw elements coalesce "
            "into glowing crystalline structures; radiant volumetric light."
        )
    },
    {
        "operator": "ERODE",
        "name": "Ecliptic Memory",
        "perspective": "Meta",
        "time": "Past",
        "agency": "Passive",
        "scale": "Macro",
        "emotion": "Longing",
        "modality": "Conceptual",
        "logic": "Metaphorical",
        "visual_motif": "Weathered stone, dissolving edges, twilight eclipse over receding forms",
        "visual_style": (
            "Atmospheric poetic realism with wind-eroded sandstone, drifting ash, and oxidized copper; "
            "muted twilight indigo, slate grey, and pale silver eclipse halo; receding horizon lines "
            "and dissolving silhouettes evoking impermanence."
        )
    },
    {
        "operator": "COLLIDE",
        "name": "Catalyst Loop",
        "perspective": "External",
        "time": "Future",
        "agency": "Active",
        "scale": "Micro",
        "emotion": "Excitement",
        "modality": "Visual",
        "logic": "Causal",
        "visual_motif": "Intersecting shockwaves, kinetic sparks, split-hemisphere tension",
        "visual_style": (
            "High-contrast dramatic split-hemisphere composition with diagonal fault lines and kinetic shockwaves; "
            "incandescent crimson-orange sparks colliding against electric cobalt shadow; sharp architectural "
            "fracture geometry and dynamic motion."
        )
    },
    {
        "operator": "BIND",
        "name": "Harmonic Lattice",
        "perspective": "Relational",
        "time": "Present",
        "agency": "Co-creative",
        "scale": "Meso",
        "emotion": "Reverence",
        "modality": "Structural",
        "logic": "Topological",
        "visual_motif": "Interlocking golden threads, symmetrical resonance, bridged constellations",
        "visual_style": (
            "Intricate Renaissance-meets-sacred-geometry tapestry; fine luminous golden filaments weaving "
            "separate worlds into symmetrical balance; warm candlelight, emerald, and ivory palette; "
            "harmonic bridges and cymatic resonance ripples."
        )
    },
    {
        "operator": "TRANSMIT",
        "name": "Prism Current",
        "perspective": "Systemic",
        "time": "Future",
        "agency": "Conductive",
        "scale": "Macro",
        "emotion": "Wonder",
        "modality": "Acoustic-Luminous",
        "logic": "Propagative",
        "visual_motif": "Refracted spectral beams, concentric ripples carrying signal across horizons",
        "visual_style": (
            "Expansive panoramic futurist art; beams of light refracting through crystal prisms into "
            "concentric acoustic and optical waves across vast landscapes; iridescent cyan, pearl white, "
            "and solar gold; sense of effortless propagation."
        )
    },
    {
        "operator": "CONTAIN",
        "name": "Obsidian Threshold",
        "perspective": "Boundary",
        "time": "Present",
        "agency": "Restraining",
        "scale": "Meso",
        "emotion": "Stillness",
        "modality": "Architectural",
        "logic": "Deductive",
        "visual_motif": "Sacred geometric vessels, gravitational horizons holding volatile energy in equilibrium",
        "visual_style": (
            "Monumental brutalist-neoclassical architecture carved from dark obsidian and brushed bronze; "
            "concentric stone rings and taut geometric thresholds holding intense inner fire in solemn "
            "equilibrium; deep charcoal, warm alabaster, and controlled ember glow."
        )
    },
    {
        "operator": "METABOLIZE",
        "name": "Alchemical Crucible",
        "perspective": "Organic",
        "time": "Transitional",
        "agency": "Adaptive",
        "scale": "Micro-to-Macro",
        "emotion": "Renewal",
        "modality": "Living-System",
        "logic": "Dialectical",
        "visual_motif": "Bioluminescent root networks, transmuting shadow and decay into living growth",
        "visual_style": (
            "Surrealist botanical alchemy; intricate bioluminescent root and mycelial networks transforming "
            "dark volcanic soil and decayed ruins into vibrant emerald moss and blooming light; "
            "deep forest viridian, rich umber, and bioluminescent turquoise."
        )
    },
    {
        "operator": "ENDURE",
        "name": "Celestial Astrolabe",
        "perspective": "Cosmic",
        "time": "Cyclical",
        "agency": "Steadfast",
        "scale": "Macro",
        "emotion": "Serenity",
        "modality": "Archetypal",
        "logic": "Recursive",
        "visual_motif": "Concentric brass orbital rings, ancient monoliths enduring across turning eras",
        "visual_style": (
            "Timeless celestial engraving meets hyper-detailed cosmic realism; weathered granite monoliths "
            "framed by giant rotating brass astrolabe rings and star trails; deep midnight ultramarine, "
            "burnished bronze, and starlight silver; serene cyclical permanence."
        )
    }
]

OPERATOR_LENS_MAP = {sig["operator"]: sig for sig in RADIANT_SIGNATURES}
NAME_LENS_MAP = {sig["name"].lower(): sig for sig in RADIANT_SIGNATURES}


def get_signature_for_operator(primary_operator):
    """Selects the matching Radiant Signature for a given vertical operator, defaulting to Mirror of Becoming."""
    if not primary_operator:
        return RADIANT_SIGNATURES[0]
    return OPERATOR_LENS_MAP.get(primary_operator.strip().upper(), RADIANT_SIGNATURES[0])


def get_signature_by_name_or_operator(lens_name="", primary_operator=""):
    """Resolves a Radiant Signature from either its lens name or its vertical operator."""
    if lens_name and lens_name.strip().lower() in NAME_LENS_MAP:
        return NAME_LENS_MAP[lens_name.strip().lower()]
    return get_signature_for_operator(primary_operator)


def build_radiance_image_prompt(core_synthesis, lens_name="", primary_operator=""):
    """Constructs an operator-tailored visual art direction prompt for /generate-image."""
    sig = get_signature_by_name_or_operator(lens_name=lens_name, primary_operator=primary_operator)
    return (
        f"Visual Lens: {sig['name']} ({sig['operator']} Force Vector). "
        f"Artistic Direction & Palette: {sig['visual_style']} "
        f"Symbolic Motif: {sig['visual_motif']}. "
        f"Conceptual Scene to Depict: {core_synthesis} "
        f"Ultra-detailed, museum-grade symbolic artwork, rich atmospheric depth, zero cluttered labels or gibberish text."
    )


def run_radiance_engine(noun1, noun2, noun3, signature, secondary_operator=""):
    """
    Synthesizes three concepts into a poetic insight using the operator-matched Radiance signature.
    """
    secondary_note = (
        f"- Secondary Undercurrent: {secondary_operator} (subtle counter-force in the background)\n"
        if secondary_operator else ""
    )

    prompt = f"""
    Interpret the relationship between the concepts **{noun1}**, **{noun2}**, and **{noun3}** 
    using the following interpretive lens:

- Signature: {signature['name']} (Force Vector: {signature.get('operator', 'FORGE')})
{secondary_note}- Perspective: {signature['perspective']}
- Time Orientation: {signature['time']}
- Agency: {signature['agency']}
- Scale: {signature['scale']}
- Emotional Tone: {signature['emotion']}
- Reasoning Style: {signature['logic']}
- Visual Motif: {signature.get('visual_motif', '')}

    Speak poetically, metaphorically, or archetypally. Structure your output in three short parts:
1. A one-line metaphor.
2. An expanded reflection.
3. A philosophical implication.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a poetic philosopher and master of metaphor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=350
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"🔥 Error in Radiance Engine: {str(e)}")
        return "The radiance is currently clouded. Please try again."
