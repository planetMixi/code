#!/usr/bin/env python3
"""
Script to analyze CWE distribution from secommits_single_file.json
"""

import json
import re
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import sys
from pathlib import Path

def extract_cwes_from_string(cwe_string):
    """
    Extract CWE IDs from a string that may contain set-like format
    e.g., "{'CWE-787'}" or "{'CWE-787', 'CWE-120'}"
    """
    if not cwe_string or cwe_string == 'null' or pd.isna(cwe_string):
        return []
    
    # Handle string representation of sets
    if isinstance(cwe_string, str):
        # Extract CWE patterns using regex
        cwe_pattern = r'CWE-\d+'
        cwes = re.findall(cwe_pattern, cwe_string)
        return cwes
    
    return []

def load_and_analyze_cwes(json_file_path):
    """
    Load JSON file and analyze CWE distribution
    """
    print(f"Loading data from {json_file_path}...")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)
    
    # Extract data entries
    if 'data' in data:
        entries = data['data']
    else:
        # Assume the entire file is a list of entries
        entries = data
    
    print(f"Found {len(entries)} entries in the dataset.")
    
    # Extract all CWEs
    all_cwes = []
    entries_with_cwes = 0
    entries_without_cwes = 0
    
    for entry in entries:
        cwe_field = entry.get('cwe_id', '')
        cwes = extract_cwes_from_string(cwe_field)
        
        if cwes:
            all_cwes.extend(cwes)
            entries_with_cwes += 1
        else:
            entries_without_cwes += 1
    
    return all_cwes, entries_with_cwes, entries_without_cwes, len(entries)

def analyze_and_visualize_cwes(all_cwes, entries_with_cwes, entries_without_cwes, total_entries):
    """
    Analyze CWE distribution and create visualizations
    """
    print(f"\n=== CWE Distribution Analysis ===")
    print(f"Total entries: {total_entries}")
    print(f"Entries with CWEs: {entries_with_cwes}")
    print(f"Entries without CWEs: {entries_without_cwes}")
    print(f"Total CWE instances: {len(all_cwes)}")
    print(f"Unique CWEs: {len(set(all_cwes))}")
    
    if not all_cwes:
        print("No CWEs found in the dataset.")
        return
    
    # Count CWE occurrences
    cwe_counter = Counter(all_cwes)
    
    # Create DataFrame for easier analysis
    cwe_df = pd.DataFrame(list(cwe_counter.items()), columns=['CWE', 'Count'])
    cwe_df = cwe_df.sort_values('Count', ascending=False)
    cwe_df['Percentage'] = (cwe_df['Count'] / len(all_cwes) * 100).round(2)
    
    print(f"\n=== Top 20 Most Common CWEs ===")
    print(cwe_df.head(20).to_string(index=False))
    
    # Save detailed results to CSV
    cwe_df.to_csv('cwe_distribution.csv', index=False)
    print(f"\nDetailed results saved to 'cwe_distribution.csv'")
    
    # Create visualizations
    create_visualizations(cwe_df, cwe_counter)
    
    return cwe_df

def create_visualizations(cwe_df, cwe_counter):
    """
    Create bar chart and pie chart visualizations
    """
    # Set up the plotting style
    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Top 15 CWEs bar chart
    top_15 = cwe_df.head(15)
    bars = ax1.bar(range(len(top_15)), top_15['Count'], color='skyblue', edgecolor='navy', alpha=0.7)
    ax1.set_xlabel('CWE ID')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Top 15 Most Common CWEs Distribution', fontsize=14, fontweight='bold')
    ax1.set_xticks(range(len(top_15)))
    ax1.set_xticklabels(top_15['CWE'], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01*max(top_15['Count']),
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie chart for top 10 CWEs
    top_10 = cwe_df.head(10)
    others_count = cwe_df.iloc[10:]['Count'].sum() if len(cwe_df) > 10 else 0
    
    if others_count > 0:
        pie_data = list(top_10['Count']) + [others_count]
        pie_labels = list(top_10['CWE']) + ['Others']
    else:
        pie_data = list(top_10['Count'])
        pie_labels = list(top_10['CWE'])
    
    colors = plt.cm.Set3(range(len(pie_data)))
    wedges, texts, autotexts = ax2.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', 
                                       colors=colors, startangle=90)
    ax2.set_title('CWE Distribution (Top 10 + Others)', fontsize=14, fontweight='bold')
    
    # Improve text readability
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    plt.tight_layout()
    plt.savefig('cwe_distribution.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'cwe_distribution.png'")
    
    # Show the plot
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze CWE distribution from secommits_filtered.json')
    parser.add_argument('--file', '-f', default='dataset/secommits_filtered.json',
                        help='Path to the JSON file (default: dataset/secommits_filtered.json)')
    parser.add_argument('--no-plot', action='store_true',
                        help='Skip creating visualizations')
    
    args = parser.parse_args()
    
    # Check if file exists
    json_file = Path(args.file)
    if not json_file.exists():
        print(f"Error: File {json_file} does not exist.")
        sys.exit(1)
    
    # Load and analyze data
    all_cwes, entries_with_cwes, entries_without_cwes, total_entries = load_and_analyze_cwes(json_file)
    
    if not args.no_plot:
        # Analyze and visualize
        cwe_df = analyze_and_visualize_cwes(all_cwes, entries_with_cwes, entries_without_cwes, total_entries)
    else:
        # Just print statistics
        if all_cwes:
            cwe_counter = Counter(all_cwes)
            cwe_df = pd.DataFrame(list(cwe_counter.items()), columns=['CWE', 'Count'])
            cwe_df = cwe_df.sort_values('Count', ascending=False)
            cwe_df['Percentage'] = (cwe_df['Count'] / len(all_cwes) * 100).round(2)
            
            print(f"\n=== CWE Distribution Analysis ===")
            print(f"Total entries: {total_entries}")
            print(f"Entries with CWEs: {entries_with_cwes}")
            print(f"Entries without CWEs: {entries_without_cwes}")
            print(f"Total CWE instances: {len(all_cwes)}")
            print(f"Unique CWEs: {len(set(all_cwes))}")
            print(f"\n=== Top 20 Most Common CWEs ===")
            print(cwe_df.head(20).to_string(index=False))
            
            cwe_df.to_csv('cwe_distribution.csv', index=False)
            print(f"\nDetailed results saved to 'cwe_distribution.csv'")

if __name__ == "__main__":
    main() 