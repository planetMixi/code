import json
import pandas as pd
import os
import re
from collections import Counter

# Input & output setup
input_file = "cleaned_diffs.jsonl"
output_dir = "clustered_by_language"
os.makedirs(output_dir, exist_ok=True)

# Load JSONL
records = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

df = pd.DataFrame(records)

# Define file extension to language mapping
language_map = {
    "c_cpp": [".c", ".cpp", ".cc", ".h", ".hpp"],
    "python": [".py"],
    "java": [".java"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "go": [".go"],
    "rust": [".rs"],
    "php": [".php"],
    "shell": [".sh", ".bash", ".zsh"],
    "ruby": [".rb"],
    "html_css": [".html", ".css"]
}

# Function to extract primary language from diff headers
def detect_primary_language(diff_text):
    if not isinstance(diff_text, str):
        return "unknown"

    ext_count = Counter()
    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            matches = re.findall(r'\b[a-zA-Z0-9_\-/]+\.(\w+)\b', line)
            for ext in matches:
                ext = f".{ext.lower()}"
                for lang, extensions in language_map.items():
                    if ext in extensions:
                        ext_count[lang] += 1

    return ext_count.most_common(1)[0][0] if ext_count else "unknown"

# Classify each commit
df["primary_language"] = df["code_diff"].apply(detect_primary_language)

# Save master annotated CSV
df.to_csv("commits_primary_language.csv", index=False)
print("✅ Saved full dataset with primary_language column to commits_primary_language.csv")

# Save individual files per primary language
for lang, group in df.groupby("primary_language"):
    filename = f"{output_dir}/commits_{lang}.csv"
    group.drop(columns=["primary_language"]).to_csv(filename, index=False)
    print(f"✅ Saved {len(group)} rows to {filename}")
