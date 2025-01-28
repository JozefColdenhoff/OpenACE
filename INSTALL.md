# Dependencies
The `./setup.sh` will install most of the required dependencies, see below. However it still requires some dependencies listed below. 

## The bazel build system
```sh
# Make sure the bazel build system is installed to compile and build the VISQOL repository. See 'https://bazel.build/install'.
# On Ubuntu Linux, you can follow 'https://bazel.build/install/ubuntu#install-on-ubuntu':
sudo apt install apt-transport-https curl gnupg -y
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor >bazel-archive-keyring.gpg
sudo mv bazel-archive-keyring.gpg /usr/share/keyrings
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list

sudo apt update && sudo apt install bazel
# Install the version 5.3.2 required by VISQOL
sudo apt install bazel-5.3.2
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

# Setup the tools

```sh
./setup.sh # install the codec dependencies liblc3, LC3Plus, EVS, and the quality metric VISQOL
```

# Create a conda environment and download the data

Most of the datasets are automatically downloaded except for the ITU-T p.501: access the [ITU-T p.501 dataset](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-P.501-202005-I!!SOFT-ZST-E&type=items) through a browser and place it in the `data/original` folder. 

```sh
conda env create -f environment.yaml
conda activate CodecBenchmark

./download_data.sh # downloads and unpacks data in data/original
```