import os
import json
import csv

# Define paths using relative paths from the script location
current_dir = os.path.dirname(os.path.abspath(__file__))
semantic_dir = os.path.join(current_dir, "..", "features", "semantic")
output_csv = os.path.join(semantic_dir, "sentiment_scores.csv")

# Initialize list to store all data
all_data = []

# Process all JSON files in the semantic directory
for filename in os.listdir(semantic_dir):
    if filename.endswith("_finbert_sentiment.json"):
        filepath = os.path.join(semantic_dir, filename)
        
        # Load JSON data
        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
            all_data.append(data)

# Write to CSV
with open(output_csv, 'w', newline='') as csvfile:
    fieldnames = ['file_id', 'sentiment', 'score']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for data in all_data:
        writer.writerow(data)

print(f"Successfully collected sentiment data from {len(all_data)} files")
print(f"Output CSV created at: {output_csv}")
