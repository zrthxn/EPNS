# convert a csv of simulation data to an array for training
# with following structure;
# 100 0 1 2 3 ... 99
# 0   X X X X ... X
# 1   X X X X ... X
# .
# 99  X X X X ... X
#
#
#
# 100 ...
# ...

# here each box represents one frame from the simulation
# frames are seperated by 3 empty lines
# with coordinates on a 2D grid, from 0 to 99
# possible values for X:
# 0: empty/background
# 1-k: k walls
# k+1 - k+1+n: n cells

import os
import numpy as np
import pandas as pd
from upycli import command


@command
def convert(
        path_name: str, 
        file_name: str, 
        save_name: str = None, 
        cell_number: int = 2, 
        wall_number: int = 8,
        size: int = 100, 
        plot: bool = False):
    
    if save_name is None:
        save_name = file_name

    # read in the csv and parse it into single frames
    if not os.path.isdir(path_name):    
        # maybe the / or \ is missing
        # is win?
        path_name = os.path.join(path_name, "")
        if not os.path.isdir(path_name): 
            raise ValueError("Path is not a folder")
        
    csv_path = os.path.join(path_name, file_name)
    csv_raw = pd.read_csv(csv_path, header=None, sep="\t")
    
    # each frame has takes size+1 rows, empty lines got collapsed by pandas
    frames = int(len(csv_raw) / (size+1))

    # print in color
    print("\033[92m>> Reading in csv file\033[0m")
    print("| frames: ", frames)
    print("| cells: ", cell_number)
    print("| walls: ", wall_number)

    # form this into an nd array of dim (t, h, w, c)
    # t = time steps, h = height, w = width, c = channels == 2
    arr = np.zeros((frames, size, size, 2))

    # iterate over the frames and fill the array
    for i in range(frames):
        # get the frame
        frame = csv_raw.iloc[i*(size+1):(i+1)*(size+1), :]
        frame = frame.to_numpy()
        # get the grid
        grid = frame[1:, 1:]
        grid = grid.astype(np.int32)

        # fix sorting issue, by inverting the numbers
        map = np.arange(1, cell_number+wall_number+1)
        map = np.flip(map)

        # add back the 0 for the background
        map = np.append([0], map)
        grid = map[grid]

        # postprocessing for EPNS
        # for (. . . 0): Back: 0, Cell: 1-cell_number
        # Wall: cell_number+1
        grid_0 = np.copy(grid)
        grid_0[grid_0 > cell_number] = cell_number+1

        # for (. . . 1): Back: 0, Cell: 1, Wall: 2
        grid_1 = np.copy(grid_0)
        grid_1[(grid > 0) & (grid < (cell_number+1))] = 1
        grid_1[grid_1 == (cell_number+1)] = 2

        # fill the array
        arr[i, :, :, 0] = grid_0
        arr[i, :, :, 1] = grid_1

    
    # plot the first frame to check if everything is correct
    if plot:
        import matplotlib.pyplot as plt
        # make 2 subplots with colorbars
        fig, axs = plt.subplots(1, 2)
        im1 = axs[0].imshow(arr[0, :, :, 0], cmap="viridis")
        im2 = axs[1].imshow(arr[0, :, :, 1], cmap="viridis")

        fig.colorbar(im1, ax=axs[0])
        fig.colorbar(im2, ax=axs[1])

        # flip y axis so that 0 is at bottom
        axs[0].invert_yaxis()
        axs[1].invert_yaxis()
        plt.show()

    # make save dir if not exists
    if not os.path.exists("data_nparray"):
        os.makedirs("data_nparray")

    # save array
    np.save(os.path.join("data_nparray", save_name), arr)
