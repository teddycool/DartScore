# DartScore, bransch: DartScoreEngine
Counting scores for dart with image recognition.
This bransch is dived into modules:
DartScoreEngine
PiSetup
WindowwsSetup
...and some gamelogic using these...


A 'dart-score-engine' that can be used from different types of environment. 
A simplified state-machine that can handle mounting, calibration and 'sets' of 3 darts.  
The engine can report the score for each hit but doesn't know anything of the number of players or what they are playing. The engine can also be 'reseted' to start all over again.

The engine can't be used by itself (but maybe a debug-mode) but is used from a game-logic that could be 
all the kinds of programs. The interaction between the 'engine' and the gamelogic should be solved in some general way since the 'engine' should be unaware of the logic that uses it.

Engine:

Cameramountingstate:
Streams the camera images to the jpg-streamer with an overlay indication where to have bulls-eye to manage calibration

Calibratestate:
Runs camera calibration and calculate all sectors on dartboard, saves this as a ??? (dictionary, bitmap, array)

Playstate:
Constantly overlooking board and reacts on changes when dart hits board. No other userinteraction is needed.

EngineMainLoop is engine and master for changing states


