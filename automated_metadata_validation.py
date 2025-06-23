import pandas as pd
import json
import re
from difflib import SequenceMatcher

# Load original data entries (first 5 from JSON)
with open("subsets/subset_1.json", "r") as f:
    raw_data = json.load(f)

original_entries = raw_data["data"][:10]

# Load generated SECOM messages
df_generated = pd.read_csv("secom_few_shot_1.csv")

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
    match = re.search(r"cwe-\d+", text.lower())
    return match.group(0) if match else None

def extract_severity(text):
    for level in ["critical", "high", "medium", "low"]:
        if level in text.lower():
            return level
    return None

def extract_cvss(text):
    match = re.search(r"cvss\s*[:]\s*(\d+\.\d+)", text.lower())
    return float(match.group(1)) if match else None

# --- Validation Process ---

validation_results = []

for original in original_entries:
    vuln_id = original.get("vuln_id", "")
    matching_row = df_generated[df_generated["vuln_id"] == vuln_id]

    if matching_row.empty:
        continue  # No match found

    generated_msg = matching_row.iloc[0]["generated_secom_message"]

    original_cvss = float(original.get("score", 0.0))
    original_severity = severity_from_score(original_cvss)

    # Parse original CWE string safely
    original_cwe_raw = original.get("cwe_id", "").strip("{}'\"")
    original_cwe = original_cwe_raw.lower() if original_cwe_raw else None

    # Extract metadata from generated message
    generated_meta = {
        "weakness": extract_weakness(generated_msg),
        "severity": extract_severity(generated_msg),
        "cvss": extract_cvss(generated_msg),
    }

    result = {
        "original_vuln_id": vuln_id,
        "generated_vuln_id": matching_row.iloc[0]["vuln_id"],
        "vuln_id_match": vuln_id == matching_row.iloc[0]["vuln_id"], 

        "original_weakness": original_cwe,
        "generated_weakness": generated_meta["weakness"],
        "weakness_match": original_cwe == generated_meta["weakness"],

        "original_severity": original_severity,
        "generated_severity": generated_meta["severity"],
        "severity_match": original_severity == generated_meta["severity"],

        "original_cvss": original_cvss,
        "generated_cvss": generated_meta["cvss"],
        "cvss_match": abs(original_cvss - generated_meta["cvss"]) < 0.1 if generated_meta["cvss"] is not None else False,
    }


    validation_results.append(result)

# Save results
validation_df = pd.DataFrame(validation_results)
validation_df.to_csv("secom_few_shot_1_metadata_validation.csv", index=False)
print("Validation complete.")
