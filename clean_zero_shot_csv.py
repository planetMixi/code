import pandas as pd

# Load original SECOM result CSV
input_file = "secom_zero_shot_10.csv"
output_file = "secom_zero_shot_10_cleaned.csv"

# Load the CSV
df = pd.read_csv(input_file)

# Filter out rows where the message contains a token length error
filtered_df = df[~df["generated_secom_message"].str.contains("maximum context length", case=False, na=False)]

# Save the cleaned results
filtered_df.to_csv(output_file, index=False)

print(f"✅ Cleaned file saved as {output_file}")
