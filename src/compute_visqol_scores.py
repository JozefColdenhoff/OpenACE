import numpy as np
import soundfile as sf
import resampy
import os
from omegaconf import DictConfig
import hydra
import pandas as pd
from tqdm.contrib.concurrent import process_map
from visqol import visqol_lib_py
from visqol.pb2 import visqol_config_pb2
from visqol.pb2 import similarity_result_pb2 # This is NOT an unused import do not remove

def compute_visqol_48k_numpy(args):
    """
    Computes the VISQOL (Virtual Speech Quality Objective Listener) score between a degraded audio file
    and a reference audio file using the VISQOL library.

    Args:
        args (tuple): A tuple containing two elements:
            - degraded_path (str): The path to the degraded audio file.
            - reference_path (str): The path to the reference audio file.

    Returns:
        float: The VISQOL score representing the perceptual similarity between the degraded and reference audio.

    Raises:
        ValueError: If the sample rates of the degraded and reference audio files do not match.
    """
    degraded_path, reference_path = args
    degraded_data, degraded_samplerate = sf.read(degraded_path)
    reference_data, reference_samplerate = sf.read(reference_path)
    
    if degraded_samplerate != reference_samplerate:
        raise ValueError(f"Sample rates for the reference and degraded file missmatch {os.path.dirname(reference_path)}")
    
    if degraded_samplerate != 48000:
        degraded_data = resampy.resample(degraded_data, degraded_samplerate, 48000, filter='kaiser_best')
        reference_data = resampy.resample(reference_data, reference_samplerate, 48000, filter='kaiser_best')
        
    # convert to mono
    if len(degraded_data.shape) > 1:
        degraded_data = degraded_data.mean(axis=1)
    
    if len(reference_data.shape) > 1:
        reference_data = reference_data.mean(axis=1)
    
    degraded_data = degraded_data.astype(np.float64)
    reference_data = reference_data.astype(np.float64)
    
    config = visqol_config_pb2.VisqolConfig()
    config.audio.sample_rate = 48000
    config.options.use_speech_scoring = False
    svr_model_path = "libsvm_nu_svr_model.txt"
    config.options.svr_model_path = os.path.join(
        os.path.dirname(visqol_lib_py.__file__), "model", svr_model_path)
    api = visqol_lib_py.VisqolApi()

    api.Create(config)

    score = api.Measure(reference_data, degraded_data).moslqo
    
    return score

@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    if cfg.metadata_file is None:
        raise RuntimeError("Please specify the metadata file of the dataset where the VISQOL scores should be computed on.")
    
    metadata = pd.read_csv(cfg.metadata_file)
    
    visqol_args = list(zip(metadata.enc_path, metadata.ref_path))
    
    scores = process_map(compute_visqol_48k_numpy, visqol_args, max_workers=10, chunksize=1)
    
    metadata["VISQOL_Scores"] = scores
    
    save_path = os.path.join(
        os.path.dirname(cfg.metadata_file),
        "visqol_scores.csv"
    )
    metadata.to_csv(save_path, index=False)
    
if __name__ == "__main__":
    main()