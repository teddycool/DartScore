# DartScore, bransch: DartScorePiCam
Counting scores for dart with image recognition
Raspberry pi cam in a case with a couple of push-buttons connected to the PI-io

Tactics:
BoardArray with 'perfect' dartboard
Board with a skewed image of the actual dartboard, from upper perspective.
Make transform matrix to calculate perspective of image to fit BoardArray
Find where the transformed board-picture is covered when image change
Calculate score for covered region....

All logic in raspberrypi
Images sent to jpg-streamer to be picked up by any webbrowser

Prereqs:
A working raspberrypi with cam

Cameramountingstate:
Streams the camera images to the jpg-streamer with an overlay indication where to have bulls-eye to manage calibration

Calibratestate:
Runs camera calibration and calculate all sectors on dartboard, saves this as a ??? (dictionary, bitmap, array)

Playstate:
Constantly overlooking board and reacts on changes when dart hits board. No other userinteraction is needed.

MainLoop is engine and master for changing states
Inputs from push-buttons decides when player is done with mounting etc and ready to play
