CS180/CS280A Project 4B - Feature Matching for Autostitching
============================================================

All Part B code is in partB.ipynb (a Jupyter notebook). The project
webpage is index.html (with style.css and script.js); Part B is the
second half of the page.

REQUIREMENTS
------------
- Python 3.9+ (developed with Python 3.11)
- Packages listed in requirements.txt:
    numpy scipy matplotlib pillow ipykernel jupyter scikit-image
  (scikit-image is only needed by the provided harris.py)

SETUP
-----
Run these from this directory (projects/project4/). The virtual
environment (.venv) is not stored in git, so create it once per machine.

Windows (PowerShell):
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe -m ipykernel install --user --name proj4 --display-name "Python (project4)"

Then open partB.ipynb and pick the "Python (project4)" kernel.

FOLDER LAYOUT
-------------
    project4/
      partB.ipynb         all Part B code, results and notes (B.1 - B.5)
      harris.py           provided starter code (get_harris_corners, dist2)
      requirements.txt    Python dependencies
      index.html          project webpage (+ style.css, script.js)
      data/               input photos (same photos as Part A)
      data/points/        hand-clicked correspondences from Part A (JSON),
                          used only to compare manual vs automatic results
      out/                output images, written by the notebook

INPUT PHOTOS (data/)
--------------------
  mosaic1_left.jpg, mosaic1_mid.jpg, mosaic1_right.jpg
  mosaic2_left.jpg, mosaic2_mid.jpg, mosaic2_right.jpg
  mosaic3_left.jpg, mosaic3_right.jpg

The middle photo of each set (index len // 2) is the reference that the
others are warped into. Photos are downscaled to 1200 px on the long side
(MAX_SIDE), the same as Part A, so the clicked points in data/points/
still line up. B.5 makes its rotated test images from these photos, so
no extra photos are needed.

HOW TO RUN
----------
Run the cells top to bottom (or "Run All"). Later parts reuse functions
and variables from earlier parts, so after restarting the kernel always
start again from the first code cell (imports). No points need to be
clicked in Part B; everything is automatic.

  Setup  imports, the Part A helpers (homography, warping, blending,
         make_mosaic) and loading the photos
  B.1    Harris corners (harris.py) and Adaptive Non-Maximal Suppression
         (500 points, c_robust = 0.9)
  B.2    8x8 descriptors sampled every 5 px from a 40x40 window of the
         blurred image (sigma = 2), bias/gain normalized
  B.3    matching with Lowe's ratio test (1-NN / 2-NN < 0.5) plus a
         mutual nearest-neighbor check
  B.4    4-point RANSAC (5000 iterations, 3 px inlier threshold), refit
         on the inliers, automatic mosaics and manual vs automatic
         comparison
  B.5    Bells & Whistles: rotation-invariant descriptors (orientation
         from the blurred gradient, sigma_o = 4.5), a rotation sweep and
         a stitch with one photo rotated 30 degrees

Every figure is also saved to out/ (the webpage reads its images from
there). Main outputs:
  {set}_harris.jpg, {set}_anms.jpg        B.1
  {set}_descriptors.jpg                   B.2
  {set}_matches_{i}.jpg, ratio_hist.jpg   B.3
  {set}_inliers_{i}.jpg, {set}_auto.jpg,
  {set}_manual_vs_auto.jpg                B.4
  oriented_features.jpg, oriented_descriptors.jpg, rotation_sweep.jpg,
  rotated_matches_*.jpg, rotated_mosaic.jpg   B.5
