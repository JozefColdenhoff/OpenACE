from abc import ABC, abstractmethod
import os
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
    It inherits from the AbstractCodec class and implements the required methods. It 
    requires the liblc3 library to be build inclusing it's tools.

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