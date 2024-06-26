# CONFIG to change:
"""
# stuff from the xml
<StartTime value="0"/>
<StopTime value="500"/>
<Population type="wall" size="1">
<Population type="cell" size="1">
<Gnuplotter time-step="10" decorate="false">

<CellPopulations>
    <Population type="wall" size="1">
        <InitCellObjects mode="distance">
            <Arrangement repetitions="5, 1, 1" displacements="0, 0, 0">
                <Box origin="rand_uni(0.1*size.x,0.9*size.x), rand_uni(0.1*size.y,0.7*size.y), 0" size="Lwall, Lwall, 0"/>
            </Arrangement>
        </InitCellObjects>
    </Population>
    <Population type="cell" size="1">
        <InitCellObjects mode="distance">
            <Arrangement repetitions="1, 1, 1" displacements="1, 1, 1">
                <Sphere center="rand_uni(0.1*size.x,0.9*size.x), rand_uni(0.8*size.y,0.9*size.y), 0" radius="10"/>
            </Arrangement>
        </InitCellObjects>
    </Population>
</CellPopulations>
"""
import os
import time
import subprocess
import numpy as np
from xml.etree import ElementTree
from upycli import command
from tqdm import tqdm

# from datagen.png_to_nparray import convert as convert_png
from datagen.csv_to_nparray import convert as convert_csv, from_csv_frames


# kind of messy but meh
VAR_NAME_MAPPER = {
    "start_time" : {"tag" : "StartTime", "attr" : "value"},
    "stop_time" : {"tag" : "StopTime", "attr" : "value"},
    "time_step" : {"tag" : "Gnuplotter", "attr" : "time-step"},
    "wall_size" : {"tag" : "Population", "attr" : "size", "type" : "wall"},
    "wall_number" : {"tag" : "Arrangement", "attr" : "repetitions", "after_2_type" : "wall"},
    "cell_size" : {"tag" : "Population", "attr" : "size", "type" : "cell"},
    "cell_number" : {"tag" : "Arrangement", "attr" : "repetitions", "after_2_type" : "cell"},
}

# if tuple then first is start, second is increment
CONFIG = {
    "start_time" : 10,
    "stop_time" : 600,
    "time_step" : 10,
    "wall_size" : 1,
    "wall_number" : 8, # (10, 1)
    "cell_size" : 1,  
    "cell_number" : 1,
}

# read in xml
tree = ElementTree.parse("datagen/models/cell_and_walls_id.xml")
root = tree.getroot()


def check_keys(match_key, match_value):
    global VAR_NAME_MAPPER
    # we loop over VAR_NAME_MAPPER and check if its subdirs match
    returns = []

    for key, sub_dict in VAR_NAME_MAPPER.items():
        for sub_key, sub_value in sub_dict.items():
            if sub_key == match_key and sub_value == match_value:
                returns.append((key, sub_dict))

    if len(returns) == 0:
        return False
    return returns


def get_new_value(key: str, index: int, first=False):
    # get the new value based on the id
    # id starts at 1
    global CONFIG
    value = CONFIG[key]

    if type(value) == tuple:
        # here it might be a _number, needed for repetitions
        if str.endswith(key, "_number"):
            return str(value[0]+(index-1))+", 1, 1"
        return value[0]+index-1

    if str.endswith(key, "_number"):
        if first: return value

        return str(value)+", 1, 1"

    return value


old_2 = ""
old = ""
def change_var(elem: ElementTree.Element, index: int):
    global old, old_2, CONFIG
    # first check if the tag is in the var_dir
    if not check_keys("tag", elem.tag):
        return
    # we now know that the elem.tag matches -> get the matching subdict
    val_array = check_keys("tag", elem.tag)

    if len(val_array) == 1:
        # directly change the value
        elem.attrib[val_array[0][1]["attr"]] = str(get_new_value(val_array[0][0], index))
        return
    
    # now multiple possibliities
    for val in val_array:
        if "after_2_type" in val[1]:
            # check if the previous tag is the same as after_2_type
            if old_2 == val[1]["after_2_type"]: 
                elem.attrib[val[1]["attr"]] = str(get_new_value(val[0], index))
                return
            
    # finally check for the type
    for val in val_array:
        if "type" in val[1]:
            if elem.attrib["type"] == val[1]["type"]:
                elem.attrib[val[1]["attr"]] = str(get_new_value(val[0], index))
                return


def change_vars(root: ElementTree.Element, index: int):
    for elem in root.iter():
        # first shift the old values
        global old, old_2
        change_var(elem, index)

        # shift the old values
        old_2 = old
        # does the elem have a type?
        if "type" in elem.attrib:
            old = elem.attrib["type"]
        else:
            old = ""


# =============================================================================
#                       MAIN
# ============================================================================= 

@command
def simulate(
    iterations: int, 
    output_path: str, 
    stop_time: int = 600,
    time_step: int = 10,
    wall_number: int = 8,
    cell_number: int = 1,
    clean: bool = True,
    debug: bool = False):
    """Run Morpheus Simulation.

    Args:
        iterations (int): Number of iterations
        output_path (str): Output Directory
        stop_time (int, optional): Configure morpheus stop time. Defaults to 600.
        time_step (int, optional): Set time for which outputs in form of csv are generated. Defaults to 10.
        wall_number (int, optional): Set wall number, static. If you want to increase this with iterations change the vars dict in this file. Defaults to 8.
        cell_number (int, optional): Cell number, static. If you want to increase this with iterations change the vars dict in this . Defaults to CONFIG["cell_number"].
        plot_hist (bool, optional): Plot the first frame for each iteration. Defaults to False.
        clean (bool, optional): Clean png files after each iteration. Defaults to True.
    """

    print("Starting morpheus with", iterations, "iterations")
    start_time = time.time()
    
    CONFIG["stop_time"] = stop_time
    CONFIG["time_step"] = time_step
    CONFIG["wall_number"] = wall_number
    CONFIG["cell_number"] = cell_number
    
    for index in tqdm(range(iterations)):
        # make a new xml file
        global tree, root
        change_vars(root, index)
        
        # save the xml; add on first line <?xml version='1.0' encoding='UTF-8'?>
        tree.write("temp__cell_and_walls.xml", xml_declaration=True, encoding='utf-8')
        
        output_path = os.path.abspath(output_path)
        # clear all old plot_*.png, .log, .dot, .gp files
        for file in os.listdir(output_path):
            if str.startswith(file, "plot_"):
                os.remove(os.path.join(output_path, file))
            if str.endswith(file, ".log") or str.endswith(file, ".dot") or str.endswith(file, ".gp"):
                pass

        # now start morpheus with the new xml
        command = f"morpheus --file temp__cell_and_walls.xml --outdir {output_path}"
        subprocess.run(command, shell=True, env={"PATH": os.path.join(os.getenv("HOME"), ".local/bin") + ":" + os.getenv("PATH")}, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        try:
            # video = from_csv_frames(output_path)
            # with open(os.path.join(output_path, f"run_{index}.npy"), 'wb') as f:
            #     np.save(f, video)
            convert_csv(output_path, "logger_1_cell.id.csv", 
                save_path=f"{output_path}/run_{index}",
                cell_number=int(get_new_value("cell_number", index, first=True)),
                wall_number=int(get_new_value("wall_number", index, first=True)),
                debug=debug)
        except:
            ...

        # cleanup
        os.remove("temp__cell_and_walls.xml")
        for file in os.listdir(output_path):
            if file.endswith(".gp") or file.endswith(".log") or file.endswith(".dot"):
                os.remove(os.path.join(output_path, file))
            if file.endswith(".csv"):
                os.remove(os.path.join(output_path, file))
            if clean:
                if file.startswith("plot_"):
                    os.remove(os.path.join(output_path, file))

    # print run time in green
    runtime = time.time() - start_time
    print(f"\033[92mRun time: {runtime:.2f} seconds\033[0m")
    print("DONE")
