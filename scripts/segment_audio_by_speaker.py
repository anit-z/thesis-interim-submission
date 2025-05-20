import os
import subprocess
import csv
from collections import defaultdict

# ----------------------------------------
# Define directory paths (relative to repo)
# ----------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(BASE_DIR, "earnings21", "earnings21", "wav")
RTTM_DIR = os.path.join(BASE_DIR, "earnings21", "earnings21", "rttms")
OUTPUT_DIR = os.path.join(BASE_DIR, "earnings21", "earnings21", "media_by_speaker")
SPEAKER_META_PATH = os.path.join(BASE_DIR, "earnings21", "earnings21", "speaker-metadata.csv")

# ----------------------------------------
# Parse RTTM file and return speaker segments
# ----------------------------------------
def parse_rttm(file_path):
    """
    Parses RTTM file and returns a dictionary:
    { speaker_id: [(start_time, end_time), ...] }
    """
    segments = defaultdict(list)
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("SPEAKER"):
                parts = line.strip().split()
                if len(parts) >= 8:
                    start_time = float(parts[3])
                    duration = float(parts[4])
                    speaker_id = parts[7]
                    end_time = start_time + duration
                    segments[speaker_id].append((start_time, end_time))

    # Sort time segments by start time
    for speaker in segments:
        segments[speaker].sort()

    return segments

# ----------------------------------------
# Load speaker_id → speaker_name mapping
# ----------------------------------------
def load_speaker_names(csv_path, file_id):
    """
    Load speaker names from metadata CSV.
    Returns a dictionary: { speaker_id: speaker_name }
    """
    mapping = {}
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)  # comma-separated by default
        for row in reader:
            if row["file_id"] == file_id:
                mapping[row["speaker_id"]] = row["speaker_name"].replace(" ", "_")
    return mapping

# ----------------------------------------
# Main segmentation and concatenation logic
# ----------------------------------------
def segment_and_concat(file_id):
    """
    Segments and concatenates speaker-specific audio from RTTM diarization.
    """
    audio_path = os.path.join(AUDIO_DIR, f"{file_id}.wav")
    rttm_path = os.path.join(RTTM_DIR, f"{file_id}.rttm")
    output_path = os.path.join(OUTPUT_DIR, file_id)
    os.makedirs(output_path, exist_ok=True)

    # Check input files
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        return
    if not os.path.exists(rttm_path):
        print(f"RTTM file not found: {rttm_path}")
        return

    print(f"Segmenting {file_id}...")

    # Load speaker metadata and RTTM speaker segments
    speaker_names = load_speaker_names(SPEAKER_META_PATH, file_id)
    speaker_segments = parse_rttm(rttm_path)

    # Step 1: Extract segments using ffmpeg
    for speaker, segments in speaker_segments.items():
        for idx, (start, end) in enumerate(segments):
            duration = end - start
            segment_path = os.path.join(output_path, f"{file_id}_spk{speaker}_seg{idx}.wav")
            cmd = [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-ss", str(start),
                "-t", str(duration),
                "-ar", "16000",  # Resample to 16kHz
                "-ac", "1",      # Mono
                segment_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"Segments created for {file_id}. Beginning concatenation...")

    # Step 2: Concatenate segments per speaker
    for speaker, segments in speaker_segments.items():
        segment_paths = [
            os.path.join(output_path, f"{file_id}_spk{speaker}_seg{idx}.wav")
            for idx in range(len(segments))
        ]

        # Create temporary list file for ffmpeg concat
        list_file = os.path.join(output_path, f"{file_id}_spk{speaker}_concat_list.txt")
        with open(list_file, "w") as f:
            for path in segment_paths:
                f.write(f"file '{path}'\n")

        # Get speaker name (fallback if not available)
        speaker_name = speaker_names.get(speaker, f"Speaker_{speaker}")
        speaker_name = speaker_name.replace(" ", "_")
        output_wav = os.path.join(output_path, f"{file_id}_{speaker_name}.wav")

        # Run ffmpeg to concatenate segments
        concat_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_wav
        ]
        subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Created: {output_wav}")

        # Clean up: remove individual segments and list file
        for seg_path in segment_paths:
            os.remove(seg_path)
        os.remove(list_file)

    print(f"Done: {file_id} processed and cleaned.\n")

# ----------------------------------------
# Entry point
# ----------------------------------------
if __name__ == "__main__":
    import multiprocessing

    wav_files = [
        f for f in os.listdir(AUDIO_DIR)
        if f.endswith(".wav")
    ]

    file_ids = sorted([os.path.splitext(f)[0] for f in wav_files])

    # Run with 4 parallel workers (adjust as needed)
    with multiprocessing.Pool(processes=4) as pool:
        pool.map(segment_and_concat, file_ids)