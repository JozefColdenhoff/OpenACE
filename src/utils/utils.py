import pandas as pd 
import os 
import glob
import soundfile as sf
from typing import List, Tuple

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

def get_audio_metadata(path: str) -> dict:
    """
    Extracts metadata from an audio file using the pysoundfile library.

    This function takes the path to an audio file and returns a dictionary containing
    key metadata about the audio file, including the sample rate, number of channels,
    duration, format, and subtype.

    Args:
        path (str): The file path to the audio file for which metadata is to be extracted.

    Returns:
        dict: A dictionary containing the following keys:
            - "sample_rate" (int): The sample rate of the audio file in Hz.
            - "channels" (int): The number of audio channels (e.g., 1 for mono, 2 for stereo).
            - "duration" (float): The duration of the audio file in seconds.
            - "format" (str): The format of the audio file (e.g., 'WAV', 'FLAC').
            - "subtype" (str): The subtype or encoding of the audio file (e.g., 'PCM_16').
    """
    audio_metadata = sf.info(path)
    
    return_dict = {
        "sample_rate": audio_metadata.samplerate,
        "channels": audio_metadata.channels,
        "duration": audio_metadata.duration,
        "format": audio_metadata.format_info,
        "subtype": audio_metadata.subtype_info
    }
    return return_dict

def add_audio_metadata_to_df(df: pd.DataFrame, path_column:str) -> pd.DataFrame:
    """
    Adds audio metadata to a DataFrame by extracting information from audio files.

    This function takes a DataFrame containing a column with file paths to audio files.
    It applies the `get_audio_metadata` function to each file path in the specified column
    to extract metadata such as sample rate, channels, duration, format, and subtype.
    The extracted metadata is then added as new columns to the original DataFrame.

    Args:
        df (pd.DataFrame): A pandas DataFrame that contains a column with file paths to audio files.
        path_column (str): The name of the column in `df` that contains the file paths to the audio files.

    Returns:
        pd.DataFrame: A pandas DataFrame with additional columns for the extracted audio metadata:
            - 'sample_rate': The sample rate of the audio file in Hz.
            - 'channels': The number of audio channels.
            - 'duration': The duration of the audio file in seconds.
            - 'format': The format of the audio file (e.g., 'WAV', 'FLAC').
            - 'subtype': The subtype or encoding of the audio file (e.g., 'PCM_16').
    """
    # Apply the get_audio_metadata function to each row and expand the dictionary into columns
    metadata_df = df[path_column].apply(lambda x: pd.Series(get_audio_metadata(x)))
    
    # Concatenate the original DataFrame with the new metadata columns
    df = pd.concat([df, metadata_df], axis=1)
    
    return df