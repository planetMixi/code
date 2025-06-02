import json
import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

input_file = "cleaned_diffs.jsonl"
output_file = "secom_zero_shot_100.csv"
results = []

# Limit to first 100 commits
with open(input_file, "r", encoding="utf-8") as f:
    
    for i, line in tqdm(enumerate(f), total=100, desc="Generating SECOM messages"):
        if i >= 100:
            break

        try:
            data = json.loads(line)
            vuln_id = data.get("vuln_id", "")
            code_diff = data.get("code_diff", "")

            prompt = f"""
You are an AI expert in security patches and commit documentation.

Your task is to strictly generate a SECOM-compliant security commit message based **only on the provided Git diff**, ensuring maximum SECOM compliance.

---

🧷 SECOM Commit Format:

Header:
<vuln-fix>: <header/subject> ({vuln_id})

Body:
(what) Clearly describe the vulnerability exactly as it appears in the diff.  
(why) Explain the potential impact strictly based on the diff.  
(how) Describe how the patch fixes the issue, using only changes found in the diff.

Metadata (Only include fields **if present** in the diff. Otherwise, **omit the field entirely** — no placeholders.)

Contributor Metadata and References should also only be included if mentioned in the diff.

⚠️ STRICT RULES:
- Use only the Git diff as your information source.  
- Do not fabricate or hallucinate any content.  
- If a field is not in the diff, leave it out completely.  
- Follow SECOM structure and tone with high precision.  
- Body should have ~75 words total, 25 per (what/why/how) section.  
- Keep the header concise (~50 characters, max 72).

---

Git Diff (For Analysis and Extraction):

{code_diff}

---

Expected Output Format:

<vuln-fix>: <header/subject> ({vuln_id})

(what) <25-word description>  
(why) <25-word impact>  
(how) <25-word fix>

<Include metadata, contributors, references only if explicitly in diff>
"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You generate SECOM-compliant commit messages based only on diffs."},
                    {"role": "user", "content": prompt}
                ]
            )

            generated = response.choices[0].message.content

        except Exception as e:
            generated = f"Error: {str(e)}"

        results.append({
            "vuln_id": vuln_id,
            "code_diff": code_diff,
            "generated_secom_message": generated
        })


# Save to CSV
df = pd.DataFrame(results)
df.to_csv(output_file, index=False)
print(f"✅ First 100 SECOM messages saved to {output_file}")
