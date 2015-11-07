# DartScore
Counting scores for dart with image recognition
Raspberry pi cam...

Tactics:
BoardArray with 'perfect' dartboard
Board with a skewed image of the actual dartboard, from upper perspective.
Make transform matrix to calculate perspective of image to fit BoardArray
Find where the transformed board-picture is covered when image change
Calculate score for covered region....