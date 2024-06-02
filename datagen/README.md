| Version | 0.0.1 |
| --- | --- |
| Author | P. Zschoppe |

# biomath-seminar

`run_morpheus.py` is the central script in this dir. Configure its properties
by changing values in the `vars` dict.

The script will interprete single values as constants and tuples as `(start, increment)`
running for n-iterations.
Each iteration will put its changes into an .xml and run `morpheus` with it.

Afterwards `png_to_array.py` gets called, turning the pngs into numpy arrays.

# Usage

Just run `run_morpheus.py`, should work under win, tested for lin (Ubuntu 22.04 LTS).
Using morpheus 2.3.7 (lin build).

Note that if `clean_png` is turned of the script will not reset the data folder, thus
runing morpheus with f.e. 10-20s and 20-30s afterwards will result in having both time
series in data. Resulting numpy arrays will then include both. Best run once for testing without
clean to check the .png results and then turn the cleaning on.

`plot_hist` is also usefull for testing as it will plot the greyscale hist of the first png.
