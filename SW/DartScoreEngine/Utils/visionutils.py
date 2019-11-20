
import numpy as np
from cv2 import cv2


def auto_canny(image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)

        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edgedimage = cv2.Canny(image, lower, upper)

        #return the edged image
        return edgedimage
