# src/automaton.py
import ahocorasick
import os

def build_automaton(pattern_file):
    """
    Build Aho-Corasick automaton from patterns.txt
    """
    A = ahocorasick.Automaton()

    with open(pattern_file, encoding='utf-8') as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            pid = parts[0].strip() if parts[0].strip() else f"p_{lineno:03d}"
            pattern = parts[1].strip().lower()
            severity = parts[2].strip().lower() if len(parts) > 2 else "medium"
            # store (id, pattern, severity) in automaton
            A.add_word(pattern, (pid, pattern, severity))

    A.make_automaton()  # finalize the automaton
    return A

def search_line(automaton, line):
    """
    Scan a line and return all matched patterns as a list of dicts
    """
    matches = []
    line_lower = line.lower()
    for end_index, (pid, pattern, severity) in automaton.iter(line_lower):
        start_index = end_index - len(pattern) + 1
        matches.append({
            "id": pid,
            "pattern": pattern,
            "severity": severity, 
            "start": start_index,
            "end": end_index
        })
    return matches
