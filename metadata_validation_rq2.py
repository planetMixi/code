import pandas as pd
import json
import re
import os

# --- Helpers ---
def severity_from_score(score):
    if score >= 9.0:
        return "critical"
    elif score >= 7.0:
        return "high"
    elif score >= 4.0:
        return "medium"
    else:
        return "low"

def extract_weakness(text):
    match = re.search(r"cwe-\d+", str(text).lower())
    return match.group(0) if match else None

def extract_severity(text):
    for level in ["critical", "high", "medium", "low"]:
        if level in str(text).lower():
            return level
    return None

def extract_cvss(text):
    match = re.search(r"cvss\s*[:=]?\s*(\d+\.\d+)", str(text).lower())
    return float(match.group(1)) if match else None

def extract_vuln_id(text):
    # Match both CVE and GHSA style IDs
    match = re.search(r"(cve-\d{4}-\d+|ghsa-[\w]{4}-[\w]{4}-[\w]{4})", str(text).lower())
    return match.group(0) if match else None

# --- Load data entries from all subsets ---
data_entries = []
for i in range(1, 6):
    with open(f"subsets/subset_{i}.json", "r") as f:
        data_entries.extend(json.load(f)["data"])

entries_by_vuln_id = {entry["vuln_id"]: entry for entry in data_entries}

# --- Load RQ2 generation output ---
df = pd.read_csv("secom_few_shot_1.csv")

# --- Validate metadata ---
results = []

for _, row in df.iterrows():
    vuln_id = row.get("vuln_id")
    entry = entries_by_vuln_id.get(vuln_id)

    if not entry:
        continue  # Skip if no matching original data

    generated_msg = row.get("generated_secom_message", "")

    # Structured truth
    original_cvss = float(entry.get("score", 0.0))
    original_severity = severity_from_score(original_cvss)
    original_cwe_raw = entry.get("cwe_id", "").strip("{}'\"")
    original_cwe = original_cwe_raw.lower() if original_cwe_raw else None
    original_vuln_id = vuln_id.lower()

    # Extracted from generated message
    generated_meta = {
        "weakness": extract_weakness(generated_msg),
        "severity": extract_severity(generated_msg),
        "cvss": extract_cvss(generated_msg),
        "vuln_id": extract_vuln_id(generated_msg),
    }

    result = {
        "vuln_id": vuln_id,
        "generated_vuln_id": generated_meta["vuln_id"],
        "vuln_id_match": original_vuln_id == generated_meta["vuln_id"],

        "original_weakness": original_cwe,
        "generated_weakness": generated_meta["weakness"],
        "weakness_match": original_cwe == generated_meta["weakness"],

        "original_severity": original_severity,
        "generated_severity": generated_meta["severity"],
        "severity_match": original_severity == generated_meta["severity"],

        "original_cvss": original_cvss,
        "generated_cvss": generated_meta["cvss"],
        "cvss_match": abs(original_cvss - generated_meta["cvss"]) < 0.1
                      if generated_meta["cvss"] is not None else False
    }

    results.append(result)

# --- Save validation output ---
validation_df = pd.DataFrame(results)
validation_df.to_csv("secom_few_shot_rq2_metadata_validation.csv", index=False)
print(f"Validation complete: {len(validation_df)} entries saved.")
