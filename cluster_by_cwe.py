import json
import re
import pandas as pd
import os

# === Config ===
input_path = "cleaned_diffs.jsonl"
output_dir = "cwe_clusters_first_100"
os.makedirs(output_dir, exist_ok=True)

# === Load First 100 Records ===
records = []
with open(input_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 100:
            break
        record = json.loads(line)
        records.append(record)

# === Extract CWE from code_diff (based on CVE metadata) ===
def extract_cwe_id(diff_text):
    match = re.search(r"\bCWE-(\d{1,5})\b", diff_text)
    if match:
        return f"CWE-{match.group(1)}"
    else:
        return "CWE-Unknown"

for record in records:
    record["cwe_id"] = extract_cwe_id(record.get("code_diff", ""))

# === Convert to DataFrame ===
df = pd.DataFrame(records)

# === Group by CWE ID and Save Each Cluster ===
grouped = df.groupby("cwe_id")

for cwe_id, group in grouped:
    safe_cwe = cwe_id.replace("/", "_").replace("\\", "_")
    filename = os.path.join(output_dir, f"cluster_{safe_cwe}.csv")
    group.to_csv(filename, index=False)
    print(f"Saved {len(group)} diffs to {filename}")

print(f"\n✅ Clustering complete. All CWE-based clusters saved in '{output_dir}/'")
