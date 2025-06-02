import json

input_path = "secommits_llms_sample.jsonl"  
output_path = "cleaned_diffs.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        try:
            entry = json.loads(line)
            cleaned_entry = {
                "vuln_id": entry.get("vuln_id", ""),
                "code_diff": entry.get("patch_content", "")
            }
            outfile.write(json.dumps(cleaned_entry) + "\n")
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON line: {e}")
