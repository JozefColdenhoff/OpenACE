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
This repository contains the code to generate the OpenACE dataset. The code allows for the automatic application of codecs, and is easily extensible to any other codecs. Currently only tested on Ubuntu Linux. 

## How to use

Follow the installation and setup in [INSTALL.md](INSTALL.md)

### Audio encoding and decoding
Run the following to apply the codecs to the fullband signals in the benchmark
```sh
conda activate CodecBenchmark; cd src
python -m apply_codecs bitrate=BITRATE data_subsets=fullband
```
You can use `test_run=True` option to run a limited number of files (10) test.

This will create a directory tree in the `data/processed/` folder. One directory per original reference file will be created. Thereafter the codecs defined in the `src/confic/codecs/default.yaml` file will be applied to the audio and saved to the respective folder. 
A metadata file will be generated at the end of the process at `data/processed/.../metadata.csv` containing the paths to the encoded files.

### VISQOL Computation
To compute VISQOL scores for the encoded files relative to their reference, a script is provided. After running the dataset generation the script can be run with the following command:

```sh
python -m compute_visqol_scores metadata_file=PATH_TO_METADATA_FILE
```

## Examples

### Visqol scores reproduction
To reproduce the VISQOL results of table 3 of our paper the following commands be run assuming that the source data is downloaded, and that the environment is set up. 
- Generate the 16 kb/s dataset `python -m apply_codecs bitrate=16400 data_subsets=fullband`
- Compute VISQOL scores `python -m compute_visqol_scores metadata_file="PROJECT_ROOT/data/processed/codecs\=default-dubset\=fullband-bitrate\=16/metadata_bitrate\=16.csv"`
- This will save a csv file containing the VISQOL scores in the folder containing the metadata. 
- Repeat for bitrates {32000, 64000} 

### Subjective evaluation of emotional speech at 16 kbps



## Citation
If you use the OpenACE dataset in any of your research, please cite the following paper:

```
@misc{coldenhoff2024openaceopenbenchmarkevaluating,
      title={OpenACE: An Open Benchmark for Evaluating Audio Coding Performance}, 
      author={Jozef Coldenhoff and Niclas Granqvist and Milos Cernak},
      year={2024},
      eprint={2409.08374},
      archivePrefix={arXiv},
      primaryClass={eess.AS},
      url={https://arxiv.org/abs/2409.08374}, 
}
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
LC3plus <in.wav> <out.wav> <bitrate>
```

### OPUSEnc opus-tools
```sh
opusenc --quiet --hard-cbr --bitrate <bitrate> - - | opusdec --quiet <out.wav>
```

### EVS ETSI reference implementation
Uses binary audio files for input and output, so wrapper converts them to this file format.
```sh
EVS_cod -q -mime <bitrate> <sample rate kHz> <in.raw> <out.bitstream>
EVS_dec -q <sample rate kHz> <out.bitstream> <out.raw>
```
