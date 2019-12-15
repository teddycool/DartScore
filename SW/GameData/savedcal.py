__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
# Example structure of a calibration dictionary saved and loaded with pickle
import numpy as np
import pickle
import time

calibration = {
    "time": time.now,
    "bullseye": (512, 237),
    "transform": np.float32( [[1.78852294e+00, -1.10143263e-01, -4.85063747e+02],
                             [2.17855239e-01, 1.03682933e+00, -3.82665632e+01],
                             [1.28478485e-03, -1.58506840e-04, 1.00000000e+00]])
}