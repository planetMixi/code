import json
import os
import random
import argparse

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
    
    # Load the data
    try:
        with open(input_file, 'r') as f:
            full_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not a valid JSON file")
        return

    # Handle the specific structure with 'schema' and 'data' keys
    if 'schema' in full_data and 'data' in full_data:
        schema = full_data['schema']
        data = full_data['data']
    else:
        data = full_data
        schema = None
    
    # Create or load a tracking file to keep track of used indices
    tracking_file = f"{input_file}.tracking"
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as f:
            used_indices = set(json.load(f))
    else:
        used_indices = set()
    
    # Get available data points (indices not in used_indices)
    all_indices = set(range(len(data)))
    available_indices = list(all_indices - used_indices)
    
    if len(available_indices) < 100:
        print(f"Warning: Only {len(available_indices)} data points available for extraction")
        if len(available_indices) == 0:
            print("No more data points available. All have been used.")
            return
    
    # Select 100 random data points (or all available if less than 100)
    to_extract = min(100, len(available_indices))
    selected_indices = random.sample(available_indices, to_extract)
    
    # Create subset
    subset_data = [data[idx] for idx in selected_indices]
    
    # Update the used indices
    used_indices.update(selected_indices)
    
    # Save the subset
    subset_file = os.path.join(subset_dir, f"subset_{next_id}.json")
    
    if schema:
        # If the original had a schema, maintain the same structure
        subset_full_data = {
            'schema': schema,
            'data': subset_data
        }
        with open(subset_file, 'w') as f:
            json.dump(subset_full_data, f, indent=2)
    else:
        # Otherwise just save the data array
        with open(subset_file, 'w') as f:
            json.dump(subset_data, f, indent=2)
    
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