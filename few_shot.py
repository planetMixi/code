import json
import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

from prompts import system_prompt_short, few_shot_prompt

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
client = OpenAI(api_key=api_key)

input_file = "subsets/subset_1.json"
output_file = "secom_few_shot_1.csv"
results = []

df = pd.read_json(input_file, orient='table')

# Process entries 1–10 (skip index 0)
for i, row in tqdm(df.head(10).iterrows(), total=10, desc="Generating SECOM messages (Few-Shot)"):

    try:
        vuln_id = str(row.get("vuln_id", "") or "")
        code_diff = str(row.get("code_diff", "") or "")
        cwe_id = str(row.get("cwe_id", "")).strip("{}' ")
        original_message = str(row.get("message", "") or "")

        few_shot_prompt_safe = few_shot_prompt.replace("{", "{{").replace("}", "}}").replace("{{code_diff}}", "{code_diff}")

        user_prompt_filled = few_shot_prompt_safe.replace("{code_diff}", code_diff)

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

# Save results
df = pd.DataFrame(results)[['id', 'cwe_id', 'vuln_id', 'code_diff', 'original_message', 'generated_secom_message']]
df.to_csv(output_file, index=False)
print(f"Few-shot SECOM messages saved to {output_file}")
