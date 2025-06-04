def assign_categories(nouns):
    """
    Assign each noun to one of 13 inner life categories.
    Returns a list of tuples: (category, noun)
    """
    category_map = {
        "Emotion": {"grief", "joy", "anger", "fear", "love", "shame", "surprise", "sadness"},
        "Desire": {"ambition", "hunger", "lust", "hope", "yearning", "craving", "curiosity"},
        "Sensation": {"pain", "pleasure", "warmth", "cold", "tingle", "itch", "sight", "sound"},
        "Imagination": {"fantasy", "dream", "vision", "scenario", "creativity", "fiction"},
        "Intuition": {"gut", "hunch", "instinct", "premonition", "sense", "knowing"},
        "Will": {"determination", "drive", "resolve", "intention", "discipline", "motivation"},
        "Attention": {"focus", "concentration", "awareness", "presence", "alertness"},
        "Thought": {"idea", "logic", "concept", "belief", "analysis", "reflection"},
        "Memory": {"recall", "past", "event", "experience", "recollection", "nostalgia"},
        "Language": {"word", "speech", "communication", "syntax", "narrative", "expression"},
        "Identity": {"self", "ego", "persona", "character", "role", "reputation"},
        "Decision-making": {"choice", "selection", "judgment", "preference", "option"},
        "Problem-solving": {"solution", "strategy", "plan", "approach", "method", "fix"}
    }

    results = []

    for noun in nouns:
        normalized = noun.strip().lower()
        assigned = False
        for category, keywords in category_map.items():
            if normalized in keywords:
                results.append((category, noun))
                assigned = True
                break
        if not assigned:
            results.append(("Uncategorized", noun))  # fallback for unknown terms

    return results
