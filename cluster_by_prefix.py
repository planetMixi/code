import json
import pandas as pd
import os

input_file = "cleaned_diffs.jsonl"
output_dir = "clustered_by_prefix"
os.makedirs(output_dir, exist_ok=True)

records = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

df = pd.DataFrame(records)

# Extract vuln_id prefix
df["vuln_id_prefix"] = df["vuln_id"].apply(lambda x: x.split("-")[0] if isinstance(x, str) and "-" in x else "UNKNOWN")

# Group and save per prefix
for prefix, group in df.groupby("vuln_id_prefix"):
    filename = f"{output_dir}/commits_{prefix}.csv"
    group.drop(columns=["vuln_id_prefix"]).to_csv(filename, index=False)
    print(f"✅ Saved {len(group)} rows to {filename}")
