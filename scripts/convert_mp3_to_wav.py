import os
from pydub import AudioSegment

# Define relative paths
MEDIA_DIR = "../earnings21/earnings21/media"
WAV_DIR = "../earnings21/earnings21/wav"

def convert_mp3_to_wav():
    """
    Converts all .mp3 files in the media directory to .wav format
    and saves them in the wav directory.
    """
    # Create the WAV directory if it doesn't exist
    os.makedirs(WAV_DIR, exist_ok=True)
    
    # Iterate through all files in the media directory
    for filename in os.listdir(MEDIA_DIR):
        if filename.endswith(".mp3"):
            mp3_path = os.path.join(MEDIA_DIR, filename)
            wav_filename = os.path.splitext(filename)[0] + ".wav"
            wav_path = os.path.join(WAV_DIR, wav_filename)

            try:
                # Load the MP3 file
                audio = AudioSegment.from_mp3(mp3_path)
                # Export as WAV
                audio.export(wav_path, format="wav")
                print(f"Converted: {mp3_path} -> {wav_path}")
            except Exception as e:
                print(f"Failed to convert {mp3_path}: {e}")

if __name__ == "__main__":
    convert_mp3_to_wav()