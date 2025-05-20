import os
import json
from pathlib import Path
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
from tqdm import tqdm

# ---------------------------------------------
# Define base paths using relative structure
# ---------------------------------------------
script_dir = Path(__file__).resolve().parent

NLP_PATH = script_dir / "../earnings21/earnings21/transcripts/nlp_references"
NORM_PATH = script_dir / "../earnings21/earnings21/transcripts/normalizations"
WER_TAG_PATH = script_dir / "../earnings21/earnings21/transcripts/wer_tags"
OUTPUT_PATH = script_dir / "../features/semantic"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------
# Load FinBERT model
# ---------------------------------------------
print("Loading FinBERT model...")
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=0, batch_size=8)

# ---------------------------------------------
# Reconstruct normalized transcripts with alignment
# ---------------------------------------------
records = []

print(f"Processing transcripts and reconstructing normalized text from: {NLP_PATH.resolve()}")

for nlp_file in tqdm(sorted(NLP_PATH.glob("*.nlp"))):
    file_id = nlp_file.stem

    norm_file = NORM_PATH / f"{file_id}.norm.json"
    wer_file = WER_TAG_PATH / f"{file_id}.wer_tag.json"

    if not norm_file.exists() or not wer_file.exists():
        print(f"[WARNING] Missing norm or WER file for {file_id}")
        continue

    try:
        with open(nlp_file, "r", encoding="utf-8") as f:
            nlp_lines = f.readlines()[1:]  # Skip header

        with open(norm_file, "r", encoding="utf-8") as f:
            norm_data = json.load(f)

        with open(wer_file, "r", encoding="utf-8") as f:
            wer_data = json.load(f)

        reconstructed_tokens = []

        for idx, line in enumerate(nlp_lines):
            line = line.strip()
            if not line:
                continue

            token_index = str(idx)
            parts = line.split("|")
            original_token = parts[0] if parts else ""

            # Default to original token
            token_to_add = [original_token]

            wer_tags = wer_data.get(token_index, [])
            if "4" in wer_tags or "5" in wer_tags or "6" in wer_tags:
                candidates = norm_data.get(token_index, {}).get("candidates", [])
                if candidates:
                    best = max(candidates, key=lambda x: x["probability"])
                    verbalization = best.get("verbalization", [])
                    if verbalization:
                        token_to_add = verbalization

            reconstructed_tokens.extend(token_to_add)

        if not reconstructed_tokens:
            print(f"[WARNING] No tokens reconstructed for {file_id}")
            continue

        normalized_text = " ".join(reconstructed_tokens)
        normalized_text = normalized_text[:512]  # Truncate to max input size for BERT

        records.append({
            "file_id": file_id,
            "text": normalized_text
        })

    except Exception as e:
        print(f"[ERROR] Failed processing {file_id}: {e}")
        continue

# ---------------------------------------------
# Run FinBERT classification in batch
# ---------------------------------------------
if not records:
    print("No valid transcripts processed. Exiting.")
    exit()

print("Running FinBERT sentiment classification...")

dataset = Dataset.from_list(records)
predictions = classifier(dataset["text"])

# Save results
for record, pred in zip(records, predictions):
    result = {
        "file_id": record["file_id"],
        "sentiment": pred["label"],
        "score": pred["score"]
    }

    output_file = OUTPUT_PATH / f"{record['file_id']}_finbert_sentiment.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

print("Sentiment classification completed. Results saved to:", OUTPUT_PATH.resolve())