import os
import subprocess

# Define relative paths
WAV_DIR = "../earnings21/earnings21/wav"
OUTPUT_DIR = "../features/acoustic"  # Updated output directory
OPENSMILE_DIR = "../opensmile"
SMILEXTRACT_BINARY = os.path.join(OPENSMILE_DIR, "build", "progsrc", "smilextract", "SMILExtract")
CONFIG_DIR = os.path.join(OPENSMILE_DIR, "config")

# OpenSMILE configuration files
CONFIG_FILES = {
    "ComParE_2016": os.path.join(CONFIG_DIR, "compare16", "ComParE_2016.conf"),
    "emobase": os.path.join(CONFIG_DIR, "emobase", "emobase.conf"),
    "prosodyShs": os.path.join(CONFIG_DIR, "prosody", "prosodyShs.conf"),
    "GeMAPS": os.path.join(CONFIG_DIR, "egemaps", "v01a", "eGeMAPSv01a.conf"),
}

def check_smilextract():
    """
    Check if the SMILExtract binary exists.
    """
    if not os.path.isfile(SMILEXTRACT_BINARY):
        raise FileNotFoundError(f"SMILExtract binary not found at {SMILEXTRACT_BINARY}. "
                                "Ensure OpenSMILE is built correctly.")

def create_output_directories():
    """
    Create output directories for storing extracted features.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_features(wav_file, config_file, output_csv):
    """
    Run openSMILE to extract features from a WAV file.
    """
    try:
        # Build the openSMILE command
        command = [
            SMILEXTRACT_BINARY,
            "-C", config_file,
            "-I", wav_file,
            "-O", output_csv,
        ]
        # Execute the command
        subprocess.run(command, check=True)
        print(f"Features extracted: {output_csv}")
    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except subprocess.CalledProcessError as cpe_error:
        print(f"Error running OpenSMILE for {wav_file}: {cpe_error}")
    except Exception as e:
        print(f"Unknown error extracting features for {wav_file}: {e}")

def process_all_files():
    """
    Process all WAV files in the input directory using the specified configurations.
    """
    for filename in os.listdir(WAV_DIR):
        if filename.endswith(".wav"):
            wav_path = os.path.join(WAV_DIR, filename)
            base_name = os.path.splitext(filename)[0]

            # Extract features with each configuration
            for config_name, config_path in CONFIG_FILES.items():
                output_csv = os.path.join(OUTPUT_DIR, f"{base_name}_{config_name}_features.csv")
                extract_features(wav_path, config_path, output_csv)

if __name__ == "__main__":
    try:
        # Check if SMILExtract binary exists
        check_smilextract()

        # Ensure output directories exist
        create_output_directories()

        # Process WAV files and extract features
        process_all_files()

    except Exception as e:
        print(f"Script failed: {e}")