import os
import json

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define relative paths
norm_dir = os.path.join(script_dir, "../../earnings21/earnings21/transcripts/normalizations")
nlp_dir = os.path.join(script_dir, "../../earnings21/earnings21/transcripts/nlp_references")
wer_dir = os.path.join(script_dir, "../../earnings21/earnings21/transcripts/wer_tags")
output_dir = os.path.join(script_dir, "processed_transcripts")

os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(norm_dir):
    if not file.endswith(".norm.json"):
        continue

    file_id = file.replace(".norm.json", "")
    norm_path = os.path.join(norm_dir, file)
    nlp_path = os.path.join(nlp_dir, f"{file_id}.nlp")
    wer_path = os.path.join(wer_dir, f"{file_id}.wer_tag.json")
    output_path = os.path.join(output_dir, f"{file_id}.txt")

    if not os.path.exists(nlp_path) or not os.path.exists(wer_path):
        print(f"[WARNING] Missing NLP or WER file for {file_id}")
        continue

    with open(norm_path, "r", encoding="utf-8") as f:
        norm_data = json.load(f)

    with open(nlp_path, "r", encoding="utf-8") as f:
        nlp_lines = f.readlines()[1:]  # Skip header

    with open(wer_path, "r", encoding="utf-8") as f:
        wer_data = json.load(f)

    reconstructed = []
    for idx, line in enumerate(nlp_lines):
        line = line.strip()
        if not line:
            continue

        token_index = str(idx)
        parts = line.split("|")
        original_token = parts[0] if parts else ""

        # Use normalized token only if WER tag doesn't indicate deletion and it's available
        wer_tags = wer_data.get(token_index, [])
        if "4" in wer_tags or "5" in wer_tags or "6" in wer_tags:
            # Use normalization if available
            candidates = norm_data.get(token_index, {}).get("candidates", [])
            if candidates:
                best = max(candidates, key=lambda x: x["probability"])
                verbalization = best.get("verbalization", [])
                if verbalization:
                    reconstructed.extend(verbalization)
                    continue  # Skip to next token

        # Else use original token
        reconstructed.append(original_token)

    # Save result
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(" ".join(reconstructed))

    print(f"[INFO] Processed {file_id} ✓")
