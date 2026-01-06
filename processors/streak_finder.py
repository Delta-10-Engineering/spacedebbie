import numpy as np
import sep
from skimage.transform import probabilistic_hough_line
from skimage.feature import canny
from astropy.io import fits

def find_debris_streaks(fits_file):
    with fits.open(fits_file) as hdul:
        data = hdul[0].data.astype(float)
        if data.ndim > 2:
            data = data[0]
        header = hdul[0].header

    data = data.copy(order='C')
    try:
        bkg = sep.Background(data)
        data_sub = data - bkg
    except Exception as e:
        data_sub = data - np.median(data)

    norm_data = (data_sub - np.min(data_sub)) / (np.max(data_sub) - np.min(data_sub))
    edges = canny(norm_data, sigma=2, low_threshold=0.1, high_threshold=0.8)

    lines = probabilistic_hough_line(edges, threshold=10, line_length=20, line_gap=5)

    return lines, data_sub, header
