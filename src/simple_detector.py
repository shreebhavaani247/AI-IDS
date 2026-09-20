# src/simple_detector.py
import os, json, re
from automaton import build_automaton, search_line

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERN_FILE = os.path.join(BASE_DIR, "signatures", "patterns.txt")
INPUT_LOG    = os.path.join(BASE_DIR, "data", "sample_traffic.log")
OUTPUT       = os.path.join(BASE_DIR, "output", "alerts.jsonl")

TS_RE = re.compile(r'\[(.*?)\]')
IP_RE = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3})')

def main():
    automaton = build_automaton(PATTERN_FILE)
    alerts = []

    with open(INPUT_LOG, encoding='utf-8', errors='replace') as fh:
        for lineno, line in enumerate(fh, start=1):
            matches = search_line(automaton, line)
            if matches:
                ts = TS_RE.search(line).group(1) if TS_RE.search(line) else None
                ip = IP_RE.search(line).group(1) if IP_RE.search(line) else None
                for m in matches:
                    alert = {
                        "timestamp": ts,
                        "line_no": lineno,
                        "src_ip": ip,
                        "matched_pattern": m['pattern'],
                        "severity": m['severity'],
                        "raw_line": line.strip()
                    }
                    alerts.append(alert)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as out:
        for a in alerts:
            out.write(json.dumps(a, ensure_ascii=False) + '\n')

    print(f"Found {len(alerts)} alerts -> {OUTPUT}")

if __name__ == '__main__':
    main()
