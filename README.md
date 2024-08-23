# CodecBenchmark

# Make sure opus-tools is installed
`sudo apt install opus-tools`



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
