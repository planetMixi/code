import json
import pandas as pd
import os
import time
from cwe_from_cve import get_cwe_from_cve, get_cwe_from_gpt

input_path = "cleaned_diffs.jsonl"
output_file = "cleaned_diffs_with_cwe_first_500.csv"
nvd_api_key = os.getenv("NVD_API_KEY")

records = []

# Load first 100 diffs
with open(input_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 500:
            break
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

# Enrich with CWE (with fallback to GPT if NVD fails)
for record in records:
    vuln_id = record.get("vuln_id", "")
    diff = record.get("code_diff", "")

    cwe_id = "CWE-Unknown"

    if vuln_id.startswith("CVE-"):
        cwe_id = get_cwe_from_cve(vuln_id, api_key=nvd_api_key)
        time.sleep(0.6)

    # Fallback: Use GPT if NVD failed or returned unknown
    if cwe_id == "CWE-Unknown":
        cwe_id = get_cwe_from_gpt(diff)
        time.sleep(1.0)

    record["cwe_id"] = cwe_id


# Save output
df = pd.DataFrame(records)
df.to_csv(output_file, index=False)
print(f"✅ Saved enriched dataset to {output_file}")
