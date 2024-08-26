#!/bin/bash
set -euo pipefail

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

# ITU-T P.501
# Due to technical limitations this dataset must be downloaded manually at https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-P.501-202005-I!!SOFT-ZST-E&type=items 

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

# # ODAQ
wget https://zenodo.org/records/10405774/files/ODAQ.zip
unzip ODAQ.zip "ODAQ/ODAQ_unprocessed/*"
rm ODAQ.zip
