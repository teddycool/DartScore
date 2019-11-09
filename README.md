# DartScore, bransch: DartScorePython3
Counting scores for dart with image recognition.
This bransch is forked from DartScoreEngine bransh and will be ported to Python3 but also simplified a lot when it comes to modules and setups.

The project will run one or two fast networked cams as image stream sources, opencv for score-count and PyGame for GUI. This could at least in theory be the same setup except from some file-pathes in all environments.

My environment is RaspberryPi 4 as the real thing' and Windos 10 for development.

The heart of the aplication is the 'dart-score-engine'. 
This is a simplified state-machine that can handle mounting, calibration and 'sets' of 3 darts.  
The engine can report the score for each hit but doesn't know anything of the number of players or what they are playing. The engine can also be 'reseted' to start all over again.

The engine can't be used by itself (maybe in debug-mode) but is used from the game-logic that could be all the kinds of setups. 

**Engine**:

**Cameramountingstate**:

Streams the camera images to the GUI with an overlay indication ofwhere to have bulls-eye to manage calibration. One setup per cam...

**Calibratestate**:

Runs camera calibration for each cam and calculate all sectors on dartboard, saves this as a ??? (dictionary, bitmap, array)

**Playstate**:

Constantly overlooking board and reacts on changes when dart hits board. No other user-interaction is needed.

EngineMainLoop is engine and master for changing states and the engine 'event-loop'.

**Prerequisites:**
Python 3.x, PyGame and OpenCv 


Raspberry pi 4 2GB, Rasbian Buster full (includes Python3  and Python-game)

Install open cv and dependencies...

pip3 install opencv-python
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo apt-get install libqtgui4
sudo apt-get install python3-pyqt5
sudo apt install libqt4-test
