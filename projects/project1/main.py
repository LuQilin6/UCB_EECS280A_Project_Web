# CS180 (CS280A): Project 1 

import os
import glob
import csv

import numpy as np
import skimage as sk
import skimage.io as skio

# Config

DATA_DIR = 'CS180_fa2026_proj1_data'
OUT_DIR = 'out'
DISPLACEMENT_RANGE = 15  # exhaustive single-scale search window: [-15, 15]


# I/O helpers (implemented)
def list_data_images(data_dir=DATA_DIR):
    """Return a sorted list of paths to the .jpg/.tif glass-plate scans
    directly inside data_dir"""
    paths = []
    for ext in ('*.jpg', '*.jpeg', '*.tif', '*.tiff'):
        paths.extend(glob.glob(os.path.join(data_dir, ext)))
    return sorted(paths)


def load_image(path):
    im = skio.imread(path)
    im = sk.img_as_float(im)
    return im


def split_channels(im):
    height = im.shape[0] // 3
    b = im[:height]
    g = im[height: 2 * height]
    r = im[2 * height: 3 * height]
    return b, g, r


# Metrics 

def score_l2(im1, im2):
    return np.sqrt(np.sum((im1 - im2) ** 2))



def score_ncc(im1, im2):
    im1_flat= im1.ravel()
    im2_flat= im2.ravel()
    ncc = np.dot((im1_flat - np.mean(im1_flat)) / np.linalg.norm(im1_flat - np.mean(im1_flat)),
                    (im2_flat - np.mean(im2_flat)) / np.linalg.norm(im2_flat - np.mean(im2_flat)))
    return ncc


# Alignment 

def align_single_scale(im1, im2, window=DISPLACEMENT_RANGE, metric=score_ncc, border=None):
    """Exhaustively search x,y displacements of im1 relative to im2 over
    [-window, window] in both dimensions
    """
    if border is None:
        border = window
    # keep border sane relative to image size so cropping never empties it
    max_border = min(im1.shape[0], im1.shape[1], im2.shape[0], im2.shape[1]) // 2 - 1
    border = max(0, min(border, max_border))

    best_score = -np.inf
    best_shift = (0, 0)
    im2_c = im2[border:-border, border:-border] if border > 0 else im2  # crop once
    im2_c_zm = im2_c - im2_c.mean() #make a constant brightness offset between channels
    for dx in range(-window, window + 1):
        for dy in range(-window, window + 1):
            im1_shifted = np.roll(im1, shift=(dy, dx), axis=(0, 1))
            im1_c = im1_shifted[border:-border, border:-border] if border > 0 else im1_shifted
            im1_c_zm = im1_c - im1_c.mean()
            if metric == score_l2:
                score = -metric(im1_c_zm, im2_c_zm)
            else:
                score = metric(im1_c_zm, im2_c_zm)
            if score > best_score:
                best_score = score
                best_shift = (dx, dy)

    return best_shift


def align_pyramid(im1, im2, metric=score_ncc, min_size=100, window=DISPLACEMENT_RANGE):
    """
    Build an image pyramid (successive 2x downsampling) for im1 and im2,
    align at the coarsest level, then refine the estimate while moving
    down to full resolution. 
    """
    max_length = max(im1.shape[0], im1.shape[1], im2.shape[0], im2.shape[1])
    if max_length <= min_size:
        return align_single_scale(im1, im2, window=window, metric=metric)
    downsampled_im1 = sk.transform.rescale(im1, 0.5, anti_aliasing=True)
    downsampled_im2 = sk.transform.rescale(im2, 0.5, anti_aliasing=True)
    coarse_dx, coarse_dy = align_pyramid(downsampled_im1, downsampled_im2, metric=metric, min_size=min_size, window=window)
    coarse_dx *= 2
    coarse_dy *= 2
    im1_shifted = np.roll(im1, shift=(coarse_dy, coarse_dx), axis=(0, 1))
    # small local search, but a border crop scaled to THIS level's size so
    # the photo's own border doesn't bias the refinement
    refine_border = max(2, int(min(im1.shape[0], im1.shape[1]) * 0.05))
    refined_dx, refined_dy = align_single_scale(
        im1_shifted, im2, window=2, metric=metric, border=refine_border)
    return coarse_dx + refined_dx, coarse_dy + refined_dy


def align_by_features(im1, im2, window=DISPLACEMENT_RANGE, metric=score_ncc, border=None):
    """align on GRADIENT/EDGE maps instead of raw pixel
    intensities.
    """
    edges1 = sobel_magnitude(im1)
    edges2 = sobel_magnitude(im2)
    return align_pyramid(edges1, edges2, window=window, metric=metric)


def sobel_magnitude(im):
    
    padded = np.pad(im, 1, mode='edge')

    # the 8 neighbors (+ center, unused by Sobel) of every pixel, as views
    tl, tc, tr = padded[:-2, :-2], padded[:-2, 1:-1], padded[:-2, 2:]
    ml,     mr = padded[1:-1, :-2],                   padded[1:-1, 2:]
    bl, bc, br = padded[2:, :-2],  padded[2:, 1:-1],  padded[2:, 2:]

    gx = (tr + 2 * mr + br) - (tl + 2 * ml + bl)
    gy = (bl + 2 * bc + br) - (tl + 2 * tc + tr)
    """
        Gx = [-1 0 1]      Gy = [-1 -2 -1]
            [-2 0 2]           [ 0  0  0]
            [-1 0 1]           [ 1  2  1]
    """

    return np.sqrt(gx ** 2 + gy ** 2)



def align(im1, im2, metric=score_ncc):
    # Dispatch to different align methods

    # method = 'singlescale'
    # shift = align_single_scale(im1, im2, metric=metric)

    # method = 'pyramid'
    # shift = align_pyramid(im1, im2, metric=metric)

    method = 'features'
    shift = align_by_features(im1, im2, metric=metric)

    return shift, method



def auto_crop(im, max_crop_frac=0.08, threshold_ratio=1.5):
    h, w = im.shape[:2]
    disagreement = im.max(axis=2) - im.min(axis=2)

    max_h = max(1, int(h * max_crop_frac))
    max_w = max(1, int(w * max_crop_frac))

    interior = disagreement[max_h:h - max_h, max_w:w - max_w]
    baseline = np.median(interior) if interior.size else np.median(disagreement)
    threshold = baseline * threshold_ratio

    row_profile = disagreement.mean(axis=1)  # one value per row -> (h,)
    col_profile = disagreement.mean(axis=0)  # one value per column -> (w,)

    top = _detect_border_width(row_profile[:max_h], threshold, from_start=True)
    bottom = _detect_border_width(row_profile[-max_h:], threshold, from_start=False)
    left = _detect_border_width(col_profile[:max_w], threshold, from_start=True)
    right = _detect_border_width(col_profile[-max_w:], threshold, from_start=False)

    # don't crop away the whole image on a side
    if top + bottom >= h:
        top = bottom = 0
    if left + right >= w:
        left = right = 0

    cropped = im[top:h - bottom, left:w - right]
    return cropped, (top, bottom, left, right)


def _detect_border_width(profile, threshold, from_start):
    seq = profile if from_start else profile[::-1]
    above = np.where(seq > threshold)[0]
    if above.size == 0:
        return 0
    return int(above[-1]) + 1


def auto_contrast(im):
    min_val = np.min(im)
    max_val = np.max(im)
    contrasted = (im - min_val) / (max_val - min_val)
    return contrasted


def auto_white_balance(im, method='gray_world'):
    eps = 1e-8  # avoid divide-by-zero if a channel's illuminant estimate is 0

    if method == 'gray_world':
        illuminant = im.mean(axis=(0, 1))
        gain = illuminant.mean() / (illuminant + eps)
    elif method == 'white_patch':
        illuminant = im.max(axis=(0, 1))
        # scale each channel so its brightest pixel becomes exactly 1
        gain = 1.0 / (illuminant + eps)
    else:
        raise ValueError(f'unknown method: {method!r}')

    balanced = im * gain
    return balanced


def color_map(im, matrix=None):
    #apply a full 3x3 linear mixing matrix to try to recover more realistic colors
    
    shape = im.shape
    pixels = im.reshape(-1, 3)  # one row per pixel: (N, 3)
    matrix = np.asarray(matrix)
    mapped = pixels @ matrix.T

    return mapped.reshape(shape)



def colorize(im, metric=score_ncc):
    """Given a stacked B/G/R glass-plate image, split it into channels,
    align G and R onto B, and combine into a color image.
    """
    b, g, r = split_channels(im)

    (dx_g, dy_g), method = align(g, b, metric=metric)
    (dx_r, dy_r), _ = align(r, b, metric=metric)

    # apply shift_g/shift_r (e.g. via np.roll) before stacking
    ag = np.roll(g, shift=(dy_g, dx_g), axis=(0, 1))
    ar = np.roll(r, shift=(dy_r, dx_r), axis=(0, 1))

    im_out = np.dstack([ar, ag, b])
    return im_out, (dx_g, dy_g), (dx_r, dy_r), method



def log_result(log_path, row):
    fieldnames = ['image', 'g_dx', 'g_dy', 'r_dx', 'r_dy']
    is_new = not os.path.exists(log_path)
    with open(log_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def process_image(path, out_dir=OUT_DIR, metric=score_ncc):
    """Load one glass-plate image, colorize it, print the displacement
    vectors, and save the result. Reports (rather than crashes on)
    NotImplementedError so the batch can run before alignment is written."""
    name = os.path.splitext(os.path.basename(path))[0]
    source_folder = os.path.basename(os.path.dirname(path)) or path
    print(f'--- {name} ---')
    M = np.array([
        [1.1,  0.0,  0.0],   #R_out = 1.1 * R_in
        [0.0,  1.2,  0.0],   #G_out = 1.2 * G_in
        [0.0,  0.0,  1.2],  #B_out = 1.2 * B_in
    ])
    try:
        im = load_image(path)
        im_out, shift_g, shift_r, method = colorize(im, metric=metric)
        #the following steps are extra techniques to improve the visual quality of the output
        im_out, crop_box = auto_crop(im_out)
        im_out = auto_contrast(im_out)
        im_out = auto_white_balance(im_out, method='gray_world')
        im_out = color_map(im_out, matrix=M)
    except NotImplementedError:
        print('  skipped (alignment not implemented yet)')
        return

    print(f'  g shift: {shift_g}')
    print(f'  r shift: {shift_r}')
    # print(f'  crop box (top,bottom,left,right): {crop_box}')

    metric_name = metric.__name__.replace('score_', '')
    output_folder = f'{method}_{metric_name}_4'
    save_dir = os.path.join(out_dir, output_folder)
    os.makedirs(save_dir, exist_ok=True)
    out_path = os.path.join(save_dir, f'{name}.jpg')
    skio.imsave(out_path, sk.img_as_ubyte(np.clip(im_out, 0, 1)))
    print(f'  saved -> {out_path}')

    log_result(os.path.join(save_dir, 'results.csv'), {
        'image': name,
        'g_dx': shift_g[0], 'g_dy': shift_g[1],
        'r_dx': shift_r[0], 'r_dy': shift_r[1],
    })


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # process all images in the data folder (or subfolders) and save results to OUT_DIR
    for path in list_data_images():
        process_image(path, metric=score_ncc)

    # process the three self-chosen images and save results to OUT_DIR
    # for i in range(1,4):
    #     process_image(f'CS180_fa2026_proj1_data/SelfChoosePic/selfchoose{i}.jpg', metric=score_l2)
    #     process_image(f'CS180_fa2026_proj1_data/SelfChoosePic/selfchoose{i}.jpg', metric=score_ncc)
    



if __name__ == '__main__':
    main()
