def generate_radiance_prompt(triplet: NounTriplet, signature: dict) -> str:
    return f"""
Interpret the relationship between the concepts **{triplet[0]}**, **{triplet[1]}**, and **{triplet[2]}**
using the following interpretive lens:

- Perspective: {signature['perspective']}
- Time Orientation: {signature['time']}
- Agency: {signature['agency']}
- Scale: {signature['scale']}
- Emotional Tone: {signature['emotion']}
- Modality: {signature['modality']}
- Reasoning Style: {signature['logic']}

Speak poetically, metaphorically, or archetypally. Structure your output in three tiers:
1. A one-line metaphor
2. An expanded reflection
3. A philosophical implication
"""
