import pandas as pd

df = pd.read_csv("secom_zero_shot_results.csv")

# Calculate average scores
avg_original_score = df["original_message_score"].mean()
avg_generated_score = df["generated_secom_message_score"].mean()

print("Average Original Message Score:", avg_original_score)
print("Average Generated SECOM Message Score:", avg_generated_score)
