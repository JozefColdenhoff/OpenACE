#!/bin/bash
set -euo pipefail

project_root=$(pwd)
cd data/original

# IEEE 269-2010
wget https://standards.ieee.org/wp-content/uploads/import/download/269-2010_downloads.zip
unzip 269-2010_downloads.zip
rm -r __MACOSX
rm 269-2010_downloads.zip
mv 269-2010_downloads IEEE-269-2010

# ETSI TS 103-281
mkdir ETSI-TS-103-281
cd ETSI-TS-103-281
wget https://docbox.etsi.org/stq/Open/TS%20103%20281%20Wave%20files/Annex_E%20speech%20data/American_P835_16_sentences_4convergence.wav
wget https://docbox.etsi.org/stq/Open/TS%20103%20281%20Wave%20files/Annex_E%20speech%20data/FBMandarin_QCETSI_26dB.wav
wget https://docbox.etsi.org/stq/Open/TS%20103%20281%20Wave%20files/Annex_E%20speech%20data/German_P835_16_sentences_4convergence.wav
cd ../


# VCTK Validation
# wget "https://datashare.ed.ac.uk/download/DS_10283_3443.zip"
unzip DS_10283_3443.zip "VCTK-Corpus-0.92.zip" -d "VCTK"
rm DS_10283_3443.zip
cd VCTK
# Extract test speakers as defined by the URGENT challenge script https://github.com/urgent-challenge/urgent2024_challenge/blob/main/utils/prepare_VCTK_speech.sh We only select mic1 
unzip -l VCTK-Corpus-0.92.zip | awk '/p226|p287|p315/ && /mic1/ {print $4}' |xargs unzip VCTK-Corpus-0.92.zip
rm VCTK-Corpus-0.92.zip
cd ../

# EARS (EARS test set)
mkdir  EARS
cd EARS
for X in $(seq -w 102 107); do
  curl -L https://github.com/facebookresearch/ears_dataset/releases/download/dataset/p${X}.zip -o p${X}.zip
  unzip -q p${X}.zip
  rm p${X}.zip
done
cd ../

# EBU SQAM
wget https://qc.ebu.io/testmaterial/523/1/download -O SQAM.zip
mkdir EBU_SQAM
unzip SQAM.zip -d EBU_SQAM
rm SQAM.zip

# # # ODAQ
wget https://zenodo.org/records/10405774/files/ODAQ.zip
unzip ODAQ.zip "ODAQ/ODAQ_unprocessed/*"
rm ODAQ.zip


# ITU-T P.501
# Due to technical limitations this dataset must be downloaded manually at https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-P.501-202005-I!!SOFT-ZST-E&type=items 
unzip T-REC-P.501-202005-I\!\!SOFT-ZST-E.zip -d T-REC-501
cd T-REC-501/Speech\ signals/
unzip \*.zip
rm *.zip
cd ../../ 


# Convert all .flac files to 16-bit PCM wav files
echo "Converting .flac files. May take some time..."
# Enable globstar for recursive file matching
shopt -s globstar

# Set the input directory to the current working directory
data_base_path=$(pwd)

# Loop through all .flac files in the input directory and its subfolders
for file in "$data_base_path"/**/*.flac; do
  # Check if the file exists
  if [ -e "$file" ]; then
    # Get the directory path of the current file
    dir=$(dirname "$file")
    
    # Get the filename without the extension
    filename=$(basename "$file" .flac)
    
    # Set the output file path
    output_file="$dir/$filename.wav"
    
    # Convert the .flac file to .wav using ffmpeg
    ffmpeg -hide_banner -loglevel error -i "$file" -acodec pcm_s16le "$output_file"
    
    # Remove the original .flac file
    rm "$file"
  else
    echo "File not found: $file"
  fi
done

# Downmix all files to mono 
# Loop through all .wav files in the input directory and its subfolders
for file in "$data_base_path"/**/*.wav; do
  # Check if the file exists
  if [ -e "$file" ]; then
    # Get the directory path of the current file
    dir=$(dirname "$file")
    
    # Get the filename without the extension
    filename=$(basename "$file" .wav)
    
    # Set the output file path for mono wav
    output_file_mono="$dir/$filename-mono.wav"
    
    # Downmix the .wav file to mono using ffmpeg
    ffmpeg -hide_banner -loglevel error -i "$file" -ac 1 "$output_file_mono"
    
    # Remove the original .wav file
    rm "$file"
    
    # Rename the mono file to the original filename
    mv "$output_file_mono" "$dir/$filename.wav"
  else
    echo "File not found: $file"
  fi
done

# Generate metadata file
cd "$project_root"/src 
python -m utils.generate_metadata --base_path "$data_base_path"