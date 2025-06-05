import pandas as pd
import os
from openai import OpenAI
from tqdm import tqdm

# Load cleaned dataset
df = pd.read_csv("secom_zero_shot_10_cleaned.csv")

# Select the one-shot example: CVE-2015-8964
example_row = df[df["vuln_id"] == "CVE-2015-8964"].iloc[0]
example_code_diff = example_row["code_diff"]
example_message = example_row["generated_secom_message"]

# Filter out the example and keep only the first 10 others
targets = df[df["vuln_id"] != "CVE-2015-8964"].head(10)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

results = []

for _, row in tqdm(targets.iterrows(), total=len(targets), desc="One-shot SECOM generation"):
    vuln_id = row["vuln_id"]
    code_diff = row["code_diff"]

    prompt = f"""
You are a security-focused AI that writes SECOM-compliant commit messages using only Git diffs.

Here is an example message you must follow precisely:

-------------------------
{example_code_diff}

{example_message}
-------------------------

Now write a SECOM-compliant message for this new diff:

- Use the exact SECOM format.
- No section labels.
- Start with: <vuln-fix>: <header/subject> (<{vuln_id}>)
- Follow with 3 concise paragraphs (vulnerability, impact, fix).
- Only include metadata fields shown in the diff. Use exact field names:
  - Weakness, Severity, CVSS, Detection, Report, Introduced in, Reported-by, Signed-off-by, Bug-tracker, Resolves, See also.

❌ Do not invent anything.
❌ Do not use “Fix:” or “Fixes:” at the start.
❌ Do not include labels like “Body”, “Metadata”, “Header”.

---

Git Diff:
{code_diff}

Commit message:
"""



    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate SECOM-compliant commit messages."},
                {"role": "user", "content": prompt}
            ]
        )
        generated_message = response.choices[0].message.content.strip()

    except Exception as e:
        generated_message = f"Error: {str(e)}"

    results.append({
        "vuln_id": vuln_id,
        "code_diff": code_diff,
        "generated_secom_message": generated_message
    })

# Save results
pd.DataFrame(results).to_csv("secom_oneshot_results.csv", index=False)
print("One-shot SECOM messages saved to secom_oneshot_results.csv")
