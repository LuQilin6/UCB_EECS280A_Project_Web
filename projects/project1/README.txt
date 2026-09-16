CS180/CS280A Project 1 - Images of the Russian Empire
======================================================

REQUIREMENTS
------------
- Python 3.9+
- numpy
- scikit-image

Install with:
    pip install numpy scikit-image

FOLDER LAYOUT
-------------
Run the script from this directory (project1/). It expects the data
folder alongside main.py:

    project1/
      main.py
      CS180_fa2026_proj1_data/
        cathedral.jpg
        monastery.jpg
        emir.tif
        ... (other provided .jpg/.tif plate scans)

Only files directly inside CS180_fa2026_proj1_data/ are picked up
(subfolders like __MACOSX and non-image files are ignored).

HOW TO RUN
----------
    python main.py

This will:
  1. Find every .jpg/.jpeg/.tif/.tiff file in CS180_fa2026_proj1_data/.
  2. For each one: split into B/G/R, align G and R onto B using a
     gradient/edge-based coarse-to-fine pyramid search (NCC metric by
     default), then apply auto-cropping, auto-contrast, gray-world white
     balance, and a fixed color-mapping matrix. 
  3. Save the colorized JPEG and shift value in the out directory under different setting. 
    It also print the computed (dx, dy) shifts for
     G and R to the console.

OUTPUT
------
Results are written under out/, in a subfolder named after the alignment
method and metric used, e.g.:

    out/features_ncc_4/cathedral.jpg
    out/features_ncc_4/results.csv

results.csv logs, per image, the computed g_dx/g_dy/r_dx/r_dy shift
values used to align that image.

RUNNING ON THE SELF-CHOSEN IMAGES
----------------------------------
main() has a commented-out block for processing your own extra images
placed in CS180_fa2026_proj1_data/SelfChoosePic/ (named selfchoose1.jpg,
selfchoose2.jpg, selfchoose3.jpg). Uncomment that loop in main() to run
those too.

SWITCHING METRICS
------------------
process_image() takes a metric= argument (score_ncc or score_l2, both
defined in proj1.py). Edit the calls inside main() to try the other one;
results land in a differently-named out/ subfolder so both can be
compared side by side.

SWITCHING ALIGNMENT METHOD
------------------
You can swith the alignment method inside align() function by uncmoment the 
method you want to use.