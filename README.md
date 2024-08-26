<div align="center">    
 
# CodecBenchmark
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
This repository automatically installs most of the required dependencies. However it still requires two dependencies listed below. 

```
Make sure the bazel build system is installed to compile and build the VISQOL repository. See 'https://bazel.build/install'
```

Install opus-tools 

```sh
sudo apt install opus-tools
```

### Installation and setup

Run these shell scripts in the following order, make sure they are executable using chmod +x SCRIPT.sh

```
cd src
./setup.sh # Installs the codec dependencies liblc3, LC3Plus, EVS, and the quality metric VISQOL
./download_data.sh # Downloads allmost all of the data with the exception of the ITU-T p.501 dataset
```
Manually download the (ITU-T p.501 dataset)[https://logitech.slack.com/archives/D06KAEZ11CN/p1724334122715079?thread_ts=1724324197.048169&cid=D06KAEZ11CN] through a browser and unzip it in data/original 

From the src directory run
```
python -m process_dataset
```
This will create a directory tree in the `data/processed` folder. One directory per original reference file will be created. Thereafter the codecs defined in the `src/confic/codecs/default.yaml` file will be applied to the audio and saved to the respective folder. 
A metadata file will be generated at the end of the process at `data/processed/metadata.csv` containing the paths to the encoded files. 


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
opusenc -hard-cbr -bitrate <bitrate> <in.wav> <out.>
```

## EVS ETSI reference implementation
Uses binary audio files for input and output, so wrapper converts them to this file format.
```sh
EVS_cod -q <bitrate> <sample rate kHz> <in.48k> <out.192>
EVS_dec -q <sample rate kHz> <out.192> <out.48k>
```
