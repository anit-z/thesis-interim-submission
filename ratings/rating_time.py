import pandas as pd
import matplotlib.pyplot as plt
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

# Convert date columns to datetime
date_cols = ['earnings_call_date', 'sp_subsequent_rating_date', 
             'moodys_subsequent_rating_date', 'fitch_subsequent_rating_date']

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# Filter for file_ids that have at least one rating date
has_any_rating_date = df.groupby('file_id').apply(
    lambda x: any(not pd.isna(x[f'{agency}_subsequent_rating_date']).all() 
                 for agency in ['sp', 'moodys', 'fitch'])
)
valid_file_ids = has_any_rating_date[has_any_rating_date].index
df_filtered = df[df['file_id'].isin(valid_file_ids)].copy()

print(f"Original rows: {len(df)}, Filtered rows: {len(df_filtered)}")

def calculate_days_diff(row):
    """Calculate days between earnings call and subsequent rating actions"""
    earnings_date = row['earnings_call_date']
    if pd.isna(earnings_date):
        return None
    
    agency_dates = []
    for agency in ['sp', 'moodys', 'fitch']:
        rating_date = row[f'{agency}_subsequent_rating_date']
        if not pd.isna(rating_date):
            delta = (rating_date - earnings_date).days
            if delta >= 0:  # Only consider dates after earnings call
                agency_dates.append(delta)
    
    if not agency_dates:  # No valid dates found
        return None
    
    return min(agency_dates)  # Return shortest duration

# Calculate time differences
df_filtered['days_to_rating'] = df_filtered.apply(calculate_days_diff, axis=1)
df_filtered = df_filtered.dropna(subset=['days_to_rating'])

# Sort by days_to_rating descending for plotting
df_sorted = df_filtered.sort_values('days_to_rating', ascending=False)

# Create a sample for better visualization (top 20 longest durations)
sample_size = min(20, len(df_sorted))
df_sample = df_sorted.head(sample_size)

# Create horizontal bar chart
plt.figure(figsize=(12, 10))
bars = plt.barh(
    range(len(df_sample)),
    df_sample['days_to_rating'],
    color='dodgerblue',
    alpha=0.7
)

plt.title('Time between Earnings Call Date and Subsequent Rating Action\n(Companies with at least one agency rating date)', pad=20)
plt.xlabel('Number of days (shortest duration among available agencies)')
plt.ylabel('Company Index (sorted by duration)')
plt.yticks([])  # Remove y-axis ticks as we'll add labels
plt.grid(axis='x', alpha=0.3)

# Add data labels with available information
for idx, bar in enumerate(bars):
    width = bar.get_width()
    row = df_sample.iloc[idx]
    
    # Collect available rating actions
    actions = []
    for agency in ['sp', 'moodys', 'fitch']:
        if not pd.isna(row[f'{agency}_subsequent_rating_date']):
            actions.append(f"{agency.upper()}: {row[f'{agency}_action']}")
    
    plt.text(
        width + 1,
        idx,
        (f'{int(width)} days\n'
         f'Sector: {row["sector"]}\n' + 
         '\n'.join(actions)),
        va='center',
        fontsize=8
    )

plt.tight_layout()

# Save the plot
output_file = 'rating_action_timing_with_any_agency.png'
plt.savefig(output_file, bbox_inches='tight', dpi=300)
print(f"Plot saved to {output_file}")

# Additional analysis output
print("\nAdditional Analysis:")
print(f"Number of unique companies: {df_filtered['file_id'].nunique()}")
print(f"Average days to rating: {df_filtered['days_to_rating'].mean():.1f}")
print(f"Median days to rating: {df_filtered['days_to_rating'].median():.1f}")

