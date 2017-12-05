#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 17:06:04 2017

@author: michael
"""

class SeaPosition(object):
    """
    Cartesian position (x,y) within the sea.
    """
    def __init__(self, x, y, sea):
        """
        Initialize position with given coordinates
        """
        self.x = x
        self.y = y
        self.sea = sea

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getSeaPosition(self):
        return(self.x, self.y)

    def getAdjacent(self, traditional):
        """
        Returns two arrays of tuples for the positions adjacent to the position.
        The first contains location tuples for empty cells, while the second
        contains cells with a creature in it.
        The cells can either be those in the n, e, s, w postion, or all eight
        surrounding cells - n, ne, e, se, s, sw, w, ne.
        traditional:
                    (0,+1)
            (-1, 0)  Pos.  (+1, 0)
                    (0,-1)
        new:
            (-1,+1) (0,+1) (+1,+1)
            (-1, 0)  Pos.  (+1, 0)
            (-1,-1) (0,-1) (+1,-1)
        """
        empty = []
        occupied = []
        search = []
        if traditional:
            search = [(0,+1),(-1, 0),(+1, 0),(0,-1)]
        else:
            search = [(-1,+1),(0,+1),(+1,+1),(-1, 0),(+1, 0),(-1,-1),(0,-1),(+1,-1)]
        for s in search:
            deltaX, deltaY = s[0], s[1]
            newX = (self.x + deltaX + self.sea.getMaxX()) % self.sea.getMaxX()
            newY = (self.y + deltaY + self.sea.getMaxY()) % self.sea.getMaxY()
            if self.sea.isCellEmpty(newX,newY):
                empty.append((newX, newY))
            else:
                occupied.append((newX, newY))
        return(empty,occupied)

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)

