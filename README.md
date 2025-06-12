1. Run `install.sh`
2. Run command to get data.

```
gdown --fuzzy https://drive.google.com/file/d/1kkjdqMis0KnJ8jBLjyBDpsP7zR1VgrfM/view\?usp\=drive_link -O dataset/
```

3. Filter dataset for diffs with only one file.
```
python filter_secommits_one_file_diff.py 
```
Expected output:
```
Total rows processed: 11036
Rows with exactly 1 file: 5306
Filtered data saved to 'dataset/secommits_single_file.json'
```