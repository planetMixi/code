1. Run `install.sh`
2. Run command to get data.

```
gdown --fuzzy https://drive.google.com/file/d/1kkjdqMis0KnJ8jBLjyBDpsP7zR1VgrfM/view\?usp\=drive_link -O dataset/
```

3. Filter dataset for diffs with only one file. 
```
python filter_secommits.py 
```
Expected output:
```
Total rows processed: 11036
Rows following the heuristics: 984
Filtered data saved to 'dataset/secommits_filtered.json'
```

Heuristics for the dataset:
* **commits with single-file diffs** (due to expenses constrains) -- you can briefly mentioned in your thesis that your first attempt was to try running llama and other free models with ollama on your computer; but since you couldn't due to your RAM memory, you shifted for OPENAI API and tried gpt.
* **from the open-source vulnerability database** (since osv is considered the most reliable source) -- you should mention the dataset includes data points from NVD and OSV in the dataset characterization.
* **with no empty or null CWE-ID** (since we want to use the CWE-ID to validate if the LLM generated the correct CWE)

4. Generate subsets

The subsets were generated in groups of 100. Each subset was collected randomly from the `dataset/secommits_filtered.json`. Only data points that were not yet used on a different subset were picked.

```
python extract_subset.py --input dataset/secommits_filtered.json
```
If you run it 10 times, you should get 10 subsets for the `dataset/secommits_filtered.json`.