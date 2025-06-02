import pandas as pd
import os
from openai import OpenAI
from tqdm import tqdm

# Load cleaned dataset
df = pd.read_csv("secom_zero_shot_100_cleaned.csv")

# Select the one-shot example: CVE-2015-8964
example_row = df[df["vuln_id"] == "CVE-2015-8964"].iloc[0]
example_code_diff = example_row["code_diff"]
example_message = example_row["generated_secom_message"]

# Filter out the example from the rest of the dataset
targets = df[df["vuln_id"] != "CVE-2015-8964"]

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

results = []

for _, row in tqdm(targets.iterrows(), total=len(targets), desc="One-shot SECOM generation"):
    vuln_id = row["vuln_id"]
    code_diff = row["code_diff"]

    prompt = f"""
You are a security-focused AI assistant who generates SECOM-compliant commit messages from Git diffs.

Here is an example:
---
Git Diff:
{example_code_diff}

SECOM Commit Message:
{example_message}
---

Now generate a SECOM-compliant commit message for this new diff:
Git Diff:
{code_diff}

SECOM Commit Message:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate SECOM-compliant commit messages."},
                {"role": "user", "content": prompt}
            ]
        )
        generated_message = response.choices[0].message.content

    except Exception as e:
        generated_message = f"Error: {str(e)}"

    results.append({
        "vuln_id": vuln_id,
        "code_diff": code_diff,
        "generated_secom_message": generated_message
    })

# Save results
pd.DataFrame(results).to_csv("secom_oneshot_results.csv", index=False)
print(" One-shot SECOM messages saved to secom_oneshot_results.csv")
