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

#Stretching line to pass whole board
def stretchlines(line):
    k, b = lineeq([line[0],line[1]],[line[2],line[3]])
    x1 = 0
    y1 = k*x1 + b
    x2 = 1024   #TODO: replace with config for frame width
    y2 = k*x2 + b
    line1 = [[x1,y1],[x2,y2]]
    return line1



#Returning coordinates for where linse intersect or exception if not crossing each other
def intersect(self, line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    return x, y