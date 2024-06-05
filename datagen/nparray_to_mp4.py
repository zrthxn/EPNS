import os
import cv2
import numpy as np
from upycli import command


@command
def convert(directory: str, output_path: str, fps: int = 12):
    """Convert set of np-arrays to set of videos

    Args:
        directory (str):
        output_path (str):
        fps (int, optional). Defaults to 12.
    """
    
    for fname in os.listdir(directory):
        if not fname.endswith(".npy"):
            continue
        
        array: np.ndarray = np.load(fname)
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

    saveto = os.path.join(output_fname)
    video = None
    
    for fname in os.listdir(directory):
        if not fname.endswith(".png"):
            continue
        
        print(os.path.join(directory, fname))
        image = cv2.imread(os.path.join(directory, fname))
        
        if video is None:
            height, width, _ = image.shape
            video = cv2.VideoWriter(saveto, -1, fps, (width, height), isColor=True)

        video.write(image)
        
    cv2.destroyAllWindows()
    video.release()