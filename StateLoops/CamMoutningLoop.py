_author__ = 'teddycool'
#State handling mounting of cam showing a square in the videofeed  where to have bulls-eye



from  StateLoop import StateLoop
import DartScoreConfig
import cv2

class CamMountingLoop(StateLoop):
    def __init__(self):
        super(CamMountingLoop, self).__init__()
        return

    def initialize(self):
        width, height= DartScoreConfig.dartconfig['cam']['res']
        aimx = DartScoreConfig.dartconfig['mounting']['aimrectx']
        aimy = DartScoreConfig.dartconfig['mounting']['aimrecty']

        self._startpos= (width/2-aimx/2,height/2-aimy/2)
        self._centerRect = (self._startpos[0]+aimx, self._startpos[1]+aimy)
        self._center = (width/2,height/2)

        return

    def update(self, frame):
        #TODO: Add logic to switch state when ready Ie a button on the cam
        return frame

    def draw(self, frame):
        cv2.rectangle(frame, self._startpos, self._centerRect, DartScoreConfig.dartconfig['color']['aim'], 5)
        cv2.circle(frame,self._center,10, DartScoreConfig.dartconfig['color']['bullseye'],2)
        return frame