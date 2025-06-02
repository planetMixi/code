import json
import pandas as pd
import os

# Load input
input_file = "cleaned_diffs.jsonl"
output_dir = "clustered_by_patch_type"
os.makedirs(output_dir, exist_ok=True)

records = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

df = pd.DataFrame(records)

# Define keyword-based patch categories
patch_categories = {
    "buffer_overflow": ["memcpy", "strcpy", "buffer", "overflow", "bounds", "CWE-120"],
    "xss": ["sanitize", "html", "escape", "script", "CWE-79"],
    "auth": ["auth", "login", "token", "jwt", "credential"],
    "access_control": ["permission", "privilege", "access check", "ACL", "is_admin"],
    "crypto": ["openssl", "mbedtls", "cipher", "key", "encrypt", "decrypt", "TLS"],
    "race_condition": ["mutex", "thread", "race", "atomic", "lock", "concurrent"],
    "config": ["config", "configuration", "parameter", "setting", "flag"],
    "input_validation": ["validate", "regex", "input", "sanitize", "check", "assert"]
}

# Prepare an empty dict to hold DataFrames per category
category_buckets = {key: [] for key in patch_categories.keys()}
category_buckets["unknown"] = []

# Populate buckets (commits can go into multiple buckets)
for _, row in df.iterrows():
    added = False
    diff_text = row["code_diff"].lower() if isinstance(row["code_diff"], str) else ""
    
    for category, keywords in patch_categories.items():
        if any(keyword.lower() in diff_text for keyword in keywords):
            category_buckets[category].append(row)
            added = True
    
    if not added:
        category_buckets["unknown"].append(row)

# Save each category to its own CSV
for category, entries in category_buckets.items():
    if entries:
        pd.DataFrame(entries).to_csv(f"{output_dir}/commits_{category}.csv", index=False)
        print(f"✅ Saved {len(entries)} rows to commits_{category}.csv")
