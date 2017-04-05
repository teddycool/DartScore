__author__ = 'teddycool'
import math
 #Calculate y=kx+b from two coordinates defining a line
def lineeq (coord1, coord2):
    k= (coord2[1]-coord1[1])/ (coord2[0]-coord1[0])
    b= coord1[1]  - k*coord1[0]
    return k, b

#defining angle for line passing through origo and 'coord'
def angle(coord):
    return math.atan(coord[1]/coord[0])

#defining lenght from origo to 'coord'
def lenght(coord):
    return math.sqrt(math.pow(coord[0], 2) + math.pow(coord[1],2))
