import json
import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

input_file = "cleaned_diffs.jsonl"
output_file = "secom_zero_shot_10.csv"
results = []

# Limit to first 20 commits
with open(input_file, "r", encoding="utf-8") as f:
    for i, line in tqdm(enumerate(f), total=10, desc="Generating SECOM messages"):
        if i >= 20:
            break

        try:
            data = json.loads(line)
            vuln_id = data.get("vuln_id", "")
            code_diff = data.get("code_diff", "")

            prompt = f"""
You are a security patch expert. Generate a SECOM-compliant commit message based only on the Git diff below.

Follow this exact SECOM format:

<vuln-fix>: <concise subject line> (<{vuln_id}>)

<One paragraph describing the vulnerability (~25 words)>  
<One paragraph explaining the impact (~25 words)>  
<One paragraph describing the fix (~25 words)>

<Only include metadata if explicitly shown in the diff. Use the exact field names below:>

Weakness: <Weakness Name/CWE-ID>  
Severity: <Low, Medium, High, Critical>  
CVSS: <Severity numerical representation>  
Detection: <Method, Tool>  
Report: <Report Link>  
Introduced in: <Commit Hash>  
Reported-by: <Name> (<Email>)  
Signed-off-by: <Name> (<Email>)  
Bug-tracker: <Bug-tracker Link>  
Resolves: <Issue/PR No.>  
See also: <Issue/PR No.>

⚠️ Do not add headings like “Header”, “Body”, “Metadata”.  
⚠️ Do not start the message with “Fix:” or any fabricated keywords.  
⚠️ Only use what’s visible in the diff — no assumptions.

---

Git Diff:
{code_diff}

Commit message:
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

df = pd.DataFrame(results)
df.to_csv(output_file, index=False)
print(f"First 10 SECOM messages saved to {output_file}")
