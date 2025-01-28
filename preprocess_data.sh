#!/bin/bash
set -euo pipefail

project_root=$(pwd)
output_dir="$project_root/data/mono-16bit-wav"
cd data/original

# Convert all .flac files to 16-bit PCM wav files
echo "Unifying audio format of .flac and .wav files to 16-bit mono PCM wav in:"
echo "  $output_dir"

# Enable globstar for recursive file matching
shopt -s globstar

# Set the input directory to the current working directory
data_base_path=$(pwd)

# Loop through all .flac and .wav files in the input directory and its subfolders
for file in "$data_base_path"/**/*.{flac,wav}; do
  # Check if the file exists
  if [ -e "$file" ]; then
    # Get the directory path of the current file
    dir=$(dirname "$file")
    # relace dir with path prefix output_dir
    dir=${dir/$data_base_path/$output_dir}
    # Create the output directory if it does not exist and skip if it does
    mkdir -p "$dir"

    # # Get the filename without the extension
    # filename=$(basename "$file" .flac)

    # Change the extension to .wav
    filename=$(basename "$file" | sed 's/\.[^.]*$//').wav
    
    # Set the output file path
    output_file="$dir/$filename"
    
    # Convert the file to 16-bit mono PCM wav using sox
    sox "$file" -c 1 -b 16 "$output_file"
    
  else
    echo "File not found: $file"
  fi
done

# Generate metadata file
cd "$project_root"/src 
echo "Generating metadata file in $output_dir"
python -m utils.generate_metadata --base_path "$output_dir"