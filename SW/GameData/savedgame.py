__author__ = 'teddycool'
# This file is part of the DartScore project created by Pär Sundbäck
# More at https://github.com/teddycool/DartScore
#
# Purpose of this file:
# Example structure of save game dictionary saved and loaded with pickle

import numpy as np
import pickle
import time

savedgame = {
            "time": time.time(),
            "gametype": "301",
            "player1": {"d1": "-", "d2": "-", "d3": "-", "set": "-" , "total": "-", "diff": "-", "done": False},  #Current struct with scores for this player
            "player2": {},
}




if __name__ == "__main__":

    sg = savedgame
    print(sg)
    pf = open(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\SW\GameData\sg.pic', "wb")
    pickle.dump(sg, pf)
    pf.close()
    time.sleep(2)
    pf = open(r'C:\Users\par\OneDrive\Documents\GitHub\DartScore\SW\GameData\sg.pic', "rb")
    sg1 = pickle.load(pf)
    print (sg1)