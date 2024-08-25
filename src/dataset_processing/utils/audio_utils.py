import soundfile as sf 
import numpy as np
from typing import List
import glob

def convert_flac_to_wav(filepath:str) -> None:
    """
    Converts a FLAC audio file to WAV format.

    This function takes the file path of a FLAC audio file as input and converts it to WAV format.
    The converted WAV file will be saved in the same directory as the original FLAC file, with the same
    filename but with a ".wav" extension. If the file is not a flac file it will be ignored.

    Parameters:
        filepath (str): The file path of the FLAC audio file to be converted.

    Returns:
        None
    """
    filename, ext = os.path.splitext(filepath)
    if ext != ".flac":
        return
    
    data, samplerate = sf.read(filepath)
    sf.write(filename + ".wav", data, samplerate)
    
def get_audio_files(path: str, audio_extensions: List[str] = None) -> Tuple[List[str], List[str]]:
    """
    Retrieves the absolute and relative file paths of audio files in a given directory.

    This function searches for audio files with specified extensions within the given directory
    and its subdirectories. It returns two lists: one with absolute paths and another with relative paths.

    Args:
        path (str): The root directory where the search for audio files will begin.
        audio_extensions (List[str], optional): A list of audio file extensions to search for.
                                                If not provided, defaults to ['wav', 'flac'].

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists:
            - The first list contains absolute paths to the audio files.
            - The second list contains paths relative to the provided directory.
    """
    if audio_extensions is None:
        audio_extensions = ['wav', 'flac']
        
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(f"{path}/**/*.{ext}", recursive=True))
    
    abs_paths = audio_files
    rel_paths = [os.path.relpath(file, path) for file in audio_files]
    
    return abs_paths, rel_paths