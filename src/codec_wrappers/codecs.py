from abc import ABC, abstractmethod
import os
import tempfile
import soundfile as sf
import numpy as np
import subprocess


class AbstractCodec(ABC):
    """
    Abstract base class for audio codecs.

    This class defines the common interface and properties for audio codec implementations.
    It serves as a blueprint for concrete codec classes and ensures that they implement
    the required methods.

    Args:
        bitrate (int): The bitrate to be used for encoding the audio.
        sample_rate (int, optional): The sample rate of the audio. Defaults to None.
        **kwargs: Additional keyword arguments that can be passed to the codec.

    Attributes:
        bitrate (int): The bitrate used for encoding the audio.
        sample_rate (int): The sample rate of the audio.
        kwargs (dict): Additional keyword arguments passed to the codec.

    Methods:
        __call__(input_file: str, output_file: str) -> None:
            Abstract method that should be implemented by concrete codec classes.
            It loads the input audio file, applies the codec encoding/decoding process,
            and saves the processed audio to the specified output file.
    """
    
    def __init__(self, bitrate: int, sample_rate: int = None, **kwargs) -> None:
        """
        Initializes the AbstractCodec instance.

        Args:
            bitrate (int): The bitrate to be used for encoding the audio.
            sample_rate (int, optional): The sample rate of the audio. Defaults to None.
            **kwargs: Additional keyword arguments that can be passed to the codec.
        """
        self.bitrate = bitrate
        self.sample_rate = sample_rate
        self.kwargs = kwargs
        
    @abstractmethod
    def __call__(self, input_file: str, output_file: str) -> None:
        """
        Abstract method that should be implemented by concrete codec classes.

        This method is responsible for loading the input audio file, applying the codec
        encoding/decoding process, and saving the processed audio to the specified output file.

        Args:
            input_file (str): The path to the input audio file.
            output_file (str): The path where the processed audio file will be saved.

        Raises:
            NotImplementedError: If the method is not implemented by a concrete codec class.
        """
        raise NotImplementedError("Subclasses must implement the __call__ method.")
    
    
class LC3Codec(AbstractCodec):
    """
    A concrete implementation of the LC3 audio codec.

    This class provides methods to encode and decode audio files using the LC3 codec.
    It inherits from the AbstractCodec class and implements the required methods.

    Args:
        bitrate (int): The bitrate to be used for encoding the audio.
        sample_rate (int, optional): The sample rate of the audio. Defaults to None.
        **kwargs: Additional keyword arguments. The 'lc3_path' argument is required and
            should specify the path to the LC3 codec binaries.

    Raises:
        RuntimeError: If the required LC3 codec binaries (dlc3 and elc3) are not found
            in the specified 'lc3_path'.

    Methods:
        __call__(input_file: str, output_file: str) -> None:
            Encodes the input audio file using the LC3 codec and decodes the encoded data
            back to an audio file. The encoded data is passed through a pipeline between
            the encoding and decoding processes without saving intermediate files.
    """
    def __init__(self, bitrate: int, sample_rate: int = None, **kwargs) -> None:
        super().__init__(bitrate, sample_rate, **kwargs)
        self.lc3_path = kwargs["lc3_path"]
        
        if (not os.path.exists(os.path.join(self.lc3_path, "bin", "dlc3"))) or (not os.path.exists(os.path.join(self.lc3_path, "bin", "elc3"))):            
            raise RuntimeError(f"liblc3 tools in {self.lc3_path} seem to not be built. Run make tools to build the required binaries.")     
        
    def __call__(self, input_file: str, output_file: str) -> None:
        """
        Encodes the input audio file using the LC3 codec and decodes the encoded data
        back to an audio file. The encoded data is passed through a pipeline between
        the encoding and decoding processes without saving intermediate files.

        Args:
            input_file (str): The path to the input audio file to be encoded.
            output_file (str): The path where the decoded audio file will be saved.
        """
        # Set the LD_LIBRARY_PATH environment variable
        bin_path = os.path.join(self.lc3_path, "bin")
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = bin_path
        
        # Encode the input file
        encode_command = [
            os.path.join(bin_path, "elc3"),
            input_file,
            "-b", str(self.bitrate)
        ]
        
        # Decode the encoded data
        decode_command = [
            os.path.join(bin_path, "dlc3")
        ]
        
        # Create a pipeline between the encoding and decoding commands
        encode_process = subprocess.Popen(encode_command, stdout=subprocess.PIPE, env=env)
        decode_process = subprocess.Popen(decode_command, stdin=encode_process.stdout, stdout=subprocess.PIPE, env=env)
        
        # Wait for the processes to finish and capture the output
        output, _ = decode_process.communicate()
        
        # Write the decoded output to the output file
        with open(output_file, "wb") as f:
            f.write(output)
    
            
            
class LC3plusCodec(AbstractCodec):
    """
    A concrete implementation of the LC3plus audio codec.

    This class provides methods to encode and decode audio files using the LC3plus codec.
    It inherits from the AbstractCodec class and implements the required methods. It
    requires the LC3plus library to be built, including its tools.

    Args:
        bitrate (int): The bitrate to be used for encoding the audio.
        sample_rate (int): The sample rate of the audio.
        **kwargs: Additional keyword arguments. The 'lc3plus_path' argument is required and
            should specify the path to the LC3plus codec binaries.

    Raises:
        RuntimeError: If the required LC3plus codec binaries are not found
            in the specified 'lc3plus_path'.

    Methods:
        __call__(input_file: str, output_file: str) -> None:
            Encodes the input audio file using the LC3plus codec and decodes the encoded data
            back to an audio file. The encoded data is passed through a pipeline between
            the encoding and decoding processes without saving intermediate files.
    """
    def __init__(self, bitrate: int, sample_rate: int = None, **kwargs) -> None:
        super().__init__(bitrate, sample_rate, **kwargs)
        self.lc3plus_path = kwargs["lc3plus_path"]
        self.lc3plus_bin = os.path.join(self.lc3plus_path, "src", "floating_point", "LC3plus")

        if not os.path.exists(self.lc3plus_bin):
            raise RuntimeError(f"LC3plus binary not found at {self.lc3plus_bin}. Make sure the LC3plus library is built.")

    def __call__(self, input_file: str, output_file: str) -> None:
        """
        Encodes the input audio file using the LC3plus codec and decodes the encoded data
        back to an audio file. The command is run directly as a shell command.

        Args:
            input_file (str): The path to the input audio file to be encoded.
            output_file (str): The path where the decoded audio file will be saved.
        """
        #TODO: Find another way of not running this as a shell command...
        # Construct the command string
        command = f"{self.lc3plus_bin} {input_file} {output_file} {self.bitrate}"

        try:
            # Run the command using subprocess.run()
            subprocess.run(
                command,
                shell=True,
                check=True,
                executable='/bin/bash',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed with exit code: {e.returncode}")

        except Exception as e:
            raise RuntimeError(f"An error occurred during encoding/decoding: {str(e)}")
        
        
class OpusCodec(AbstractCodec):
    """
    A concrete implementation of the Opus audio codec.

    This class provides a method to encode audio files using the Opus codec.
    It inherits from the AbstractCodec class and implements the required methods.

    Args:
        bitrate (int): The bitrate to be used for encoding the audio, in bits per second.
        sample_rate (int, optional): The sample rate of the audio. Defaults to None.
        **kwargs: Additional keyword arguments.

    Methods:
        __call__(input_file: str, output_file: str) -> None:
            Encodes the input audio file using the Opus codec and saves the encoded
            audio to the specified output file.

    Note:
        The Opus codec and its command-line tools (opusenc) must be installed and
        accessible through the system's PATH for this class to function properly.
    """
    def __call__(self, input_file: str, output_file: str) -> None:
        """
        Encodes the input audio file using the Opus codec.

        Args:
            input_file (str): The path to the input audio file to be encoded.
            output_file (str): The path where the encoded audio file will be saved.
        """
        # Construct the command string
        try:
            # Run the opusenc command using subprocess.run()
            subprocess.run(
                ["opusenc", "--hard-cbr","--bitrate", str(self.bitrate // 1000), input_file, output_file],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Opus encoding failed with exit code: {e.returncode}")

        except Exception as e:
            raise RuntimeError(f"An error occurred during Opus encoding: {str(e)}")


class EVSCodec(AbstractCodec):
    """Concrete implementation of the EVS codec."""
    
    def __init__(self, bitrate: int, sample_rate: int, **kwargs) -> None:
        super().__init__(bitrate, sample_rate, **kwargs)
        self.evs_path = kwargs["evs_path"]
        self.encoder = os.path.join(self.evs_path, "EVS_cod")
        self.decoder = os.path.join(self.evs_path, "EVS_dec")

    def __call__(self, input_file: str, output_file: str) -> None:
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=f'.{self.sample_rate // 1000}k', delete=False) as raw_input_file, \
             tempfile.NamedTemporaryFile(suffix='.192', delete=False) as bitstream_file, \
             tempfile.NamedTemporaryFile(suffix=f'.{self.sample_rate // 1000}k', delete=False) as raw_output_file:
            
            try:
                # Encode: Convert WAV to raw PCM, encode to bitstream
                n_channels = self._wav_to_raw(input_file, raw_input_file.name)
                self._encode(raw_input_file.name, bitstream_file.name)

                # Decode: Convert bitstream to raw PCM, then to WAV
                self._decode(bitstream_file.name, raw_output_file.name)
                self._raw_to_wav(raw_output_file.name, output_file, n_channels)         
            
            finally:
                # Ensure temporary files are deleted
                os.remove(raw_input_file.name)
                os.remove(bitstream_file.name)
                os.remove(raw_output_file.name)

    def _encode(self, raw_file: str, bitstream_file: str) -> None:
        """Encode the raw PCM file to an EVS bitstream."""
        command = [
            self.encoder,
            "-q",
            str(self.bitrate),
            str(self.sample_rate // 1000),
            raw_file,
            bitstream_file,
        ]
        
        subprocess.run(command, check=True)

    def _decode(self, bitstream_file: str, raw_file: str) -> None:
        """Decode the EVS bitstream to a raw PCM file."""
        command = [
            self.decoder,
            "-q",
            str(self.sample_rate // 1000),
            bitstream_file,
            raw_file,
        ]
        
        subprocess.run(command, check=True)

    def _wav_to_raw(self, wav_file: str, raw_file: str) -> None:
        """Convert a WAV file to raw PCM format expected by the EVS codec."""
        data, samplerate = sf.read(wav_file, dtype='int16')
        assert samplerate == self.sample_rate, "Input WAV file sample rate must match the specified sample rate."

        # Ensure the data is in interleaved format (if multi-channel)
        data.tofile(raw_file)
        n_channels = data.shape[1]
        
        return n_channels

    def _raw_to_wav(self, raw_file: str, wav_file: str, n_channels:int) -> None:
        """Convert raw PCM format back to WAV file."""

        # Read the raw PCM data and write to a WAV file
        pcm_data = np.fromfile(raw_file, dtype='int16')
        
        # Reshape the data if it's stereo or multi-channel
        if n_channels > 1:
            pcm_data = pcm_data.reshape(-1, n_channels)

        sf.write(wav_file, pcm_data, self.sample_rate)