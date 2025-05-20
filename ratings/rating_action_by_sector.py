import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Read the CSV file with error handling for encoding
file_path = './earnings21-file-metadata0520.csv'
if not os.path.exists(file_path):
    print(f"Error: File not found at path {file_path}")
    exit()

# Try different encodings if UTF-8 fails
encodings_to_try = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']
df = None

for encoding in encodings_to_try:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        print(f"Successfully read file with {encoding} encoding")
        break
    except UnicodeDecodeError:
        print(f"Failed to read with {encoding} encoding")
        continue
    except Exception as e:
        print(f"Error reading CSV file with {encoding} encoding: {e}")
        continue

if df is None:
    print("Failed to read file with all attempted encodings")
    exit()

# Define the columns we need
columns_needed = [
    'sector', 'file_id', 'earnings_call_date',
    'sp_subsequent_rating_date', 'sp_action',
    'moodys_subsequent_rating_date', 'moodys_action',
    'fitch_subsequent_rating_date', 'fitch_action',
    'FinBERT Sentiment'
]

# Check if all columns exist in the dataframe
missing_columns = [col for col in columns_needed if col not in df.columns]
if missing_columns:
    print(f"Error: The following columns are missing from the CSV file: {missing_columns}")
    exit()

# Extract needed columns
df = df[columns_needed]

# Define rating action types we're interested in
action_types = ['affirm', 'downgrade', 'upgrade']

def classify_action(action):
    """Classify an action into one of our types or 'other'"""
    if pd.isna(action):
        return np.nan
    action = str(action).lower().strip()
    if action in action_types:
        return action
    return 'other'

# Classify actions for each rating agency
for agency in ['sp', 'moodys', 'fitch']:
    df[f'{agency}_action_class'] = df[f'{agency}_action'].apply(classify_action)

# Count actions by sector and agency
results = []
for sector in df['sector'].unique():
    if pd.isna(sector):
        continue
    sector_data = df[df['sector'] == sector]
    sector_result = {'sector': sector}
    
    for agency in ['sp', 'moodys', 'fitch']:
        action_counts = sector_data[f'{agency}_action_class'].value_counts()
        for action in action_types + ['other']:
            count = action_counts.get(action, 0)
            sector_result[f'{agency}_{action}'] = count
    
    results.append(sector_result)

# Create a results dataframe
results_df = pd.DataFrame(results)

# Plotting
fig, axes = plt.subplots(3, 1, figsize=(15, 18), sharex=True)

agencies = ['sp', 'moodys', 'fitch']
bar_width = 0.2
x = np.arange(len(results_df['sector']))

# Define colors for different actions
colors = {
    'affirm': 'blue',
    'downgrade': 'red',
    'upgrade': 'green',
    'other': 'gray'
}

for i, agency in enumerate(agencies):
    ax = axes[i]
    for j, action in enumerate(['affirm', 'downgrade', 'upgrade', 'other']):
        values = results_df[f'{agency}_{action}']
        ax.bar(x + j*bar_width, values, width=bar_width, color=colors[action], label=action.capitalize())
    
    ax.set_title(f'{agency.upper()} Rating Actions by Sector')
    ax.set_ylabel('Number of Companies')
    ax.set_xticks(x + 1.5*bar_width)
    ax.set_xticklabels(results_df['sector'], rotation=45, ha='right')
    ax.legend()

plt.suptitle('Rating Agency Actions by Sector')
plt.tight_layout()

# Save the plot instead of showing it (since you're on a server)
output_file = 'rating_actions_by_sector.png'
plt.savefig(output_file, bbox_inches='tight', dpi=300)
print(f"Plot saved to {output_file}")

