# DartScore, bransch: DartScorePyhton3
Counting scores for dart with image recognition.
This bransch is forked from DartScoreEngine bransh and will be ported to Pyhton3 but also simplified a lot when it comes to modules and setups.

The project will run one or two fast networked cams as image stream sources, opencv for scorecount and PyGame for GUI. This could at least in theary be the same setup except from some file-pathes in all environments.

My environemnt is RaspberryPi 4 as the real thing' and Windos 10 for development.

The heart of the aplication is the 'dart-score-engine'. 
A simplified state-machine that can handle mounting, calibration and 'sets' of 3 darts.  
The engine can report the score for each hit but doesn't know anything of the number of players or what they are playing. The engine can also be 'reseted' to start all over again.

The engine can't be used by itself (but maybe a debug-mode) but is used from the game-logic that could be 
all the kinds of setups. 

**Engine**:

**Cameramountingstate**:

Streams the camera images to the GUI with an overlay indication where to have bulls-eye to manage calibration. One setup per cam...

**Calibratestate**:

Runs camera calibration for each cam and calculate all sectors on dartboard, saves this as a ??? (dictionary, bitmap, array)

**Playstate**:

Constantly overlooking board and reacts on changes when dart hits board. No other userinteraction is needed.

EngineMainLoop is engine and master for changing states and the engine 'event-loop'.

**Prerequisites:**
Python 3.x, PyGame and OpenCv 



