__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
#Mock needed features in the mainloop for testing purposes. Features are added when needed

from DartScoreEngine.DartScoreEngineConfig import dartconfig

import Cam

class DummyMainLoop(object):
    def __init__(self, camurl = dartconfig["cam"]["camurl"]):
        self._cam = Cam.createCam("STREAM")
        self._cam.initialize(camurl)
        self._tmatrix = None


    def changeState(self, newstate):
        pass