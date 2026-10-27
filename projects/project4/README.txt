CS180/CS280A Project 4A - Image Warping and Mosaicing
=====================================================

All code is in partA.ipynb (a Jupyter notebook). The project webpage is
index.html (with style.css and script.js).

REQUIREMENTS
------------
- Python 3.9+ (developed with Python 3.11)
- Packages listed in requirements.txt:
    numpy scipy matplotlib pillow ipykernel jupyter
- macOS for the point-clicking windows (%matplotlib osx). On other
  systems, see "Clicking points" below.

SETUP
-----
Run these from this directory (projects/project4/). The virtual
environment (.venv) is not stored in git, so create it once per machine.

macOS / Linux:
    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python -m ipykernel install --user --name proj4 --display-name "Python (project4)"

Windows (PowerShell):
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe -m ipykernel install --user --name proj4 --display-name "Python (project4)"

Then open partA.ipynb and pick the "Python (project4)" kernel.

FOLDER LAYOUT
-------------
    project4/
      partA.ipynb         all code, results and notes (A.1 - A.5)
      requirements.txt    Python dependencies
      index.html          project webpage (+ style.css, script.js)
      data/               input photos
      data/points/        saved correspondences (JSON), written by the notebook
      out/                output images, written by the notebook
      assets/             extra image made only for the webpage
                          (mosaic1_seam_zoom.jpg, a crop of out/ images)

INPUT PHOTOS (data/)
--------------------
  Mosaics (A.1, A.4, A.5)   mosaic1_left.jpg, mosaic1_mid.jpg, mosaic1_right.jpg
                            mosaic2_left.jpg, mosaic2_mid.jpg, mosaic2_right.jpg
                            mosaic3_left.jpg, mosaic3_right.jpg
  Rectification (A.3)       rect1.jpg (monitor), rect2.jpg (laptop lid)

The file names and the rectangles' aspect ratios (width / height) are
set in the SETS and RECT dictionaries in the A.1 cell. The middle photo
of each set (index len // 2) is the reference that the others are warped
into; for a 2-photo set that is the second photo. Photos are downscaled
to 1200 px on the long side when loaded, so all pixel numbers in the
notebook refer to that size.

HOW TO RUN
----------
Run the cells top to bottom (or "Run All"). Later parts reuse functions
and variables from earlier parts, so after restarting the kernel always
start again from the first code cell (imports).

  A.1  loads and shows the photos
  A.2  click / load correspondences, build the system Ah = b, solve for H
  A.3  warpImageNearestNeighbor, warpImageBilinear, rectification
  A.4  feathered two-band blending into planar mosaics
  A.5  cylindrical mosaics (Bells & Whistles) and the focal-length sweep

Every result is also saved to out/ (the webpage reads its images from
there).

CLICKING POINTS
---------------
Two cells start with %matplotlib osx and open a separate window:

  A.2  For every non-reference photo, a window shows that photo on the
       LEFT and the reference on the RIGHT. Click 8 pairs, alternating:
       point 1 in the left image, the same point 1 in the right image,
       point 2 left, point 2 right, ... The window title says which side
       is next. Pick sharp corners that are visible in both photos and
       spread them over the whole overlap.
  A.3  For each rectification photo, click the 4 corners of the
       rectangle in the order top-left, top-right, bottom-right,
       bottom-left.

Clicks are saved to data/points/*.json once a window is finished, and
later runs reload them without opening a window. To redo a set, delete
its JSON file (e.g. data/points/mosaic3_0_to_1.json) or pass redo=True,
then re-run the cell. A misclick cannot be undone: interrupt the kernel
and re-run the cell. The open window's points are only saved once all of
them are clicked, so the bad click is thrown away; windows that were
already finished are kept.

If %matplotlib osx does not work (not on macOS, or a different editor),
install a Qt backend (pip install pyqt6) and change the two magics to
%matplotlib qt.

Quality checks printed by the notebook:
  - A.2 reprojection error: mean ~1-5 px is fine; a much larger value
    usually means one pair of points does not match.
  - A.5 ray misalignment: small (a few px) means the photos were taken
    by rotating in place; large values (like mosaic2, 12-15 px) mean the
    camera also moved, so the cylindrical mosaic will show ghosting.

NOTES
-----
- No cv2 / skimage homography or warping functions and no griddata are
  used. Homography fitting, inverse warping, nearest-neighbor and
  bilinear interpolation, blending and cylindrical projection are all
  written in NumPy. Only np.linalg (lstsq, inv, svd) and
  scipy.ndimage.gaussian_filter (for the blend's low-pass band) are
  library calls.
- The focal length for A.5 is read from each photo's EXIF
  (35 mm-equivalent focal length). Without EXIF it falls back to
  0.8 x the image width.
- The numbers on the webpage (errors, timings, H, focal lengths) come
  from the current notebook run. If you re-click points or change
  photos, re-run the notebook and update those numbers in index.html.
