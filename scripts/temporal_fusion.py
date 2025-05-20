import os
import glob
import json
import csv
from collections import defaultdict

# --- Directory Paths ---

RTTM_DIR = "earnings21/earnings21/rttms"
LLD_DIR = "features/llds_by_speaker"
SENTIMENT_DIR = "features/semantic"
TRANSCRIPT_DIR = "features/semantic/processed_transcripts"
NLP_REF_DIR = "earnings21/earnings21/transcripts/nlp_references"
OUTPUT_DIR = "features/fused_segments"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Utility Functions ---

def load_rttm(rttm_path):
    """
    Load RTTM file and return a list of speaker segments.
    """
    segments = []
    with open(rttm_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            _, file_id, _, start, dur = parts[:5]
            speaker = parts[7] if len(parts) > 7 else "unknown"
            segments.append({
                "file_id": file_id,
                "start": float(start),
                "end": float(start) + float(dur),
                "speaker": speaker
            })
    return segments

def load_llds(csv_path):
    """
    Load acoustic LLD CSV with proper delimiter and extract timestamps.
    """
    data = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f, delimiter=';')
        if "frameTime" not in reader.fieldnames:
            raise ValueError(f"'frameTime' not found in {csv_path}")
        for row in reader:
            try:
                row["timestamp"] = float(row["frameTime"])
                data.append(row)
            except ValueError:
                continue  # skip malformed rows
    if data:
        print(f"[DEBUG] LLD timestamp range: {data[0]['timestamp']} - {data[-1]['timestamp']} for {os.path.basename(csv_path)}")
    else:
        print(f"[DEBUG] No LLD data found in {os.path.basename(csv_path)}")
    return data

def load_sentiment(json_path):
    """
    Load sentiment data from a JSON file.
    """
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except:
        return {}

def load_transcript(txt_path):
    """
    Load normalized transcript text.
    """
    try:
        with open(txt_path, "r") as f:
            return f.read().strip()
    except:
        return ""

def load_nlp_tokens(nlp_path):
    """
    Load token-level timestamped words from .nlp file.
    """
    tokens = []
    try:
        with open(nlp_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                start, end, word = parts[0], parts[1], " ".join(parts[2:])
                tokens.append({
                    "start": float(start),
                    "end": float(end),
                    "word": word
                })
    except:
        pass
    return tokens

def average_acoustic_features(lld_data, start, end):
    """
    Compute average of each acoustic feature in the time window.
    """
    relevant = [row for row in lld_data if start <= row["timestamp"] <= end]
    if not relevant:
        return {}
    features = defaultdict(list)
    for row in relevant:
        for k, v in row.items():
            if k in ["frameTime", "timestamp"]:
                continue
            try:
                features[k].append(float(v))
            except:
                pass
    return {k: sum(vs)/len(vs) for k, vs in features.items()}

def extract_segment_tokens(tokens, start, end):
    """
    Return all tokens within a time segment.
    """
    words = [t["word"] for t in tokens if start <= t["start"] and t["end"] <= end]
    return " ".join(words)

def find_lld_file(file_id, speaker_label):
    """
    Map numeric speaker label to the corresponding LLD file by index order.
    """
    lld_dir = os.path.join(LLD_DIR, file_id)
    if not os.path.exists(lld_dir):
        return None

    candidates = sorted(glob.glob(os.path.join(lld_dir, f"{file_id}_*_llds.csv")))

    try:
        index = int(speaker_label)
        if 0 <= index < len(candidates):
            return candidates[index]
    except ValueError:
        return None

    return None

# --- Main Processing Loop ---

for rttm_path in glob.glob(f"{RTTM_DIR}/*.rttm"):
    file_id = os.path.splitext(os.path.basename(rttm_path))[0]
    print(f"\n[INFO] Processing {file_id}")

    segments = load_rttm(rttm_path)

    if segments:
        seg_start = min(s["start"] for s in segments)
        seg_end = max(s["end"] for s in segments)
        print(f"[DEBUG] RTTM segment range: {seg_start} - {seg_end}")

    sentiment_path = os.path.join(SENTIMENT_DIR, f"{file_id}_finbert_sentiment.json")
    transcript_path = os.path.join(TRANSCRIPT_DIR, f"{file_id}.txt")
    nlp_path = os.path.join(NLP_REF_DIR, f"{file_id}.nlp")

    sentiment_data = load_sentiment(sentiment_path)
    transcript = load_transcript(transcript_path)
    nlp_tokens = load_nlp_tokens(nlp_path)

    output = []
    warned_speakers = set()

    for segment in segments:
        speaker_label = segment["speaker"]
        lld_csv_path = find_lld_file(file_id, speaker_label)

        if not lld_csv_path:
            if (file_id, speaker_label) not in warned_speakers:
                print(f"[WARN] No LLD match for speaker '{speaker_label}' in {file_id}")
                warned_speakers.add((file_id, speaker_label))
            continue

        try:
            llds = load_llds(lld_csv_path)
        except Exception as e:
            print(f"[ERROR] Failed to load LLD from {lld_csv_path}: {e}")
            continue

        acoustic = average_acoustic_features(llds, segment["start"], segment["end"])
        text = extract_segment_tokens(nlp_tokens, segment["start"], segment["end"])
        sentiment = sentiment_data.get("sentiment", "Neutral")

        # Skip segments with no features and no text
        if not acoustic and not text:
            print(f"[SKIP] Segment ({segment['start']}–{segment['end']}) in {file_id} has no features or text")
            continue

        segment_data = {
            "file_id": file_id,
            "speaker": speaker_label,
            "start": segment["start"],
            "end": segment["end"],
            "text": text,
            "sentiment": sentiment,
            "acoustic": acoustic
        }

        output.append(segment_data)

    out_path = os.path.join(OUTPUT_DIR, f"{file_id}_fused.jsonl")
    with open(out_path, "w") as f:
        for entry in output:
            json.dump(entry, f)
            f.write("\n")

    print(f"[DONE] Saved: {out_path}")
    print(f"[SUMMARY] {len(output)} valid segments written to {file_id}_fused.jsonl")