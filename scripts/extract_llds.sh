#!/bin/bash

# Relative paths from project root
INPUT_DIR="earnings21/earnings21/media_by_speaker"
OUTPUT_BASE="features/llds_by_speaker"
CONFIG_PATH="opensmile/config/emobase/emobase_f0only.conf"
SMILE_BIN="opensmile/build/progsrc/smilextract/SMILExtract"

# Loop through all .wav files
find "$INPUT_DIR" -type f -name "*.wav" | while read -r audio_file; do
  file_id=$(basename "$(dirname "$audio_file")")
  speaker=$(basename "$audio_file" .wav)
  output_dir="$OUTPUT_BASE/$file_id"
  mkdir -p "$output_dir"

  output_lld="$output_dir/${speaker}_llds.csv"
  output_func="$output_dir/${speaker}_functionals.csv"

  "$SMILE_BIN" -C "$CONFIG_PATH" \
               -I "$audio_file" \
               -lldoutput "$output_lld" \
               -funcoutput "$output_func" \
               -nologfile

  echo "[INFO] Processed: $audio_file"
  echo "       ├── LLDs:        $output_lld"
  echo "       └── Functionals: $output_func"
done