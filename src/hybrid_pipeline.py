import argparse
import datetime
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from automaton import build_automaton, search_line
from preprocess import preprocess_line
from check_columns import check_columns

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_ai_model(model_path):
    logging.info(f"Loading AI model from {model_path}")
    return joblib.load(model_path)


def load_signatures(patterns_file):
    logging.info("Loading automaton using build_automaton()")
    return build_automaton(patterns_file)


def convert_np(obj):
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    return obj


def process_log_line(line, automaton, model, feature_columns, threshold=0.6):
    """
    Process one log line through signature + AI detectors
    Returns alert dict or None
    """
    # --- Signature detection ---
    matched = search_line(automaton, line)
    signature_hit = len(matched) > 0

    # --- AI detection ---
    try:
        df = pd.DataFrame([{"raw": line.strip()}])
        df = preprocess_line(df)
        df = check_columns(df, feature_columns)

        if not df.empty:
            proba = model.predict_proba(df)[0][1]  # anomaly probability
            ai_hit = proba >= threshold
        else:
            ai_hit = False
            proba = 0.0
    except Exception as e:
        logging.error(f"AI processing failed for line: {line.strip()} | {e}")
        ai_hit, proba = False, 0.0

    # --- Decision logic with better cloud handling ---
    if signature_hit and ai_hit:
        priority = "Critical"
    elif signature_hit:
        priority = "High"
    elif ai_hit:
        # AI-only hit: upgrade to High if probability is strong
        if proba >= 0.8:
            priority = "High"
        else:
            priority = "Medium"
    else:
        return None

    # --- Logging for debugging ---
    logging.debug(f"Signature hit: {signature_hit}, AI proba: {proba}, Priority: {priority}")

    # --- Build alert object ---
    alert = {
        "id": f"alert-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f')}",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "priority": priority,
        "signature_match": matched,
        "ai_score": float(round(proba, 3)),
        "raw_line": line.strip(),
    }
    return alert


def run_pipeline(input_file, patterns_file, model_file, output_file):
    automaton = load_signatures(patterns_file)
    model = load_ai_model(model_file)

    # Extract training feature columns
    if hasattr(model, "feature_names_in_"):
        feature_columns = list(model.feature_names_in_)
    else:
        raise ValueError("Model does not have feature_names_in_ attribute. Re-train with sklearn/xgboost interface.")

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    fout = open(output_file, "w")

    count, alerts_written = 0, 0

    with open(input_file, "r") as f:
        for line in f:
            count += 1
            alert = process_log_line(line, automaton, model, feature_columns)
            if alert:
                fout.write(json.dumps(alert, default=convert_np) + "\n")
                alerts_written += 1
                logging.info(f"ALERT {alert['priority']} {alert['id']}")

    fout.close()
    logging.info(f"Processed {count} lines, wrote {alerts_written} alerts to {output_file}")
    logging.info("Hybrid pipeline finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hybrid IDS Pipeline (Signatures + AI)")
    parser.add_argument("--input", required=True, help="Input traffic log file")
    parser.add_argument("--patterns", required=True, help="Signature patterns file")
    parser.add_argument("--model", required=True, help="Trained AI model file")
    parser.add_argument("--output", required=True, help="Output alerts JSONL file")

    args = parser.parse_args()
    run_pipeline(args.input, args.patterns, args.model, args.output)
