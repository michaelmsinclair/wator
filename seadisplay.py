#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 12:04:29 2017

@author: michael
"""

import numpy
import pygame

from sea import *

class SeaDisplay(object):
    """
    Display the sea of x by y cells.
    Each cell can hold one thing or be empty (None).
    """
    def __init__(self, x, y, filenumber=0):
        """
        Initialize screen
        """
        self.maxX = x
        self.maxY = y
        self.fileNumber = filenumber
        self.screen = self.initScreen(x,y)
        self.seaColor = 0x0000ff

    def initScreen(self, x, y):
        """
        Create a screen with dimensions x, y.
        Return the screen.
        Allows addition of new characteristics.
        """
        return pygame.display.set_mode((x,y))

    def setFileNumber(self, fileNumber):
        self.fileNumber = fileNumber

    def showImage(self, sea, save=False):
        """
        Show the sharks, fishes, empty sea as a red, green, or blue pixel, respectively.
        sea = array[x,y] of creatures.
        save = write to file if True (save as png).
        """
        
        screenArray = numpy.zeros((self.maxX,self.maxY))
        for y in range(self.maxY-1,-1,-1):
            for x in range(self.maxX):
                c = sea.getCell(x,y)
                pixelColor = self.seaColor
                if c is not None:
                    if c.isAlive(): # an empty cell 
                        pixelColor = c.getColor()
                screenArray[x][y] = pixelColor
        pygame.surfarray.blit_array(self.screen, screenArray)
        pygame.display.flip()
        if save:
            pygame.image.save(self.screen, ("images/wator_%06d.png" % self.fileNumber))
        self.fileNumber += 1

    def exportDisplay(self):
        return [self.fileNumber]
