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
        "visual_motif": "Luminous gestation, molten light crystallizing into new architecture"
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
        "visual_motif": "Weathered stone, dissolving edges, twilight eclipse over receding forms"
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
        "visual_motif": "Intersecting shockwaves, kinetic sparks, split-hemisphere tension"
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
        "visual_motif": "Interlocking golden threads, symmetrical resonance, bridged constellations"
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
        "visual_motif": "Refracted spectral beams, concentric ripples carrying signal across horizons"
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
        "visual_motif": "Sacred geometric vessels, gravitational horizons holding volatile energy in equilibrium"
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
        "visual_motif": "Bioluminescent root networks, transmuting shadow and decay into living growth"
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
        "visual_motif": "Concentric brass orbital rings, ancient monoliths enduring across turning eras"
    }
]

OPERATOR_LENS_MAP = {sig["operator"]: sig for sig in RADIANT_SIGNATURES}


def get_signature_for_operator(primary_operator):
    """Selects the matching Radiant Signature for a given vertical operator, defaulting to Mirror of Becoming."""
    if not primary_operator:
        return RADIANT_SIGNATURES[0]
    return OPERATOR_LENS_MAP.get(primary_operator.strip().upper(), RADIANT_SIGNATURES[0])


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
            model="gpt-4o-mini",  # Fast and efficient for poetic text
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
