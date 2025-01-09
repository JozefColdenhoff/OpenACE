# Dependencies
The `./setup.sh` will install most of the required dependencies, see below. However it still requires some dependencies listed below. 

## The bazel build system
```
Make sure the bazel build system is installed to compile and build the VISQOL repository. See 'https://bazel.build/install'. On Ubuntu Linux, you can follow 'https://bazel.build/install/ubuntu#install-on-ubuntu'.
```

## opus-tools 

```sh
sudo apt install opus-tools
```

## miniconda/anaconda

Follow https://docs.anaconda.com/miniconda/

## ffmpeg

```sh
sudo apt install ffmpeg
```

# Installation and setup
## Create a conda environment

```sh
conda env create -f environment.yaml
conda activate CodecBenchmark
```

## Process the datasets and unify the format
1. To setup the required libraries run `./setup.sh` which will install the codec dependencies liblc3, LC3Plus, EVS, and the quality metric VISQOL

2. Then manually download the [ITU-T p.501 dataset](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-P.501-202005-I!!SOFT-ZST-E&type=items) through a browser and place it in the `data/original` folder. 

3. Activate the conda environment created by ./setup.sh `conda activate CodecBenchmark`

4. Finally run `./generate_dataset.sh` to download and process the remaining datasets.
