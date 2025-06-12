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
Rows following the heuristics: 952
Filtered data saved to 'dataset/secommits_filtered.json'
```

## Heuristics for the dataset
We applied the following heuristics to curate high-quality vulnerability-related commits for our dataset:

* **Single-file diffs only**: To minimize inference costs (especially when using OpenAI’s API), we selected commits that modify only one file. This design choice followed initial failed attempts to run open-source models like LLaMA locally via Ollama, due to insufficient RAM.

* **From authoritative vulnerability sources**: Commits were filtered to include only those linked to entries in public vulnerability databases — primarily the Open Source Vulnerabilities (OSV) and the National Vulnerability Database (NVD). These sources are recognized for their reliability in security research.

* **CWE-annotated only**: We excluded commits with missing or null CWE IDs. This ensures we can later verify whether the LLM-generated vulnerability description correctly identifies the CWE class.

* **Exclude documentation, configuration, and test-only changes**: Commits that only touch documentation files (.md, .txt, .rst), configuration (.toml), or test directories (test/, tests/) are excluded, as these changes are less likely to represent real vulnerabilities.

* **Non-empty patch content only**: We ensured that the patch_content field is not null or empty, excluding any commits where a diff could not be retrieved or parsed.

4. Generate subsets

The subsets were generated in groups of 100. Each subset was collected randomly from the `dataset/secommits_filtered.json`. Only data points that were not yet used on a different subset were picked.

```
python extract_subset.py --input dataset/secommits_filtered.json
```
If you run it 10 times, you should get 10 subsets for the `dataset/secommits_filtered.json`.

5. Generate code diffs to provide to the model.