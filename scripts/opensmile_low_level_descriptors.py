import os
import subprocess
import pandas as pd
from pathlib import Path

# Configuration
OPENSMILE_PATH = "/path/to/opensmile/bin/SMILExtract"  # Update this path
CONFIG_DIR = "/path/to/opensmile/config"  # Update this path
OUTPUT_DIR = "./output_features"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Feature extraction configuration
FEATURE_CONFIGS = [
    {
        "name": "Pitch (F0)",
        "config": "prosodyShs.conf",
        "output": "pitch_features.csv"
    },
    {
        "name": "Loudness",
        "config": "emobase.conf",
        "output": "loudness_features.csv"
    },
    {
        "name": "MFCCs",
        "config": "MFCC12_0_D_A.conf",
        "output": "mfcc_features.csv"
    },
    {
        "name": "Jitter/Shimmer",
        "config": "prosodyShs.conf",
        "output": "voice_quality_features.csv"
    },
    {
        "name": "Formants",
        "config": "Formants.conf",
        "output": "formant_features.csv"
    },
    {
        "name": "Spectral Features",
        "config": "GeMAPS.conf",
        "output": "spectral_features.csv"
    },
    {
        "name": "Pause/Speech Rate",
        "config": "prosodyShs.conf",
        "output": "pause_features.csv"
    },
    {
        "name": "Delta Coefficients",
        "config": "MFCC12_0_D_A.conf",
        "output": "delta_features.csv"
    }
]

def extract_features(audio_file):
    """Extract all specified features from an audio file"""
    results = {}
    
    for config in FEATURE_CONFIGS:
        config_path = os.path.join(CONFIG_DIR, config["config"])
        output_path = os.path.join(OUTPUT_DIR, config["output"])
        
        cmd = [
            OPENSMILE_PATH,
            "-C", config_path,
            "-I", audio_file,
            "-O", output_path,
            "-l", "0"  # Disable console output
        ]
        
        try:
            subprocess.run(cmd, check=True)
            df = pd.read_csv(output_path)
            results[config["name"]] = df
            print(f"Successfully extracted {config['name']} features")
        except Exception as e:
            print(f"Error extracting {config['name']}: {str(e)}")
    
    return results

def process_directory(audio_dir):
    """Process all audio files in a directory"""
    audio_files = list(Path(audio_dir).glob("*.wav")  # Adjust extension as needed
    
    all_results = {}
    for audio_file in audio_files:
        print(f"\nProcessing {audio_file.name}...")
        all_results[audio_file.name] = extract_features(str(audio_file))
    
    return all_results

if __name__ == "__main__":
    # Example usage
    audio_directory = "./audio_samples"  # Directory containing your audio files
    feature_results = process_directory(audio_directory)
    
    # Save all results to a single file
    combined_results = {}
    for filename, features in feature_results.items():
        combined_results[filename] = {}
        for feature_name, df in features.items():
            combined_results[filename][feature_name] = df.iloc[0].to_dict()
    
    pd.DataFrame.from_dict(combined_results, orient='index').to_csv("all_features_combined.csv")
    print("\nFeature extraction complete. Results saved to all_features_combined.csv")