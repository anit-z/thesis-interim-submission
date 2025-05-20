import pandas as pd

# Load the nlp file
nlp_file = '/scratch/s6055702/ser_credit_rating/earnings21/earnings21/transcripts/nlp_references/4346923.nlp'
with open(nlp_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Initialize lists to store the data
tokens = []
speakers = []
ts = []
end_ts = []
punctuations = []
cases = []
tags = []
wer_tags = []

# Iterate through the lines
for line in lines:
    line = line.strip().split('|')
    if len(line) == 8:
        token, speaker, ts_val, end_ts_val, punctuation, case, tags_val, wer_tags_val = line
        tokens.append(token)
        speakers.append(speaker)
        ts.append(ts_val)
        end_ts.append(end_ts_val)
        punctuations.append(punctuation)
        cases.append(case)
        tags.append(tags_val)
        wer_tags.append(wer_tags_val)

# Create a DataFrame
df = pd.DataFrame({'token': tokens, 'speaker': speakers, 'ts': ts, 'end_ts': end_ts, 'punctuation': punctuations, 'case': cases, 'tags': tags, 'wer_tags': wer_tags})

# Load the speaker metadata
speaker_metadata = '/scratch/s6055702/ser_credit_rating/earnings21/earnings21/speaker-metadata.csv'
metadata = pd.read_csv(speaker_metadata)

# Map the speaker name with the metadata
speaker_map = metadata.set_index('speaker_id')['speaker_name'].to_dict()

# Add the speaker name to the DataFrame
df['speaker_name'] = df['speaker'].map(speaker_map)

# Save the reformatted file
output_file = 'reformatted_token_4346923.txt'
with open(output_file, 'w') as f:
    for index, row in df.iterrows():
        line = f"{row['token']}|{row['speaker_name']}|{row['ts']}|{row['end_ts']}|{row['punctuation']}|{row['case']}|{row['tags']}|{row['wer_tags']}\n"
        f.write(line)

print("Reformatted file saved to:", output_file)

# Load the reformatted nlp file
with open(output_file, 'r') as f:
    lines = f.readlines()

# Initialize lists to store the data
data = []
for line in lines:
    line = line.strip().split('|')
    data.append(line)

# Initialize variables to store the paragraphs
paragraphs = []
current_paragraph = []
current_speaker = None

# Iterate through the lines
for line in data:
    token, speaker, ts, end_ts, punctuation, case, tags, wer_tags = line
    if speaker != current_speaker and current_speaker is not None:
        paragraphs.append(f"{current_speaker}: {' '.join(current_paragraph)}")
        current_paragraph = []
    current_paragraph.append(token)
    current_speaker = speaker

# Append the last paragraph
paragraphs.append(f"{current_speaker}: {' '.join(current_paragraph)}")

# Save the paragraphs to a new file
output_paragraphs_file = 'reformatted_transcription_4346923.txt'
with open(output_paragraphs_file, 'w') as f:
    for paragraph in paragraphs:
        f.write(paragraph + '\n\n')

print("Paragraphs file saved to:", output_paragraphs_file)

speakers = set()
with open(output_paragraphs_file, 'r') as f:
    for line in f:
        if ':' in line:
            speaker = line.split(':')[0].strip()
            speakers.add(speaker)

speakers = list(set(speakers))

for speaker in speakers:
    with open(f'{speaker}.txt', 'w') as f:
        with open(output_paragraphs_file, 'r') as file:
            for line in file:
                if line.startswith(f"{speaker}:"):
                    f.write(line)