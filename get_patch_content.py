#!/usr/bin/env python3
import pandas as pd
import os
import argparse
import requests

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
        #print(row['vuln_id'], eval(row["files"]).keys(), row['commit_href'])
        response = requests.get(f"{row['commit_href']}.patch")
        print(f"{row['commit_href']}.patch")
        if response.status_code == 200:
            page_content = response.text  # HTML content of the page
            df.at[index, "patch_content"] = page_content.strip()
        else:
            print(f"Failed to retrieve page. Status code: {response.status_code} | {row['commit_href']}")
    
    # save to json file
    df.to_json(args.output, orient='table', index=False)
    
    