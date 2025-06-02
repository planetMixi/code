import pandas as pd
import os
from openai import OpenAI
from tqdm import tqdm

# Load cleaned dataset
df = pd.read_csv("secom_zero_shot_100_cleaned.csv")

# Select the one-shot example: CVE-2015-8964
example_row = df[df["vuln_id"] == "CVE-2015-8964"].iloc[0]
example_code_diff = example_row["code_diff"]

# Fully filled SECOM-compliant example message (with placeholders where needed)
example_message = """vuln-fix: prevent stale tty field reuse in ldisc drivers (CVE-2015-8964)

(what) Line discipline drivers reused stale tty fields during initialization, risking access to already-freed memory and system instability.

(why) Such reuse could lead to use-after-free errors, especially during line discipline changes where internal memory management is sensitive.

(how) The patch resets tty_struct fields such as receive_room and disc_data before initializing a new line discipline, ensuring safe reuse.

Weakness: CWE-416
Severity: Not specified in diff
CVSS Score: Not specified in diff
Detection Method: KASAN use-after-free trace
Report Link: Not specified in diff
Introduced in: Not specified in diff

Reported-by: Sasha Levin <sasha.levin@oracle.com>
Reviewed-by: Not specified in diff
Co-authored-by: Not specified in diff
Signed-off-by: Peter Hurley <peter@hurleysoftware.com>
Signed-off-by: Greg Kroah-Hartman <gregkh@linuxfoundation.org>

Bug-tracker: Not specified in diff
Resolves: Not specified in diff
See also: Not specified in diff"""

# Filter out the example from the rest of the dataset
targets = df[df["vuln_id"] != "CVE-2015-8964"]

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

results = []

# Loop through each commit and apply one-shot prompt
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
output_file = "secom_oneshot_full_metadata_results.csv"
pd.DataFrame(results).to_csv(output_file, index=False)
print(f" One-shot SECOM messages (with full metadata) saved to {output_file}")
