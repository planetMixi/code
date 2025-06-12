# JSON Subset Extractor

This script extracts subsets of 100 data points from a large JSON file, keeping track of which data points have been used to avoid duplication.

## Features

- Extracts 100 random data points that haven't been used before
- Uses pandas for simplified JSON handling
- Works with both table-oriented JSON (with schema) and standard JSON formats
- Keeps track of used data points using a separate tracking file
- Assigns sequential IDs to created subsets
- Saves each subset as a separate JSON file with table orientation
- Preserves data types and structure from the original file

## Usage

```bash
python extract_subset.py --input path/to/your/file.json --output-dir path/to/subsets
```

### Arguments

- `--input`, `-i`: Path to the input JSON file (default: `dataset/secommits_filtered.json`)
- `--output-dir`, `-o`: Directory to store subset files (default: `subsets`)

## Example

```bash
# Using default paths
python extract_subset.py

# Specifying custom paths
python extract_subset.py --input data/my_data.json --output-dir output/my_subsets
```

## Output

- Subset files will be created in the specified output directory as `subset_1.json`, `subset_2.json`, etc.
- Each subset file contains 100 data points (or fewer if less than 100 are available)
- A tracking file (e.g., `your_file.json.tracking`) is created to keep track of which data points have been used
- Subsets are saved in pandas' table-oriented JSON format, which preserves data types and structure

## Notes

- If all data points have been used, the script will notify you
- The script automatically creates the output directory if it doesn't exist
- The original JSON file is not modified
- The script uses pandas for simplified JSON handling
- Subsets can be easily loaded into pandas DataFrames using `pd.read_json(subset_file, orient='table')` 