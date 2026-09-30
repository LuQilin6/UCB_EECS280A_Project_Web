CS180/CS280A Project 2 - Fun with Filters and Frequencies
==========================================================

All code is in main.ipynb (a Jupyter notebook). The project webpage is
index.html (with style.css and script.js).

REQUIREMENTS
------------
- Python 3.9+ (developed with Python 3.11)
- Packages listed in requirements.txt:
    numpy scipy matplotlib scikit-image opencv-python ipykernel jupyter

SETUP
-----
Run these from this directory (projects/project2/). The virtual
environment (.venv) is not stored in git, so create it once per machine.

Windows (PowerShell):
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe -m ipykernel install --user --name proj2 --display-name "Python (proj2)"


FOLDER LAYOUT
-------------
    project2/
      main.ipynb          all code, results and write-up
      requirements.txt    Python dependencies
      requirement.pdf     assignment description
      index.html          project webpage (+ style.css, script.js)
      data/               input images (see below)
      out/                output images, written by the notebook

INPUT IMAGES (data/)
--------------------
  Part 1.1           selfie.jpg (grayscale, resized to max side 300)
  Part 1.2 / 1.3     cameraman.png (falls back to skimage.data.camera()
                     if missing)
  Part 2.1           taj.jpg, selfchoose.jpg (my cat)
  Part 2.2           DerekPicture.jpg + nutmeg.jpg (required pair)
                     selfhybrid21.jpg + selfhybrid22.jpg (me + my cat's face)
                     selfhybrid11alt.jpg + selfhybrid12.jpg (onigiri + my
                     cat's back)
  Part 2.3 / 2.4     apple.jpeg + orange.jpeg
  Part 2.4           selfhybrid21.jpg + selfhybrid22.jpg (half me, half cat)
                     coffee3.jpg + selfhybrid22.jpg (cat latte)

Naming of my own hybrid images: selfhybrid{group}{who}, where group is
the hybrid number and who is 1 = me, 2 = my cat (e.g. selfhybrid12 =
group 1, cat). selfhybrid11alt.jpg is the onigiri that replaces
selfhybrid11.jpg (my back) in group 1.

HOW TO RUN
----------
Open main.ipynb and choose "Run All" (or run the cells top to bottom).
Later parts reuse functions and variables from earlier parts,
so after restarting the kernel, always start again from the Setup cell.

The notebook does not need the course starter files
(align_image_code.py, hybrid_image_starter.py); the parts that were used
(the get_points click helper) are copied into the Part 2.2 cells.


OUTPUT
------
Every figure the webpage needs is saved as a PNG in out/, named by part:
    p11_*   Part 1.1          p21_*    Part 2.1
    p12_*   Part 1.2          p22_*    Part 2.2   (p22bw_* = B&W)
    p13_*   Part 1.3          p23_*    Part 2.3
    p1bw_*  Part 1 B&W        p24_*    Part 2.4   (p24bw_* = B&W)
