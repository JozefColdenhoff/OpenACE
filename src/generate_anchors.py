from tqdm import tqdm
import soundfile as sf
import os
import scipy.signal as signal
from omegaconf import DictConfig
import hydra
import pandas as pd
from tqdm.contrib.concurrent import process_map


def filter_and_save_signal(path: str, passband: float, stopband: float, gpass: float = 0.1, gstop: float = 25.0):
    """
    Apply a Chebyshev Type 1 low-pass filter to an audio signal.

    Args:
        path (str): Path to the audio file.
        passband (float): Passband frequency in Hz.
        stopband (float): Stopband frequency in Hz.
        gpass (float, optional): Maximum ripple allowed in passband, in dB. Default is 0.1 dB.
        gstop (float, optional): Minimum attenuation required in stopband, in dB. Default is 25 dB.

    Returns:
        None
    """
    assert 0 < passband < stopband, "Passband must be lower than stopband"
    assert gpass > 0, "Passband ripple must be positive"
    assert gstop > 0, "Stopband attenuation must be positive"

    data, fs = sf.read(path)
    
    # Normalize frequencies
    wp = passband / (0.5 * fs)
    ws = stopband / (0.5 * fs)

    # Design the Chebyshev Type 1 filter
    N, Wn = signal.cheb1ord(wp, ws, gpass, gstop)
    sos = signal.cheby1(N, gpass, Wn, btype='low', output='sos')
    
    filtered = signal.sosfilt(sos, data)
    
    new_path = os.path.join(
        os.path.dirname(path),
        f"lp{passband}.wav"
        )
    
    sf.write(
        file=new_path,
        data=filtered,
        samplerate=fs,
        subtype="PCM_16"
    )
    

def filter_wrapper(args):
    filter_and_save_signal(*args)
        
@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    """

    Args:
        cfg (DictConfig): A Hydra configuration object containing the following keys:
            - metadata_file (str): Path to the metadata CSV file containing 'enc_path' and 'ref_path' columns.

    Raises:
        RuntimeError: If the 'metadata_file' key is not specified in the Hydra configuration.

    Returns:
        None
    """
    
    if cfg.metadata_file is None:
        raise RuntimeError("Please specify the metadata file of the dataset for which to generate anchors")
    
    metadata = pd.read_csv(cfg.metadata_file)
    
    reference_paths = metadata.ref_path.unique() 

    low_args = [(x, 3500, 4000) for x in reference_paths]
    
    process_map(filter_wrapper, low_args, max_workers=10, chunksize=1)
    
    med_args = [(x, 7000, 7500) for x in reference_paths]
    
    process_map(filter_wrapper, med_args, max_workers=10, chunksize=1)
    
    
if __name__ == "__main__":
    main()