__author__ = 'psk'
from opencv import adaptors
from pygame import surfarray

def surf2CV(surf):
    """Given a surface, convert to an opencv format (cvMat)
    """
    numpyImage = surfarray.pixels3d(surf)
    cvImage = adaptors.NumPy2Ipl(numpyImage.transpose(1,0,2))
    return cvImage

def cv2SurfArray(cvMat):
    """Given an open cvMat convert it to a pygame surface pixelArray
    Should be able to call blit_array directly on this.
    """
    numpyImage = adaptors.Ipl2NumPy(cvMat)
    return numpyImage.transpose(1,0,2)

http://stackoverflow.com/questions/8584674/opencv-2-0-where-is-adaptors-py

import Image
import cv
pi = Image.open('foo.png')       # PIL image
cv_im = cv.CreateImageHeader(pi.size, cv.IPL_DEPTH_8U, 1)
cv.SetData(cv_im, pi.tostring())

OpenCV to PIL Image:

cv_im = cv.CreateImage((320,200), cv.IPL_DEPTH_8U, 1)
pi = Image.fromstring("L", cv.GetSize(cv_im), cv_im.tostring())

       cvimg=pygame.surfarray.pixels3d(snapshot)
        cvImage = cvimg
        cv2.transpose(cvimg,cvImage)
        gray = cv2.cvtColor(cvImage, cv2.COLOR_BGR2GRAY)

import PIL
PIL.pil
