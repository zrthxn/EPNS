import os
import cv2
import numpy as np
from upycli import command
from matplotlib import pyplot as plt
from PIL import Image

@command
def convert(directory: str, output_path: str = None, fps: int = 12):
    """Convert set of np-arrays to set of videos

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
        
        array: np.ndarray = np.load(os.path.join(directory, fname))
        length, height , width = array.shape

        saveto = os.path.join(output_path, fname.replace(".npy", ".mp4")) 
        video = cv2.VideoWriter(saveto, -1, fps, (width, height), isColor=True)
        
        for fnum in range(length):
            video.write(array[fnum])
            
        cv2.destroyAllWindows()
        video.release()


@command
def from_pngs(directory: str, output_fname: str, fps: int = 12):
    """Convert set of pngs to a video

    Args:
        directory (str)
        output_path (str)
        fps (int, optional). Defaults to 12.
    """

    video = None
    
    for fname in sorted(os.listdir(directory), key=lambda x: int(os.path.splitext(x)[0].split("_")[-1])):
        if not fname.endswith(".png"):
            continue
        
        image = cv2.imread(os.path.join(directory, fname))
        
        if video is None:
            height, width, _ = image.shape
            video = cv2.VideoWriter(output_fname, -1, fps, (width, height), isColor=True)

        video.write(image)
        
    video.release()
    cv2.destroyAllWindows()