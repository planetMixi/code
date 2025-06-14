import json
import os
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

from prompts import system_prompt, one_shot_prompt

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
client = OpenAI(api_key=api_key)

input_file = "subsets/subset_10.json"
output_file = "secom_one_shot_10.csv"
results = []

# Read the JSON file into a DataFrame
df = pd.read_json(input_file, orient='table')

# Process each row in the DataFrame
for i, row in tqdm(df.iterrows(), total=1, desc="Generating SECOM messages (One-Shot)"):
    try:
        vuln_id = row.get("vuln_id", "")
        code_diff = row.get("code_diff", "")
        cwe_id = row.get("cwe_id", "")
        original_message = row.get("message", "")

        # Inject the target diff into the user prompt
        user_prompt_filled = one_shot_prompt.replace("<code_diff>", code_diff).replace("GHSA-xxxx-yyyy-zzzz", vuln_id)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_filled}
            ]
        )

        generated = response.choices[0].message.content
        generated = generated.replace("```", "").strip()
        print(generated)

        results.append({
            "id": i,
            "cwe_id": cwe_id,
            "vuln_id": vuln_id,
            "code_diff": code_diff,
            "original_message": original_message,
            "generated_secom_message": generated
        })

        # REMOVE THIS WHEN YOU WANT TO RUN THE WHOLE SET
        break

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

# Save to CSV
df = pd.DataFrame(results)
df.to_csv(output_file, index=False)
print(f"First SECOM one-shot messages saved to {output_file}")
