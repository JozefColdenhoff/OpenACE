from abc import ABC, abstractmethod
import os
import tempfile
import soundfile as sf
import numpy as np
import subprocess
from utils.utils import get_audio_metadata
from typing import Tuple


class AbstractCodec(ABC):
    """
    Abstract base class for audio codecs.

    This class defines the common interface and properties for audio codec implementations.
    It serves as a blueprint for concrete codec classes and ensures that they implement
    the required methods.

    Args:
        **kwargs: Additional keyword arguments that can be passed to the codec.

    Attributes:
        kwargs (dict): Additional keyword arguments passed to the codec.
        name (str): Name of the codec implementation.

    Methods:
        __call__(input_file: str, output_file: str, bitrate:int) -> None:
            Abstract method that should be implemented by concrete codec classes.
            It loads the input audio file, applies the codec encoding/decoding process,
            and saves the processed audio to the specified output file.
    """
    
    def __init__(self, **kwargs) -> None:
        """
        Initializes the AbstractCodec instance.

        Args:
            **kwargs: Additional keyword arguments that can be passed to the codec.
        """
        self.kwargs = kwargs
        
    @abstractmethod
    def __call__(self, input_file: str, output_file: str, bitrate:int) -> None:
        """
        Abstract method that should be implemented by concrete codec classes.

        This method is responsible for loading the input audio file, applying the codec
        encoding/decoding process, and saving the processed audio to the specified output file.

        Args:
            input_file (str): The path to the input audio file.
            output_file (str): The path where the processed audio file will be saved.
            bitrate (int): The bitrate to be used for encoding the audio.

        Raises:
            NotImplementedError: If the method is not implemented by a concrete codec class.
        """
        raise NotImplementedError("Subclasses must implement the __call__ method.")
    
    def _verify_audio(self, path):
        audio_metadata = get_audio_metadata(path)
        # Assert that audio is mono
        if audio_metadata["channels"] != 1:
            raise ValueError(f"Audio must be mono {path}")
    
    
class LC3Codec(AbstractCodec):
    """
    A concrete implementation of the LC3 audio codec.

    This class provides methods to encode and decode audio files using the LC3 codec.
    It inherits from the AbstractCodec class and implements the required methods.

    Args:        
        **kwargs: Additional keyword arguments. The 'lc3_path' argument is required and
            should specify the path to the LC3 codec binaries.

    Raises:
        RuntimeError: If the required LC3 codec binaries (dlc3 and elc3) are not found
            in the specified 'lc3_path'.

    Methods:
        __call__(input_file: str, output_file: str, bitrate:int) -> None:
            Encodes the input audio file using the LC3 codec and decodes the encoded data
            back to an audio file. The encoded data is passed through a pipeline between
            the encoding and decoding processes without saving intermediate files.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.lc3_path = kwargs["lc3_path"]
        self.name = "LC3"
        
        if (not os.path.exists(os.path.join(self.lc3_path, "bin", "dlc3"))) or (not os.path.exists(os.path.join(self.lc3_path, "bin", "elc3"))):            
            raise RuntimeError(f"liblc3 tools in {self.lc3_path} seem to not be built. Run make tools to build the required binaries.")     
        
    def __call__(self, input_file: str, output_file: str, bitrate:int) -> None:
        """
        Encodes the input audio file using the LC3 codec and decodes the encoded data
        back to an audio file. The encoded data is passed through a pipeline between
        the encoding and decoding processes without saving intermediate files.

        Args:
            input_file (str): The path to the input audio file to be encoded.
            output_file (str): The path where the decoded audio file will be saved.
            bitrate (int): The bitrate to be used for encoding the audio.
        """
        self._verify_audio(input_file)
        
        # Set the LD_LIBRARY_PATH environment variable
        bin_path = os.path.join(self.lc3_path, "bin")
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = bin_path
        
        # Encode the input file
        encode_command = [
            os.path.join(bin_path, "elc3"),
            input_file,
            "-b", str(bitrate)
        ]
        
        # Decode the encoded data
        decode_command = [
            os.path.join(bin_path, "dlc3")
        ]
        
        # Create a pipeline between the encoding and decoding commands
        encode_process = subprocess.Popen(
            encode_command, 
            stdout=subprocess.PIPE, 
            env=env,
            stderr=subprocess.DEVNULL)
        
        decode_process = subprocess.Popen(
            decode_command, 
            stdin=encode_process.stdout, 
            stdout=subprocess.PIPE, 
            env=env,
            stderr=subprocess.DEVNULL
            )
        
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
        **kwargs: Additional keyword arguments. The 'lc3plus_path' argument is required and
            should specify the path to the LC3plus codec binaries.

    Raises:
        RuntimeError: If the required LC3plus codec binaries are not found
            in the specified 'lc3plus_path'.

    Methods:
        __call__(input_file: str, output_file: str, bitrate:int) -> None:
            Encodes the input audio file using the LC3plus codec and decodes the encoded data
            back to an audio file. The encoded data is passed through a pipeline between
            the encoding and decoding processes without saving intermediate files.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.lc3plus_path = kwargs["lc3plus_path"]
        self.lc3plus_bin = os.path.join(self.lc3plus_path, "src", "floating_point", "LC3plus")
        self.name = "LC3Plus"
        
        if "frame_ms" in kwargs:
            self.frame_ms = kwargs["frame_ms"]
        else:
            self.frame_ms = None

        if not os.path.exists(self.lc3plus_bin):
            raise RuntimeError(f"LC3plus binary not found at {self.lc3plus_bin}. Make sure the LC3plus library is built.")

    def __call__(self, input_file: str, output_file: str, bitrate:int) -> None:
        """
        Encodes the input audio file using the LC3plus codec and decodes the encoded data
        back to an audio file.

        Args:
            input_file (str): The path to the input audio file to be encoded.
            output_file (str): The path where the decoded audio file will be saved.
        """
        self._verify_audio(input_file)
        try:
            # Create the command arguments
            if self.frame_ms is None:
                command_args = [self.lc3plus_bin, input_file, output_file, str(bitrate)]
            else:
                command_args = [self.lc3plus_bin, "-frame_ms", str(self.frame_ms), input_file, output_file, str(bitrate)]

            # Run the command using subprocess.run
            subprocess.run(
                command_args,
                check=True,
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
        **kwargs: Additional keyword arguments.

    Methods:
        __call__(input_file: str, output_file: str) -> None:
            Encodes the input audio file using the Opus codec and saves the encoded
            audio to the specified output file.

    Note:
        The Opus codec and its command-line tools (opusenc) must be installed and
        accessible through the system's PATH for this class to function properly.
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = "Opus"
        
    def __call__(self, input_file: str, output_file: str, bitrate: int) -> None:
        """
        Encodes the input audio file using the Opus codec.

        Args:
            input_file (str): The path to the input audio file to be encoded.
            output_file (str): The path where the encoded audio file will be saved.
            bitrate (int): The bitrate to be used for encoding the audio, in bits per second.
        """
        self._verify_audio(input_file)
        try:
            # Open the input file in binary mode
            with open(input_file, "rb") as file:
                input_data = file.read()

            # Create the opusenc process
            opusenc_process = subprocess.Popen(
                ["opusenc", "--quiet", "--hard-cbr", "--bitrate", str(bitrate // 1000), "-", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            # Create the opusdec process
            opusdec_process = subprocess.Popen(
                ["opusdec", "--quiet", "-", output_file],
                stdin=opusenc_process.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Write the input data to opusenc's stdin
            opusenc_process.stdin.write(input_data)
            opusenc_process.stdin.close()

            # Wait for both processes to finish
            opusenc_process.wait()
            opusdec_process.wait()

            # Check if the processes completed successfully
            if opusenc_process.returncode != 0 or opusdec_process.returncode != 0:
                raise subprocess.CalledProcessError(opusenc_process.returncode, "opusenc | opusdec")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Opus encoding failed with exit code: {e.returncode}")

        except Exception as e:
            raise RuntimeError(f"An error occurred during Opus encoding: {str(e)}")


class EVSCodec(AbstractCodec):
    """Concrete implementation of the EVS codec."""
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.evs_path = kwargs["evs_path"]
        self.encoder = os.path.join(self.evs_path, "EVS_cod")
        self.decoder = os.path.join(self.evs_path, "EVS_dec")
        self.name = "EVS"

    def __call__(self, input_file: str, output_file: str, bitrate:int) -> None:
        self._verify_audio(input_file)
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False) as raw_input_file, \
             tempfile.NamedTemporaryFile(suffix='.mime', delete=False) as bitstream_file, \
             tempfile.NamedTemporaryFile(delete=False) as raw_output_file:
            
            try:
                # Encode: Convert WAV to raw PCM, encode to bitstream
                samplerate = self._wav_to_raw(input_file, raw_input_file.name)
                self._encode(raw_input_file.name, bitstream_file.name, bitrate, samplerate)

                # Decode: Convert bitstream to raw PCM, then to WAV
                self._decode(bitstream_file.name, raw_output_file.name, samplerate)
                self._raw_to_wav(raw_output_file.name, output_file, samplerate)         
            
            finally:
                # Ensure temporary files are deleted
                os.remove(raw_input_file.name)
                os.remove(bitstream_file.name)
                os.remove(raw_output_file.name)

    def _encode(self, raw_file: str, bitstream_file: str, bitrate:int, sample_rate:int) -> None:
        """Encode the raw PCM file to an EVS bitstream."""
        
        command = [
            self.encoder,
            "-mime",
            "-q",
            str(bitrate),
            str(sample_rate // 1000),
            raw_file,
            bitstream_file,
        ]
        
        if sample_rate == 48000:
            command.insert(1, "FB")
            command.insert(1, "-max_band")
            
        
        subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )

    def _decode(self, bitstream_file: str, raw_file: str, sample_rate:int) -> None:
        """Decode the EVS bitstream to a raw PCM file."""
        command = [
            self.decoder,
            "-mime",
            "-q",
            str(sample_rate // 1000),
            bitstream_file,
            raw_file,
        ]
        
        subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

    def _wav_to_raw(self, wav_file: str, raw_file: str) -> Tuple[int, int]:
        """Convert a WAV file to raw PCM format expected by the EVS codec."""
        data, samplerate = sf.read(wav_file, dtype='int16')

        data.tofile(raw_file)
        
        return samplerate

    def _raw_to_wav(self, raw_file: str, wav_file: str, sample_rate:int) -> None:
        """Convert raw PCM format back to WAV file."""

        # Read the raw PCM data and write to a WAV file
        # Audio is assumed to be mono
        pcm_data = np.fromfile(raw_file, dtype='int16')

        sf.write(wav_file, pcm_data, sample_rate)