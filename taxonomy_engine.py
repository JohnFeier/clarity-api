import csv
import io
import json
import os
import sqlite3
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
import openai

CSV_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "Google_Sheet_for_Kumu.csv")
TAXONOMY_CSV_URL = os.getenv("TAXONOMY_CSV_URL", "").strip()
DB_PATH = os.path.join(os.path.dirname(__file__), "interactions.db")

_NOUN_TO_GROUPS = defaultdict(set)
_ALL_GROUPS = set()
_LOADED = False


def _parse_csv_stream(stream):
    global _NOUN_TO_GROUPS, _ALL_GROUPS
    noun_map = defaultdict(set)
    groups = set()
    reader = csv.DictReader(stream)
    for row in reader:
        label = (row.get("Label") or row.get("Id") or "").strip()
        group = (row.get("Group") or "").strip()
        if label and group:
            noun_map[label.lower()].add(group)
            groups.add(group)
    if noun_map:
        _NOUN_TO_GROUPS = noun_map
        _ALL_GROUPS = groups


def load_taxonomy(force_reload=False):
    """Loads the 31-domain Kumu noun taxonomy from a live Google Sheet CSV URL or local CSV."""
    global _LOADED
    if _LOADED and not force_reload:
        return

    loaded_from_url = False
    if TAXONOMY_CSV_URL:
        try:
            with urllib.request.urlopen(TAXONOMY_CSV_URL, timeout=6) as resp:
                text = resp.read().decode("utf-8-sig")
                _parse_csv_stream(io.StringIO(text))
                loaded_from_url = True
        except Exception as e:
            print(f"[Taxonomy] Remote CSV fetch failed ({e}); falling back to local CSV.")

    if not loaded_from_url and os.path.exists(CSV_LOCAL_PATH):
        with open(CSV_LOCAL_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
            _parse_csv_stream(f)

    _LOADED = True
    print(f"[Taxonomy] Loaded {len(_NOUN_TO_GROUPS)} unique nouns across {len(_ALL_GROUPS)} domains.")


def init_db():
    """Creates the SQLite interaction ledger for tracking three-noun and domain collisions."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                noun_1 TEXT NOT NULL,
                noun_2 TEXT NOT NULL,
                noun_3 TEXT NOT NULL,
                domains_1 TEXT NOT NULL,
                domains_2 TEXT NOT NULL,
                domains_3 TEXT NOT NULL,
                tier_1 TEXT,
                tier_2 TEXT,
                tier_3 TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS candidate_nouns (
                noun TEXT PRIMARY KEY,
                assigned_domain TEXT NOT NULL,
                times_seen INTEGER NOT NULL DEFAULT 1,
                first_seen TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _classify_unknown_noun(noun):
    """Assigns a brand-new user noun to the closest of the 31 Kumu domains and queues it as a candidate."""
    if not _ALL_GROUPS:
        return ["General"]

    sorted_groups = sorted(_ALL_GROUPS)
    prompt = (
        f"Classify the noun '{noun}' into the single best-fitting domain from this exact list:\n"
        f"{', '.join(sorted_groups)}\n\n"
        "Respond with ONLY the exact domain name from the list above."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict taxonomic classifier. Output only one exact category name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=20
        )
        choice = response.choices[0].message["content"].strip()
        matched = next((g for g in sorted_groups if g.lower() == choice.lower()), "General")
    except Exception as e:
        print(f"[Taxonomy] Dynamic classification fallback for '{noun}': {e}")
        matched = "General"

    # Record the new noun in SQLite so you can review and add popular user nouns to your Google Sheet
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            INSERT INTO candidate_nouns (noun, assigned_domain, times_seen, first_seen)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(noun) DO UPDATE SET times_seen = times_seen + 1
        """, (noun.lower(), matched, now))
        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"[Taxonomy] Candidate noun log skipped: {db_err}")

    return [matched]


def lookup_nouns(nouns):
    """
    Returns structural metadata for each input noun:
    - exact domains from Google_Sheet_for_Kumu.csv
    - whether it is a multi-domain 'bridge' noun
    - dynamic domain classification if not yet in the sheet
    """
    load_taxonomy()
    results = []
    for raw in nouns:
        clean = raw.strip()
        key = clean.lower()
        if key in _NOUN_TO_GROUPS:
            domains = sorted(_NOUN_TO_GROUPS[key])
            source = "kumu_taxonomy"
        else:
            domains = _classify_unknown_noun(clean)
            source = "dynamic_candidate"

        results.append({
            "noun": clean,
            "domains": domains,
            "is_bridge": len(domains) > 1,
            "source": source
        })
    return results


def log_interaction(noun_profiles, tier_1, tier_2, tier_3):
    """Records the triad, its Kumu domain coordinates, and the Tier 3 synthesis into interactions.db."""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            INSERT INTO interactions (
                created_at, noun_1, noun_2, noun_3,
                domains_1, domains_2, domains_3,
                tier_1, tier_2, tier_3
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now,
            noun_profiles[0]["noun"],
            noun_profiles[1]["noun"],
            noun_profiles[2]["noun"],
            json.dumps(noun_profiles[0]["domains"]),
            json.dumps(noun_profiles[1]["domains"]),
            json.dumps(noun_profiles[2]["domains"]),
            tier_1,
            tier_2,
            tier_3
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Taxonomy] Interaction log warning: {e}")
