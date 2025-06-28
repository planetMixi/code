import pandas as pd
import os
from pathlib import Path

def filter_web_vulnerabilities():
    # Create output directory if it doesn't exist
    output_dir = 'by_weakness'
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the CWE IDs we're interested in
    # CWE-617
    # CWE-79
    # CWE-125
    # CWE-89
    # CWE-918
    cwe_ids = [f'CWE-{i}' for i in ('617', '79', '125', '89', '918')]  # CWE-79 through CWE-88
    print(f"Looking for vulnerabilities: {', '.join(cwe_ids)}")
    
    # Dictionary to store samples by CWE ID
    samples_by_cwe = {cwe: [] for cwe in cwe_ids}
    all_samples = []  # List to store all samples for combined file
    
    # Process each subset file
    for i in range(2, 11):  # Since we have 4 subsets
        subset_file = f'subsets/subset_{i}.json'
        if os.path.exists(subset_file):
            print(f"\nReading {subset_file}...")
            try:
                # Read the subset file
                df = pd.read_json(subset_file, orient='table')
                
                # Filter for each CWE ID
                for cwe_id in cwe_ids:
                    cwe_df = df[df['cwe_id'].str.contains(cwe_id, case=False, na=False)]
                    if not cwe_df.empty:
                        print(f"Found {len(cwe_df)} {cwe_id} samples in {subset_file}")
                        samples_by_cwe[cwe_id].append(cwe_df)
                        all_samples.append(cwe_df)  # Add to combined samples
                    
            except Exception as e:
                print(f"Error processing {subset_file}: {str(e)}")
    
    # Process results for each CWE ID
    for cwe_id, samples in samples_by_cwe.items():
        if samples:
            # Combine samples for this CWE ID
            merged_df = pd.concat(samples, ignore_index=True)
            
            # Save JSON
            output_file = f'{output_dir}/{cwe_id.lower()}_samples.json'
            print(f"\nSaving {len(merged_df)} {cwe_id} samples to {output_file}...")
            merged_df.to_json(output_file, orient='table', indent=2)
            
            print(f"Summary for {cwe_id}:")
            print(f"- Total samples: {len(merged_df)}")
            print(f"- Output file: {output_file}")
        else:
            print(f"\nNo {cwe_id} samples found in any subset")
    
    # # Save combined file with all web vulnerabilities
    # if all_samples:
    #     combined_df = pd.concat(all_samples, ignore_index=True)
    #     combined_file = f'{output_dir}/all_web_vulnerabilities.json'
    #     print(f"\nSaving combined file with {len(combined_df)} total samples to {combined_file}...")
    #     combined_df.to_json(combined_file, orient='table', indent=2)
    #     print(f"Summary for combined file:")
    #     print(f"- Total samples: {len(combined_df)}")
    #     print(f"- Output file: {combined_file}")

if __name__ == "__main__":
    filter_web_vulnerabilities() 