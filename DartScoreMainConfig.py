__author__ = 'teddycool'
#Config vaues for the DartScore game. This is the only place for these.

dartconfig = {"cam": {"res": (800, 600), "id": 1, "framerate": 20},  # CAM settings
              "color": {"sector": (0, 255, 0), "hit": (255, 0, 0), "aim": (0, 255, 0), "calibrate": (0, 0, 255),
                        "bullseye": (0, 0, 255)},  # colors of sectors and markers
              "mounting": {"aimrectx": 80, "aimrecty": 40},  # values for mounting the cam and center bulls-eye
              "play": {"warmupframes": 5, "hitframes": 2},
              "Streamer": {"StreamerImage": "/tmp/stream/pic.jpg", "StreamerLib": "/tmp/stream",
                           "VideoFile": "/home/pi/DartScore/video.avi"},
              "Button": {"Pressed": 0.1, "LongPressed": 1.5},
              "LedIndicator":{"ActivationTime":1},
              "Logger": {"Level": "Verbose", "LogFile": "/tmp/stream/log.log", "SaveDartEvalFrames": False},
              "IO": {"CalButton": 23, "GameButton": 24, "OnLed": 25, "CalLed": 8, "GameLed":7, "HitLed":18, "GameSwitch1":9, "GameSwitch2":10},
              "Main": {"MaxFrameRate": 10},
              "Vision": {"WriteFramesToSeparateFiles": False, "PrintFrameRate": True, "RecordRaw": False, "RecordCv": False, "CamType": "PI"},
              "DartHit": {"WriteFramesToSeparateFiles": False, "DartHitMinArea": 500},
              "Recorder": {"VideoFileDir": "/home/pi/DartScore/Videos/", "VideoFile":"/home/pi/DartScore/video.avi", "tempfile": "/ram/videos/", "MinSize": 70000, "MaxFrames": 600},
              }