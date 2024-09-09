<div align="center">    
 
# OpenACE
<!-- 
[![Paper](http://img.shields.io/badge/paper-arxiv.1001.2234-B31B1B.svg)](https://www.nature.com/articles/nature14539)
[![Conference](http://img.shields.io/badge/NeurIPS-2019-4b44ce.svg)](https://papers.nips.cc/book/advances-in-neural-information-processing-systems-31-2018)
[![Conference](http://img.shields.io/badge/ICLR-2019-4b44ce.svg)](https://papers.nips.cc/book/advances-in-neural-information-processing-systems-31-2018)
[![Conference](http://img.shields.io/badge/AnyConference-year-4b44ce.svg)](https://papers.nips.cc/book/advances-in-neural-information-processing-systems-31-2018)   -->
<!--
ARXIV   
[![Paper](http://img.shields.io/badge/arxiv-math.co:1480.1111-B31B1B.svg)](https://www.nature.com/articles/nature14539)
-->


<!--  
Conference   
-->   
</div>
 
## Description   
This repository contains the code to generate the CodecBenchmark dataset. The code allows for the automatic application of codecs, and is easily extensible to any other codecs. Currently only tested on Ubuntu Linux. 

## How to use

### Dependencies
This repository automatically installs most of the required dependencies. However it still requires some dependencies listed below. 

```
Make sure the bazel build system is installed to compile and build the VISQOL repository. See 'https://bazel.build/install'. On Ubuntu Linux, you can follow 'https://bazel.build/install/ubuntu#install-on-ubuntu'.
```

Install opus-tools 

```sh
sudo apt install opus-tools
```
Install miniconda/anaconda see https://docs.anaconda.com/miniconda/

Install ffmpeg
```sh
sudo apt install ffmpeg
```
### Installation and setup
#### Process the datasets and unify the format
1. To setup the required libraries run `./setup.sh` which will install the codec dependencies liblc3, LC3Plus, EVS, and the quality metric VISQOL

2. Then manually download the [ITU-T p.501 dataset](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-P.501-202005-I!!SOFT-ZST-E&type=items) through a browser and place it in the `data/original` folder. 

3. Activate the conda environment created by ./setup.sh `conda activate CodecBenchmark`

4. Finally run `./generate_dataset.sh` to download and process the remaining datasets.


#### Generate the encoded audio
Activate the conda env `conda activate CodecBenchmark`

Then from the src directory run the following to apply the codecs to the fullband signals in the benchmark
```sh
python -m apply_codecs bitrate=BITRATE data_subsets=fullband
```
or 
```sh
python -m apply_codecs bitrate=BITRATE test_run=True data_subsets=fullband
```

This will create a directory tree in the `data/processed/` folder. One directory per original reference file will be created. Thereafter the codecs defined in the `src/confic/codecs/default.yaml` file will be applied to the audio and saved to the respective folder. 
A metadata file will be generated at the end of the process at `data/processed/.../metadata.csv` containing the paths to the encoded files. The test `test_run` flag will only run the script on 10 files.

### VISQOL Computation
To compute VISQOL scores for the encoded files relative to their reference, a script is provided. After running the dataset generation the script can be run with the following command:

```sh
python -m compute_visqol_scores metadata_file=PATH_TO_METADATA_FILE
```

# Extra info
## Equivalent codec commands 

### liblc3

```sh
$ alias elc3="LD_LIBRARY_PATH=`pwd`/bin `pwd`/bin/elc3"
$ alias dlc3="LD_LIBRARY_PATH=`pwd`/bin `pwd`/bin/dlc3"
$ elc3 <in.wav> -b <bitrate> | dlc3 > <out.wav>
```

### LC3Plus ETSI
```sh
LC3plus -E -q -v <in.wav> <out.wav> <bitrate>
```

### OPUSEnc opus-tools
```sh
opusenc --quiet --hard-cbr --bitrate <bitrate> - | opusdec --quiet <out.wav>
```

### EVS ETSI reference implementation
Uses binary audio files for input and output, so wrapper converts them to this file format.
```sh
EVS_cod -q <bitrate> <sample rate kHz> <in.48k> <out.192>
EVS_dec -q <sample rate kHz> <out.192> <out.48k>
```
