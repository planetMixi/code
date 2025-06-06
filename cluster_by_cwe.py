import pandas as pd
import os

# === CONFIG ===
input_file = "cleaned_diffs_with_cwe_first_500.csv"
output_dir = "clustered_by_cwe"
os.makedirs(output_dir, exist_ok=True)

# === Load enriched data ===
df = pd.read_csv(input_file)

# === Group and save ===
for cwe_id, group in df.groupby("cwe_id"):
    safe_name = cwe_id.replace("/", "_").replace(" ", "_")
    output_path = os.path.join(output_dir, f"commits_{safe_name}.csv")
    group.to_csv(output_path, index=False)
    print(f"✅ Saved {len(group)} diffs to {output_path}")
