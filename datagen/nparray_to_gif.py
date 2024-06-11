import os
import re
import numpy as np
from upycli import command
from matplotlib import pyplot as plt
from PIL import Image


@command
def convert(directory: str, output_path: str = None, fps: int = 12):
    """Convert set of np-arrays to set of GIFs

    Args:
        directory (str):
        output_path (str):
        fps (int, optional). Defaults to 12.
    """
    if not output_path:
        output_path = directory

    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".npy"):
            continue
        
        array: np.ndarray = np.load(os.path.join(directory, fname)).astype(np.float32)
        array = (array - array.max())  * 255 / (array.min() - array.max())
        
        saveto = os.path.join(output_path, fname.replace(".npy", ".gif"))
        
        gif = [ Image.fromarray(frame) for frame in array ]
        gif[0].save(saveto, save_all=True, append_images=gif[1:], duration=int((1/fps)*100), loop=0)


@command
def from_pngs(directory: str, output_path: str = None, fps: int = 12):
    """Convert set of np-arrays to set of GIFs

    Args:
        directory (str):
        output_path (str):
        fps (int, optional). Defaults to 12.
    """
    if not output_path:
        output_path = os.path.join(directory, "video.gif")
        
    DIR = [ fname for fname in os.listdir(directory) if fname.endswith(".png") ]
    DIR = sorted(DIR, key=lambda x: int(os.path.splitext(x)[0].split("_")[1]))
    gif = [ Image.open(os.path.join(directory, fname)) for fname in DIR ]
    gif[0].save(output_path, save_all=True, append_images=gif[1:], duration=int((1/fps)*100), loop=0)
