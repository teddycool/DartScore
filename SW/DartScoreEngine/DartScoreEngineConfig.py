__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
#Config values for DartScoreEngine. This is the only place for these.


dartconfig = {"cam": {"res": (1024, 768), "camurl": "http://192.168.1.131:8081" },  # CAM settings, NO support for other res then (1024, 768)!

                "color": {"sector": (0, 255, 0),
                        "hit": (255, 0, 0),
                        "aim": (0, 255, 0),
                        "calibrate": (0, 0, 255),
                        "bullseye": (0, 0, 255)},  # colors of sectors and markers
                "mounting": {"aimrectx": 200, "aimrecty": 200},  # values for mounting the cam and center bulls-eye
                "DartHit": {"WriteFramesToSeparateFiles": False, "DartHitMinArea": 500, "DartHitMaxArea": 1300, "DartHitFrames": 0},
                "calibration": {"savepath": r"/home/pi/DartScore/SW/GameData/calt.pic"},

              #TODO: fix filepathes for rpi and switch automatically

              "play": {"warmupframes": 5, "hitframes": 3},
              "Button": {"Pressed": 0.1, "LongPressed": 1.5},

              #Not used in MVP1...
              "LedIndicator":{"ActivationTime":1},
              "Logger": {"Level": "Verbose", "LogFile": "/tmp/stream/log.log", "SaveDartEvalFrames": False},
              "IO": {"CalButton": 23, "GameButton": 24, "OnLed": 25, "CalLed": 8, "GameLed":7, "HitLed":18, "GameSwitch1":9, "GameSwitch2":10},
              "Main": {"MaxFrameRate": 10},
              "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": False, "RecordRaw": False, "RecordCv": False, "CamType": "NetCam"},

              "Recorder": {"VideoFileDir": "/home/pi/DartScore/Videos/", "VideoFile":"/home/pi/DartScore/video.avi", "tempfile": "/ram/videos/", "MinSize": 70000, "MaxFrames": 600},
              }