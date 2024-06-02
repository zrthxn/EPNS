import os
import cv2
import numpy as np
from upycli import command


@command
def convert(path: str, video_name: str, save_path: str = None, hist: bool = False):
    """ convert set of pngs to array we need for training
    """

    # we wanna make nd arrays of the form (t, h, w, c)
    # t = time steps, h = height, w = width, c = channels
    # where only 2 channels are used in EPNS first for nr of cells,
    # second for type, only use first channel for now 

    # check if path points to a folder
    if not os.path.isdir(path):    
        # maybe the / or \ is missing
        # is win?
        if os.name == "nt":
            path += "\\"
        else:
            path += "/"
        if not os.path.isdir(path): 
            raise ValueError("Path is not a folder")

    if save_path is None:
        save_path = video_name

    # first get how many frames we have
    frames = []

    for file in os.listdir(path):
        if file.startswith(video_name):
            frames.append(file)
    
    frames.sort()
    print("Frames: ", len(frames))

    # get the first frame to get the shape of the images
    frame = cv2.imread(os.path.join(path, frames[0]))
    print("Shape of image: ", frame.shape)

    # make it into greyscale and then analye color values
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if hist:
        # make historgram of greyscale values
        import matplotlib.pyplot as plt
        plt.hist(gray_frame.ravel(), 256, [0, 256])
        plt.title("Histogram of greyscale values")
        plt.show()

    # create array
    arr = np.zeros((len(frames), frame.shape[0], frame.shape[1], 2))
    for i, frame in enumerate(frames):
        img = cv2.imread(os.path.join(path, frame))
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        arr[i, :, :, 0] = gray_img
        # save the same to the second channel, we dont have differnt cells currently
        arr[i, :, :, 1] = gray_img

    print("Array shape: ", arr.shape)

    # save array
    np.save(save_path, arr)
