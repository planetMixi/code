import json
import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT_SHORT, few_shot_prompt

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
client = OpenAI(api_key=api_key)

input_file = "by_weakness/cwe-79_samples.json"
output_file = "secom_few_shot_cwe79.csv"
results = []

df = pd.read_json(input_file, orient='table')

# count = 0
for i, row in tqdm(df.iterrows(), total=len(df), desc="Generating SECOM messages"):
    # if count >= 5:
    #     break
    try:
        vuln_id = str(row.get("vuln_id", "") or "")
        code_diff = str(row.get("code_diff", "") or "")
        cwe_id = str(row.get("cwe_id", "")).strip("{}' ")
        original_message = str(row.get("message", "") or "")

        few_shot_prompt_safe = few_shot_prompt.replace("{", "{{").replace("}", "}}").replace("{{code_diff}}", "{code_diff}")
        user_prompt_filled = few_shot_prompt_safe.replace("{code_diff}", code_diff)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SHORT},
                {"role": "user", "content": user_prompt_filled}
            ],
            temperature=0.0,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
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
        # count += 1 

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
        # count += 1  

# Save results
df = pd.DataFrame(results)[['id', 'cwe_id', 'vuln_id', 'code_diff', 'original_message', 'generated_secom_message']]
df.to_csv(output_file, index=False)
print(f"Few-shot SECOM messages saved to {output_file}")
