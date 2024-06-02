# vars to change:
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
import xml.etree.ElementTree as ET
from upycli import command

from png_to_array import convert


# kind of messy but meh
old_2 = ""
old = ""
ID = 1
HOME = os.getenv("HOME")


VAR_NAME_MAPPER = {
    "start_time" : {"tag" : "StartTime", "attr" : "value"},
    "stop_time" : {"tag" : "StopTime", "attr" : "value"},
    "time_step" : {"tag" : "Gnuplotter", "attr" : "time-step"},
    "wall_size" : {"tag" : "Population", "attr" : "size", "type" : "wall"},
    "wall_number" : {"tag" : "Arrangement", "attr" : "repetitions", "after_2_type" : "wall"},
    "cell_size" : {"tag" : "Population", "attr" : "size", "type" : "cell"},
    "cell_number" : {"tag" : "Arrangement", "attr" : "repetitions", "after_2_type" : "cell"},
}

# read in xml
tree = ET.parse("datagen/models/cell_and_walls.xml")
root = tree.getroot()


def check_keys(match_key, match_value):
    global VAR_NAME_MAPPER
    # we loop over var_dict and check if its subdirs match
    returns = []

    for key, sub_dict in VAR_NAME_MAPPER.items():
        for sub_key, sub_value in sub_dict.items():
            if sub_key == match_key and sub_value == match_value:
                returns.append((key, sub_dict))

    if len(returns) == 0:
        return False
    return returns


def get_new_value(key):
    # get the new value based on the id
    # id starts at 1
    global CONFIG, ID
    value = CONFIG[key]

    if type(value) == tuple:
        # here it might be a _number, needed for repetitions
        if str.endswith(key, "_number"):
            return str(value[ID-1])+", 1, 1"

        return value[ID-1]

    if str.endswith(key, "_number"):
        return str(value)+", 1, 1"

    return value


def change_var(elem):
    global old, old_2
    # first check if the tag is in the var_dir
    if not check_keys("tag", elem.tag):
        return
    # we now know that the elem.tag matches -> get the matching subdict
    val_array = check_keys("tag", elem.tag)

    if len(val_array) == 1:
        # directly change the value
        elem.attrib[val_array[0][1]["attr"]] = str(get_new_value(val_array[0][0]))
        print("Changed ", val_array[0][0], " to ", get_new_value(val_array[0][0]))
        return
    
    # now multiple possibliities
    for val in val_array:
        if "after_2_type" in val[1]:
            # check if the previous tag is the same as after_2_type
            if old_2 == val[1]["after_2_type"]: 
                elem.attrib[val[1]["attr"]] = str(get_new_value(val[0]))
                print("Changed ", val[0], " to ", get_new_value(val[0]))
                return
            
    # finally check for the type
    for val in val_array:
        if "type" in val[1]:
            if elem.attrib["type"] == val[1]["type"]:
                elem.attrib[val[1]["attr"]] = str(get_new_value(val[0]))
                print("Changed ", val[0], " to ", get_new_value(val[0]))
                return


def change_vars(root):
    for elem in root.iter():
        # first shift the old values
        global old, old_2
        change_var(elem)

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

def run_simulation(output_path, hist, clean):
    global tree, root, ID
    change_vars(root)
    ID += 1
    # make a new xml file
    
    # add on first line
    # <?xml version='1.0' encoding='UTF-8'?>
    
    # save the xml
    tree.write("cell_and_walls_temp.xml", xml_declaration=True, encoding='utf-8')
    
    data_path = os.path.abspath(output_path)
    # clear all old plot_*.png, .log, .dot, .gp files
    for file in os.listdir(data_path):
        if str.startswith(file, "plot_"):
            os.remove(os.path.join(data_path, file))
        if str.endswith(file, ".log") or str.endswith(file, ".dot") or str.endswith(file, ".gp"):
            pass
            #os.remove(os.path.join(data_path, file))

    # now start morpheus with the new xml
    command = "morpheus --file cell_and_walls_temp.xml --outdir " + data_path
    subprocess.run(command, shell=True, env={"PATH": HOME + "/.local/bin:" + os.getenv("PATH")}, 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
    
    # now we have a bunch of .gp files, that need some editing
    # set style line 40 lc rgb "black" lw 1 -> set style line 40 lc rgb "black" lw 0
    # set term pngcairo  enhanced size 600.00,600.00 font "Verdana,15.19" lw 1.00 truecolor ;
    # -> set term pngcairo  enhanced size X,X font "Verdana,15.19" lw 1.00 truecolor ;

    # edit each .gp file in the data folder and then run it
    for file in os.listdir(data_path):
        if str.endswith(file, ".gp"):
            with open(os.path.join(data_path, file), "r") as f:
                lines = f.readlines()
            
            with open(os.path.join(data_path, file), "w") as f:
                for line in lines:
                    if "set style line 40 lc rgb \"black\" lw 1" in line:
                        f.write("set style line 40 lc rgb \"black\" lw 0\n")
                    #elif "set term pngcairo  enhanced size 600.00,600.00 font \"Verdana,15.19\" lw 1.00 truecolor ;" in line:
                    #    f.write("set term pngcairo  enhanced size 100.00,100.00 font \"Verdana,15.19\" lw 1.00 truecolor ;\n")
                    else:
                        f.write(line)

            # now run the .gp file inside the data folder
            command = "gnuplot " + file
            subprocess.run(command, shell=True, cwd=data_path, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # now queue the eval script
    # naming of the pngs: plot_00000.png -> plot_00010.png
    data_array_name = f"{data_path}/run_{str(ID-1)}"
    convert(data_path, "plot_", save_path=data_array_name, hist=hist)

    # cleanup, remove the temp xml, all .gp, .log, .dot files
    os.remove("cell_and_walls_temp.xml")
    for file in os.listdir(data_path):
        if str.endswith(file, ".gp") or str.endswith(file, ".log") or str.endswith(file, ".dot"):
            os.remove(os.path.join(data_path, file))
        if clean:
            if str.startswith(file, "plot_"):
                os.remove(os.path.join(data_path, file))



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


@command
def simulate(iterations: int, output_path: str, plot_hist: bool = False, clean_png: bool = True):
    
    print("Starting morpheus with", iterations, "iterations")
    
    for i in range(iterations):
        print("Iteration", i + 1)
        start_time = time.time()

        run_simulation(output_path, plot_hist, clean_png)

        # print run time in green
        runtime = time.time() - start_time
        print(f"\033[92mRun time: {runtime:.2f} seconds\033[0m")
        print("DONE")
