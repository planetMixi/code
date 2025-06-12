import json
import os
import random
import argparse
import pandas as pd

def extract_subset(input_file, subset_dir="subsets"):
    # Create subsets directory if it doesn't exist
    if not os.path.exists(subset_dir):
        os.makedirs(subset_dir)
    
    # Get the next subset ID
    existing_subsets = [f for f in os.listdir(subset_dir) if f.startswith("subset_") and f.endswith(".json")]
    if existing_subsets:
        max_id = max([int(f.split("_")[1].split(".")[0]) for f in existing_subsets])
        next_id = max_id + 1
    else:
        next_id = 1
    
    # Load the data using pandas
    try:
        # The orient='table' automatically handles the schema/data structure
        df = pd.read_json(input_file, orient='table')
        print(f"Loaded dataset with {len(df)} records")
    except ValueError:
        # If not in table format, try standard JSON
        try:
            df = pd.read_json(input_file)
            print(f"Loaded dataset with {len(df)} records (standard JSON format)")
        except Exception as e:
            print(f"Error: Unable to read {input_file}: {str(e)}")
            return
    
    # Create or load a tracking file to keep track of used indices
    tracking_file = f"{input_file}.tracking"
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as f:
            used_indices = set(json.load(f))
    else:
        used_indices = set()
    
    # Get available data points (indices not in used_indices)
    all_indices = set(range(len(df)))
    available_indices = list(all_indices - used_indices)
    
    if len(available_indices) < 100:
        print(f"Warning: Only {len(available_indices)} data points available for extraction")
        if len(available_indices) == 0:
            print("No more data points available. All have been used.")
            return
    
    # Select 100 random data points (or all available if less than 100)
    to_extract = min(100, len(available_indices))
    selected_indices = random.sample(available_indices, to_extract)
    
    # Create subset dataframe
    subset_df = df.iloc[selected_indices].copy()
    
    # Update the used indices
    used_indices.update(selected_indices)
    
    # Save the subset
    subset_file = os.path.join(subset_dir, f"subset_{next_id}.json")
    subset_df.to_json(subset_file, orient='table', indent=4)
    
    # Save the updated tracking file
    with open(tracking_file, 'w') as f:
        json.dump(list(used_indices), f)
    
    print(f"Extracted {to_extract} data points to {subset_file}")
    print(f"Remaining unused data points: {len(all_indices) - len(used_indices)}")
    
    return subset_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract subsets of data from a JSON file')
    parser.add_argument('--input', '-i', default="dataset/secommits_filtered.json",
                        help='Path to the input JSON file (default: dataset/secommits_filtered.json)')
    parser.add_argument('--output-dir', '-o', default="subsets",
                        help='Directory to store subset files (default: subsets)')
    
    args = parser.parse_args()
    
    extract_subset(args.input, args.output_dir) 