#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 17:06:04 2017

@author: michael

The sea that is the planet Wa-Tor.
Laid out with finite cartesian coordinates that wrap around, it is a torus.
If a creature moves beyond maxX, or maxY it returns to the origin.

All X: {0, 1, ..., maxX}
All Y: {0, 1, ..., maxY}
"""

import numpy
import pygame

from seacreature import *
from seaposition import *

class Sea(object):
    """
    A sea of x by y cells.
    A cell can hold one thing or be empty (None).
    """
    def __init__(self, x, y, random):
        """
        Initialize an empty sea.
        """
        self.creatures = []
        self.maxX = x
        self.maxY = y
        self.sea = [[ None for Y in range(self.maxY)] for X in range(self.maxX)]
        self.sharks = 0
        self.fishes = 0
        self.random = random

    def getMaxX(self):
        return self.maxX

    def getMaxY(self):
        return self.maxY

    def isCellEmpty(self, x, y):
        """
        If cell is None type, or contains a dead creature it is empty,
        otherwise it is not.
        """
        try:
            if self.sea[x][y] == None:
                return True
            elif self.sea[x][y].isAlive():
                return False
            else:
                return True
        except IndexError:
            return False

    def setCell(self, x, y, c):
        """
        Put creature c in cell (x,y) of the sea, if the cell is empty
        Return True if possible and false if not.
        """
        result = False
        try:
            if self.isCellEmpty(x,y):
                self.sea[x][y] = c
                result = True
        except IndexError:
            pass
        return result

    def getCell(self, x, y):
        try:
            return self.sea[x][y]
        except IndexError:
            return None

    def emptyCell(self, x, y):
        if type(self.sea[x][y]) is Shark:
            self.sharks -= 1
        elif type(self.sea[x][y]) is Fish:
            self.fishes -= 1

        self.sea[x][y] = None

    def getSharks(self):
        return self.sharks

    def getFishes(self):
        return self.fishes

    def addCreature(self, x, y, newCreature, t, spawn, parent, starve=99):
        """
        If creature can be added to sea, add it to the list of creatures
        Return the creature if added, None otherwise
        """
        if self.isCellEmpty(x, y):
            pos = SeaPosition(x,y,self)
            creature = newCreature(self, pos, t, spawn, starve, self.random, parent)
            self.setCell(x,y, creature)
            self.creatures.append(creature)
            if type(creature) is Shark:
                self.sharks += 1
            elif type(creature) is Fish:
                self.fishes += 1
            return creature
        else:
            return None

    def cleanCreatures(self):
        """
        Remove the dead creatures from the dictionary of self.creatures.
        """
        self.sharks = 0
        self.fishes = 0
        aliveCreatures = []
        for c in self.creatures:
            if c.isAlive():
                aliveCreatures.append(c)
                if type(c) is Shark:
                    self.sharks += 1
                elif type(c) is Fish:
                    self.fishes += 1

        self.creatures = aliveCreatures

    def exportSea(self):
        return [self.maxX,self.maxY]

    def setCreatureTag(self, creatureTag):
        self.creatureTag = creatureTag
        
    def __str__(self):
        sharks = self.getSharks()
        fishes = self.getFishes()
        positions = self.maxX * self.maxY
        empty = positions - sharks - fishes
        return "Sharks: %d Fishes: %d Fishes per Shark: %d Empty: %d" % (sharks, fishes, round(fishes/sharks), empty)
