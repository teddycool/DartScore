__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore

# Purpose of this file:
# A set of common used fuctions and variables  to use when testing each module/part of the project

from cv2 import cv2
import sys
import platform

if platform.node() == 'DELL-laptop1':      
    #The development pc
    sys.path.append(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\SW')
    videofilepath = r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\Testdata\Videos\dartscore_20191120_174641.avi'
    recorderfilepath = r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\Testdata\Videos'
    camstreamurl = 'http://192.168.1.131:8081'
else:
    videofilepath = r'/home/pi/DartScore/Testdata/Videos/dartscore_20191107_152701.avi'


#Create a videocapture replacing the cam feed at test, 
def GetTestVideoCapture():        
        cap = cv2.VideoCapture(videofilepath)   
        if (cap.isOpened() == False): 
                print("Error opening video stream or file")
                return None
        else:
                return cap