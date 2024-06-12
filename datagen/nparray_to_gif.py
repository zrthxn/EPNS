import os
import numpy as np
from PIL import Image
from upycli import command
from matplotlib import animation, colormaps, pyplot as plt

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
        if len(array.shape) > 3:
            array = array[:, :, :, 0]
        array = array * 255 / (array.max() - array.min())
        
        saveto = os.path.join(output_path, fname.replace(".npy", ".gif"))
        
        gif = [ Image.fromarray(frame).resize((320, 320), resample=Image.Resampling.NEAREST) for frame in array ]
        gif[0].save(saveto, save_all=True, append_images=gif[1:], duration=int((1/fps)*100), loop=0)


@command
def convert_one(path: str = None, fps: int = 12, size: int = 320):
    """Convert set of np-arrays to set of GIFs

    Args:
        directory (str):
        output_path (str):
        fps (int, optional). Defaults to 12.
    """

    if not path.endswith(".npy"):
        raise TypeError("Not a numpy file!")
    
    array: np.ndarray = np.load(path).astype(np.float32)
    if len(array.shape) > 3:
        array = array[:, :, :, 0]
    array = array * 255 / (array.max() - array.min())
    
    saveto = path.replace(".npy", ".gif")
    gif = [ Image.fromarray(frame).resize((size, size), resample=Image.Resampling.NEAREST) for frame in array ]
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
    gif = [ Image.open(os.path.join(directory, fname)).resize((320, 320), resample=Image.Resampling.NEAREST) for fname in DIR ]
    gif[0].save(output_path, save_all=True, append_images=gif[1:], duration=int((1/fps)*100), loop=0)


@command
def color_plots(directory: str, output_path: str = None, cmap: str = "viridis", fps: int = 12):
    if not output_path:
        output_path = directory
    
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".npy"):
            continue
        
        array: np.ndarray = np.load(os.path.join(directory, fname))
        if len(array.shape) > 3:
            array = array[:, :, :, 0]
        fig = plt.figure()

        frames = [
            [plt.imshow(frame, cmap=colormaps[cmap], animated=True, origin="lower")]
            for frame in array
        ]

        ani = animation.ArtistAnimation(fig, frames, interval=int((1/fps)*1000), blit=True, repeat_delay=1000)
        ani.save(os.path.join(output_path, fname.replace(".npy", ".gif")) )
