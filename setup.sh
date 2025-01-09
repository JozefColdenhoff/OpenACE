#!/bin/bash
set -euo pipefail

# This script sets up the necessary environment and libraries for the CodecBenchmark project.
# It creates an Anaconda environment, installs various audio processing libraries and tools,
# and compiles source code for several codecs including liblc3, LC3 Plus, and 3GPP EVS.
# The script ensures that specific versions or commits of the libraries are used to maintain consistency.

# Setup libraries 
cd src/libraries

# Setup liblc3
git clone https://github.com/google/liblc3.git
cd liblc3
git reset --hard 73bbc00 # v1.1.1
make -j 
make tools 
cd .. 

# Setup ESTI implementation for LC3 Plus
wget https://www.etsi.org/deliver/etsi_ts/103600_103699/103634/01.03.01_60/ts_103634v010301p0.zip
unzip ts_103634v010301p0.zip
rm ts_103634v010301p0.zip
cd ETSI_Release/LC3plus_ETSI_src_v172062927c2_20210930/src/floating_point
make
cd ../../../../

# Setup 3GPP EVS codec
# Release 18 2024-05-16 see https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=1464
wget https://www.3gpp.org/ftp/Specs/archive/26_series/26.442/26442-i00.zip
unzip 26442-i00.zip
rm 26442-i00.zip
rm 26442-i00.doc
unzip 26442-i00-ANSI-C_source_code.zip
rm 26442-i00-ANSI-C_source_code.zip
mv c-code EVS_3GPP
cd EVS_3GPP/
make
cd ../

# Setup VISOQOL library
git clone https://github.com/google/visqol.git
cd visqol
git reset --hard b2b2a64 # Latest version as of 08-2024
python -m pip install .