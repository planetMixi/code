import requests
import time
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
nvd_api_key = os.getenv("NVD_API_KEY")


def get_cwe_from_cve(cve_id, api_key=None):
    if not cve_id.startswith("CVE-"):
        return "CWE-Unsupported-ID"

    url = f"https://services.nvd.nist.gov/rest/json/cve/1.0/{cve_id}"
    headers = {"apiKey": api_key} if api_key else {}

    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            items = data.get("result", {}).get("CVE_Items", [])
            if items:
                for entry in items[0]["cve"]["problemtype"]["problemtype_data"]:
                    for desc in entry.get("description", []):
                        value = desc.get("value", "")
                        if "CWE-" in value and value != "NVD-CWE-noinfo":
                            return value

        print(f"⚠️ No CWE found for {cve_id} in NVD response.")
    except Exception as e:
        print(f"❌ NVD lookup failed for {cve_id}: {e}")

    return "CWE-Unknown"



def get_cwe_from_gpt(diff, max_chars=8192):  # you can tune this lower if needed
    truncated_diff = diff[:max_chars]

    prompt = f"""
You are a vulnerability classification expert.

Based ONLY on the following Git diff, return the most applicable CWE identifier (e.g., CWE-79). Do not explain. Just return the CWE ID.

Git diff:
{truncated_diff}

Answer:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        return result if result.startswith("CWE-") else "CWE-Unknown"
    except Exception as e:
        print(f"❌ GPT classification failed: {e}")
        return "CWE-Unknown"

