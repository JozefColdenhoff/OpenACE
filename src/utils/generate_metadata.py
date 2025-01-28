from utils.utils import get_audio_files, add_audio_metadata_to_df
from argparse import ArgumentParser
import pandas as pd
import os

def main(base_path):
    """Simple utility script that generates audio metadata based on a base path.
    
    Finds all the wav/flac files in the directory and subdirectories and adds 
    file metadata to the column. The following attributes are added:
        - "sample_rate" (int): The sample rate of the audio file in Hz.
        - "channels" (int): The number of audio channels (e.g., 1 for mono, 2 for stereo).
        - "duration" (float): The duration of the audio file in seconds.
        - "format" (str): The format of the audio file (e.g., 'WAV', 'FLAC').
        - "subtype" (str): The subtype or encoding of the audio file (e.g., 'PCM_16').

    Args:
        base_path (str): path to the root directory.
    """    
    abs_paths, rel_paths = get_audio_files(path=base_path)
    metadata = pd.DataFrame(
        data={
            "abs_path":abs_paths,
            "rel_path": rel_paths
            }
        )
    metadata = add_audio_metadata_to_df(metadata, path_column="abs_path")
    metadata.to_csv(os.path.join(base_path, "metadata.csv"))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--base_path")
    args = parser.parse_args()
    main(base_path= args.base_path)