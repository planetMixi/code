import json
import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

from prompts import system_prompt_short, zero_shot_prompt


# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
client = OpenAI(api_key=api_key)


input_file = "by_weakness/cwe-79_samples.json"
output_file = "secom_zero_shot_rq2.csv"
results = []

# Read the JSON file into a DataFrame
df = pd.read_json(input_file, orient='table')

count = 0
for i, row in tqdm(df.iterrows(), total=len(df), desc="Generating SECOM messages"):
    if count >= 5:
        break

    try:
        vuln_id = row.get("vuln_id", "")
        code_diff = row.get("code_diff", "")
        cwe_id = row.get("cwe_id", "")
        original_message = row.get("message", "")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt_short},
                {"role": "user", "content": zero_shot_prompt.replace("<code_diff>", code_diff)}
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

        count += 1  

    except Exception as e:
        generated = f"Error: {str(e)}"



df = pd.DataFrame(results)
df.to_csv(output_file, index=False)
print(f"SECOM messages saved to {output_file}")
