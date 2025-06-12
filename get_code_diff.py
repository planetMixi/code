#!/usr/bin/env python3
import pandas as pd
import os
import argparse
import requests

import re

# clean diff information
def extract_full_code_with_changes(diff_text):
    code_with_context = []
    capture = False

    for line in diff_text.splitlines():
        # Start capturing after the first diff section begins
        if line.startswith("diff --git "):
            capture = True
            continue

        if capture:
            # Capture lines that are part of the code section, skipping metadata lines
            if not (line.startswith("From ") or 
                    line.startswith("Date: ") or 
                    line.startswith("Subject: ") or
                    re.match(r'^\s*\d+ files changed', line) or
                    re.match(r'index ', line) or
                    re.match(r'^@@ ', line) or
                    line.startswith('---') or line.startswith('+++')):
                code_with_context.append(line)
    
    return "\n".join(code_with_context)

def read_subset(subset_file):
    """
    Read a subset JSON file and convert it to a pandas DataFrame.
    
    Args:
        subset_file (str): Path to the subset JSON file
        
    Returns:
        pandas.DataFrame: DataFrame containing the subset data
    """
    # Check if file exists
    if not os.path.exists(subset_file):
        raise FileNotFoundError(f"Subset file not found: {subset_file}")
    
    # Read the JSON file using pandas (try table format first)
    try:
        df = pd.read_json(subset_file, orient='table')
        print(f"Successfully loaded table-oriented subset with {len(df)} records and {len(df.columns)} columns.")
    except ValueError:
        # Fall back to standard JSON if not in table format
        try:
            df = pd.read_json(subset_file)
            print(f"Successfully loaded standard JSON subset with {len(df)} records and {len(df.columns)} columns.")
        except Exception as e:
            raise ValueError(f"Error reading {subset_file}: {str(e)}")
    
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read a subset JSON file and convert it to a pandas DataFrame')
    parser.add_argument('subset_file', help='Path to the subset JSON file')
    parser.add_argument('--csv', '-c', action='store_true', help='Save the DataFrame to a CSV file')
    parser.add_argument('--output', '-o', help='Path to save the CSV file (used with --csv)')
    
    args = parser.parse_args()
    
    # Read the subset file
    df = read_subset(args.subset_file)

    for index, row in df.iterrows():
        df.at[index, "code_diff"] = extract_full_code_with_changes(row['patch_content'])
    # save to json file
    df.to_json(args.output, orient='table', indent=4)
    
    