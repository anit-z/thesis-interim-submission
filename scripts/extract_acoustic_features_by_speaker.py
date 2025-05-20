import os
import subprocess

# Base directory of the project (relative to this script)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Input directory containing subfolders like "4384683" with speaker .wav files
INPUT_ROOT = os.path.join(BASE_DIR, "earnings21", "earnings21", "media_by_speaker")

# Output root directory for extracted features
OUTPUT_ROOT = os.path.join(BASE_DIR, "features", "acoustic_by_speaker")

# Path to openSMILE executable (ensure SMILExtract is in PATH or use full path)
OPENSMILE_BIN = os.path.join(BASE_DIR, "opensmile", "build", "progsrc", "smilextract", "SMILExtract")

# Path to ComParE_2016.conf configuration file
CONFIG_PATH = os.path.join(BASE_DIR, "opensmile", "config", "compare16", "ComParE_2016.conf")

# Make sure the output root exists
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# Loop through each subdirectory (e.g., 4384683) in the input directory
for file_id in os.listdir(INPUT_ROOT):
    input_dir = os.path.join(INPUT_ROOT, file_id)

    # Skip non-directory entries
    if not os.path.isdir(input_dir):
        continue

    # Create output directory for this file_id
    output_dir = os.path.join(OUTPUT_ROOT, file_id)
    os.makedirs(output_dir, exist_ok=True)

    # Process each .wav file in the subdirectory
    for wav_filename in os.listdir(input_dir):
        if not wav_filename.endswith(".wav"):
            continue

        input_path = os.path.join(input_dir, wav_filename)

        # Use the .wav file base name as the .csv output name
        base_name = os.path.splitext(wav_filename)[0]
        output_csv = os.path.join(output_dir, f"{base_name}.csv")

        # Construct openSMILE command
        cmd = [
            OPENSMILE_BIN,
            "-C", CONFIG_PATH,
            "-I", input_path,
            "-O", output_csv
        ]

        # Log processing status
        print(f"Extracting: {input_path}")
        print(f"Saving to : {output_csv}")

        # Run the command
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Feature extraction failed for {input_path}: {e}")

print("All feature extraction tasks completed.")