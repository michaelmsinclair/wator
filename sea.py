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
        self.filenumber = 0
        self.creatures = {}
        self.creatureTag = 0
        self.maxX = x
        self.maxY = y
        self.sea = [[ None for Y in range(self.maxY)] for X in range(self.maxX)]
        self.screen = pygame.display.set_mode((x,y))
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

    def getSea(self):
        return self.sea

    def getSharks(self):
        return self.sharks

    def getFishes(self):
        return self.fishes

    def addCreature(self, x, y, newCreature, t, spawn, starve=99):
        """
        If creature can be added to sea, add it to the list of creatures
        """
        if self.isCellEmpty(x, y):
            pos = SeaPosition(x,y,self)
            creature = newCreature(self, pos, t, spawn, starve, self.random)
            self.setCell(x,y, creature)
            self.creatures[self.creatureTag] = creature
            self.creatureTag += 1
            if type(creature) is Shark:
                self.sharks += 1
            elif type(creature) is Fish:
                self.fishes += 1
            return True
        else:
            return False

    def getCreature(self, tag):
        return self.creatures[tag]

    def cleanCreatures(self):
        """
        Remove the dead creatures from the dictionary of self.creatures.
        """
        self.sharks = 0
        self.fishes = 0
        aliveCreatures = {}
        for c in self.creatures:
            if self.creatures[c].isAlive():
                aliveCreatures[c] = self.creatures[c]
                if type(self.creatures[c]) is Shark:
                    self.sharks += 1
                elif type(self.creatures[c]) is Fish:
                    self.fishes += 1

        self.creatures = aliveCreatures

    def display(self):
        """
        Show the sharks, fishes, empty sea as a red, green, or blue pixel, respectively.
        Save each screen as a png file.
        """
        screenArray = numpy.zeros((self.maxX,self.maxY))
        for y in range(self.maxY-1,-1,-1):
            for x in range(self.maxX):
                c = self.getCell(x,y)
                if type(c) is Shark:
                    screenArray[x][y] = 0xff0000
                elif type(c) is Fish:
                    screenArray[x][y] = 0x00ff00
                else:
                    screenArray[x][y] = 0x0000ff
        pygame.surfarray.blit_array(self.screen, screenArray)
        pygame.display.flip()
        pygame.image.save(self.screen, ("images/wator_%06d.png" % self.filenumber))
        self.filenumber += 1

    def exportSea(self):
        return (self.maxX,self.maxY,self.creatureTag,self.filenumber)

    def setFileNumber(self, filenumber):
        self.filenumber = filenumber

    def setCreatureTag(self, creatureTag):
        self.creatureTag = creatureTag
        
    def __str__(self):
        sharks = self.getSharks()
        fishes = self.getFishes()
        positions = self.maxX * self.maxY
        empty = positions - sharks - fishes
        return "Sharks: %d Fishes: %d Empty: %d" % (sharks, fishes, empty)
