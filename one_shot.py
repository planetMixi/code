import json
import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

from prompts import system_prompt_short, one_shot_prompt

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
client = OpenAI(api_key=api_key)

input_file = "by_weakness/cwe-79_samples.json"
output_file = "secom_one_shot_79.csv"
results = []

# Read the JSON file into a DataFrame
df = pd.read_json(input_file, orient='table')

# Loop and process only the second entry (index 1)
for i, row in tqdm(df.iterrows(), total=len(df), desc="Generating SECOM messages (One-Shot Test)"):
    if i < 1 or i > 5:
        continue   # Only process the second row

    try:
        vuln_id = str(row.get("vuln_id", "") or "")
        code_diff = str(row.get("code_diff", "") or "")
        cwe_id = str(row.get("cwe_id", "")).strip("{}' ")
        original_message = str(row.get("message", "") or "")
        author = str(row.get("author", "") or "")
        commit_datetime = str(row.get("commit_datetime", "") or "")

        coauthors = "\n".join([
            line for line in original_message.split("\n")
            if "Co-authored-by:" in line
        ])

        # Fill in prompt with all known metadata
        user_prompt_filled = one_shot_prompt.format(
            vuln_id=vuln_id,
            cwe_id=cwe_id,
            author=author,
            commit_datetime=commit_datetime,
            commit_message=original_message,
            coauthors=coauthors,
            code_diff=code_diff
        )

        # Call the model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt_short},
                {"role": "user", "content": user_prompt_filled}
            ]
        )

        generated = response.choices[0].message.content.replace("```", "").strip()
        print(generated)

        results.append({
            "id": i,
            "cwe_id": cwe_id,
            "vuln_id": vuln_id,
            "code_diff": code_diff,
            "original_message": original_message,
            "generated_secom_message": generated
        })


    except Exception as e:
        print(f"Error processing row {i}: {e}")
        results.append({
            "id": i,
            "cwe_id": cwe_id,
            "vuln_id": vuln_id,
            "code_diff": code_diff,
            "original_message": original_message,
            "generated_secom_message": f"Error: {str(e)}"
        })

# Save results with exact column order
df = pd.DataFrame(results)[['id', 'cwe_id', 'vuln_id', 'code_diff', 'original_message', 'generated_secom_message']]
df.to_csv(output_file, index=False)
print(f"One-shot SECOM message saved to {output_file}")
