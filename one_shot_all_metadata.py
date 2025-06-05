import pandas as pd
import os
from openai import OpenAI
from tqdm import tqdm

# Load cleaned dataset
df = pd.read_csv("secom_zero_shot_10_cleaned.csv")

# Select the one-shot example: CVE-2015-8964
example_row = df[df["vuln_id"] == "CVE-2015-8964"].iloc[0]
example_code_diff = example_row["code_diff"]

# Fully filled SECOM-compliant example message (placeholder fields filled)
example_message = """vuln-fix: prevent stale tty field reuse in ldisc drivers (CVE-2015-8964)

Line discipline drivers reused stale tty fields during initialization, risking access to already-freed memory and system instability.

Such reuse could lead to use-after-free errors, especially during line discipline changes where internal memory management is sensitive.

The patch resets tty_struct fields such as receive_room and disc_data before initializing a new line discipline, ensuring safe reuse.

Weakness: CWE-416  
Severity: Not specified in diff  
CVSS: Not specified in diff  
Detection: KASAN use-after-free trace  
Report: Not specified in diff  
Introduced in: Not specified in diff  
Reported-by: Sasha Levin <sasha.levin@oracle.com>  
Signed-off-by: Peter Hurley <peter@hurleysoftware.com>  
Signed-off-by: Greg Kroah-Hartman <gregkh@linuxfoundation.org>  
Bug-tracker: Not specified in diff  
Resolves: Not specified in diff  
See also: Not specified in diff"""

# Filter and limit to 10 target diffs (excluding the example)
targets = df[df["vuln_id"] != "CVE-2015-8964"].head(10)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

results = []

# Generate for 10 commits
for _, row in tqdm(targets.iterrows(), total=len(targets), desc="One-shot full metadata SECOM generation"):
    vuln_id = row["vuln_id"]
    code_diff = row["code_diff"]

    prompt = f"""
You are a security-focused AI assistant. Your task is to generate a SECOM-compliant commit message for the given Git diff.

Use the example below as strict guidance. Follow its structure and style exactly. Include **all** SECOM metadata fields — even if not present in the diff — and mark missing ones with "Not specified in diff".

-------------------------
{example_code_diff}

{example_message}
-------------------------

Now generate a SECOM-compliant commit message for this diff:

<vuln-fix>: <concise subject line> (<{vuln_id}>)

<Three paragraphs: vulnerability, impact, fix (25 words each)>

Metadata (use these exact field names; include all):
Weakness: <...>  
Severity: <...>  
CVSS: <...>  
Detection: <...>  
Report: <...>  
Introduced in: <...>  
Reported-by: <...>  
Signed-off-by: <...>  
Bug-tracker: <...>  
Resolves: <...>  
See also: <...>

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

# Save result
output_file = "secom_oneshot_full_metadata_10.csv"
pd.DataFrame(results).to_csv(output_file, index=False)
print(f"One-shot SECOM messages (full metadata) saved to {output_file}")
