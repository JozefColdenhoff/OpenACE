import pandas as pd
import soundfile as sf
from typing import List, Tuple
import pandas as pd
import resampy
import os
import glob
from omegaconf import DictConfig
import hydra
from hydra.utils import instantiate
from tqdm.contrib.concurrent import process_map
from definitions import DATA_PATH

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

def generate_directory_tree(file_paths: List[str], new_root_dir: str) -> None:
    """
    Creates a directory structure under a new root directory based on a list of relative file paths.

    This function replicates the directory structure implied by the given relative file paths within
    a specified new root directory. For each file path provided, a corresponding directory is created
    in the new root directory, where the directory's name is derived from the file name (excluding its extension).

    Args:
        file_paths (List[str]): A list of relative file paths. The directory structure of each path will be
                                replicated under the new root directory, with each directory named after the file
                                without its extension.
        new_root_dir (str): The base directory where the new directory structure will be created.

    Returns:
        None

    Example:
        If `file_paths` contains ['folder1/audio1.wav', 'folder2/subfolder/audio2.flac'] and 
        `new_root_dir` is '/new/root', the following directories will be created:

        /new/root/folder1/audio1
        /new/root/folder2/subfolder/audio2
    """
    for file_path in file_paths:
        
        # Extract the directory path of the file
        directory, ext = os.path.splitext(file_path)
        
        # Combine the new root directory with the file's directory path
        new_directory = os.path.join(new_root_dir, directory)
        
        # Create the directory if it doesn't exist
        os.makedirs(new_directory, exist_ok=True)

def process_and_save_reference_file(args):
    """
    Processes a reference audio file and saves it with a specific naming convention.

    This function takes a tuple of arguments containing the absolute file path, relative file path,
    and a new root directory. It reads the audio data from the file, resamples it to 48kHz if necessary,
    and saves the processed audio file with a specific naming convention based on the sample rate.

    Parameters:
        args (tuple): A tuple containing the following elements:
            - abs_filepath (str): The absolute file path of the reference audio file.
            - rel_filepath (str): The relative file path of the reference audio file.
            - new_root (str): The new root directory where the processed audio file will be saved.

    Returns:
        None
    """
    abs_filepath, rel_filepath, new_root = args
    
    data, samplerate = sf.read(abs_filepath)
        
    save_folder, _ = os.path.splitext(rel_filepath)
    
    if samplerate == 44100:
        data = resampy.resample(data, samplerate, 48000, filter='kaiser_best')    
        samplerate = 48000
        new_save_path = os.path.join(new_root, save_folder, "reference_re.wav")
    
    else:
        new_save_path = os.path.join(new_root, save_folder, "reference.wav")
    
    sf.write(
        file=new_save_path, 
        data=data,
        samplerate=samplerate,
        subtype="PCM_24"
        )

def apply_and_save_codec(args) -> None:
    """
    Applies a specified audio codec to an audio file and saves the encoded file.

    This function takes a tuple of arguments containing the original file path, the codec to be applied,
    and the desired bitrate. It applies the specified codec to the original audio file and saves the
    encoded file in the same directory as the original file, with the codec name appended to the filename.

    Parameters:
        args (tuple): A tuple containing the following elements:
            - original_path (str): The file path of the original audio file.
            - codec (Callable): The audio codec to be applied. It should be a callable object that takes
                                the original file path, the new file path, and the bitrate as arguments.
            - bitrate (int): The desired bitrate for the encoded audio file.

    Returns:
        str: The file path of the newly encoded audio file.
    """
    original_path, codec, bitrate = args
    new_path = os.path.join(
        os.path.dirname(original_path),
        codec.name + ".wav"        
        )
    codec(original_path, new_path, bitrate)
    return new_path, original_path

@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    """
    Process an audio dataset, apply codecs, and generate a metadata file.

    This function takes a Hydra configuration object as input and performs the following steps:
    1. Retrieves a list of unprocessed audio files from the "original" directory.
    2. If it's a test run, limits the number of files to 10.
    3. Creates directories to store the processed data based on the bitrate.
    4. Generates a directory tree for the processed files.
    5. Converts the original audio files to 24-bit PCM WAV format using parallel processing.
    6. Applies specified codecs to the processed audio files using parallel processing.
    7. Generates a metadata file containing information about the encoded and reference files.
    8. Adds audio metadata to the metadata DataFrame.
    9. Adds an "encoder" column to the metadata indicating the encoding type.
    10. Saves the metadata file in the processed data directory.

    Args:
        cfg (DictConfig): A Hydra configuration object containing the following keys:
            - test_run (bool): Flag indicating whether it's a test run with a limited number of files.
            - bitrate (int): The bitrate used for encoding the audio files.
            - codecs (dict): A dictionary specifying the codecs to be applied to the audio files.

    Returns:
        None
    """
    # Get a list of the original unprocessed dataset
    original_data_path = os.path.join(DATA_PATH, "original")
    unprocessed_abs_paths, unprocessed_rel_paths = get_audio_files(path=original_data_path)
    
    if cfg.test_run:
        unprocessed_abs_paths = unprocessed_abs_paths[:10]
        unprocessed_rel_paths = unprocessed_rel_paths[:10]
    
    # Create the folders to store the processed data
    if cfg.test_run:
        processed_root_dir = os.path.join(DATA_PATH, "processed", f"bitrate={cfg.bitrate//1000}_test")
    else:
        processed_root_dir = os.path.join(DATA_PATH, "processed", f"bitrate={cfg.bitrate//1000}")
    
    os.makedirs(processed_root_dir)
    
    generate_directory_tree(
        file_paths=unprocessed_rel_paths, 
        new_root_dir=processed_root_dir
        )    

    # Convert all the original audio to 24-bit PCM wav files. 
    # Create a list of arguments for each file
    file_args = [(abs_path, rel_path, processed_root_dir) for abs_path, rel_path in zip(unprocessed_abs_paths, unprocessed_rel_paths)]
    # Use process_map to process files concurrently
    process_map(process_and_save_reference_file, file_args, max_workers=10, chunksize=1)
    
    # Generate metadata file
    processed_abs_paths, processed_rel_paths = get_audio_files(path=processed_root_dir)
    
    encoded_paths = []
    for codec_name, codec_args in cfg.codecs.items():
        codec = instantiate(codec_args)
        codec_args = [(processed_abs_path, codec, cfg.bitrate) for processed_abs_path in processed_abs_paths]
        encoded_paths.extend(process_map(apply_and_save_codec, codec_args, max_workers=10, chunksize=1))
    
    metadata = pd.DataFrame(
        data={
            "enc_path":[x[0] for x in encoded_paths],
            "ref_path": [x[1] for x in encoded_paths]
            }
        )
    
    metadata = add_audio_metadata_to_df(metadata, path_column="enc_path")
    
    # Add encoding type
    metadata["encoder"] = metadata["enc_path"].apply(lambda x: x.split(os.sep)[-1].split(".")[0])
    
    metadata.to_csv(
        os.path.join(
            processed_root_dir,
            f"metadata_bitrate={cfg.bitrate//1000}.csv"
        ),
        index=False
    )
    
if __name__ == "__main__":
    main()