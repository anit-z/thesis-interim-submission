import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table
import numpy as np
import os
from matplotlib import rcParams
import ast

# Set larger default font sizes
rcParams['font.size'] = 12
rcParams['axes.titlesize'] = 14

# Read the CSV file
file_path = './earnings21-file-metadata0520.csv'
if not os.path.exists(file_path):
    print(f"Error: File not found at path {file_path}")
    exit()

# Read CSV with error handling
try:
    df = pd.read_csv(file_path, encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv(file_path, encoding='latin1')
    except Exception as e:
        print(f"Failed to read CSV: {str(e)}")
        exit()

# Columns we need
required_columns = [
    'file_id', 'sp_action', 'moodys_action', 'fitch_action',
    'FinBERT Sentiment', 'FinBERT Sentiment Score'
]

# Verify columns exist
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    print(f"Missing columns: {missing_cols}")
    exit()

# Extract sentiment label properly
def extract_sentiment(sent_str):
    if pd.isna(sent_str):
        return None
    
    # The column contains strings like: {"label":"Negative","score":0.99}
    try:
        # Remove any problematic characters
        clean_str = str(sent_str).replace("'", '"').strip()
        if clean_str.startswith('{'):
            data = ast.literal_eval(clean_str)
            return data.get('label')
        return None
    except Exception as e:
        print(f"Error processing sentiment: {str(e)}")
        return None

# Create clean columns                
df['FinBERT_Sentiment'] = df['FinBERT Sentiment'].apply(extract_sentiment)
df['FinBERT_Sentiment_Score'] = pd.to_numeric(df['FinBERT Sentiment Score'], errors='coerce')

# Filter for valid actions
valid_actions = ['affirm', 'upgrade', 'downgrade']
df_filtered = df[
    df['sp_action'].str.lower().str.strip().isin(valid_actions) |
    df['moodys_action'].str.lower().str.strip().isin(valid_actions) |
    df['fitch_action'].str.lower().str.strip().isin(valid_actions)
].copy()

# Create output table (first 20 records)
output_table = df_filtered[required_columns].head(20).copy()
output_table.columns = ['file_id', 'sp_action', 'moodys_action', 'fitch_action',
                       'FinBERT_Sentiment', 'FinBERT_Sentiment_Score']

# Fill any remaining NAs
output_table['FinBERT_Sentiment'] = output_table['FinBERT_Sentiment'].fillna('N/A')

# Verify we have sentiment data
print("\nSample sentiment data:")
print(output_table[['FinBERT_Sentiment', 'FinBERT_Sentiment_Score']].head())

# Create visualization
plt.figure(figsize=(16, min(12, 0.5*len(output_table)+2)))
ax = plt.gca()
ax.axis('off')

# Table colors
colors = {
    'affirm': '#6495ED',
    'upgrade': '#90EE90',
    'downgrade': '#FF7F7F', 
    'header': '#DDDDDD',
    'default': 'white',
    'neutral': '#F0F0F0'  # Light gray for neutral sentiment
}

# Create table data
table_data = [output_table.columns.tolist()] + output_table.values.tolist()
table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                colWidths=[0.15, 0.15, 0.15, 0.15, 0.2, 0.2])

# Style the table
for (row, col), cell in table.get_celld().items():
    cell.set_height(0.12)
    table.auto_set_font_size(False)
    
    if row == 0:  # Header
        cell.set_facecolor(colors['header'])
        cell.set_text_props(weight='bold', fontsize=14)
    else:
        val = table_data[row][col]
        
        # Color action columns
        if col in [1,2,3]:
            action = str(val).lower().strip()
            if 'affirm' in action:
                cell.set_facecolor(colors['affirm'])
            elif 'upgrade' in action:
                cell.set_facecolor(colors['upgrade']) 
            elif 'downgrade' in action:
                cell.set_facecolor(colors['downgrade'])
        
        # Highlight sentiment column
        elif col == 4:
            sentiment = str(val).lower()
            if 'neutral' in sentiment:
                cell.set_facecolor(colors['neutral'])
        
        # Format score column
        elif col == 5 and pd.notna(val):
            try:
                cell._text.set_text(f"{float(val):.3f}")
            except:
                pass
        
        cell.set_text_props(fontsize=12)

plt.tight_layout()
output_file = 'rating_actions_with_sentiment.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nTable saved to {output_file}")

plt.close()


