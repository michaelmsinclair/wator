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
    def __init__(self, sea, filenumber=0):
        """
        Initialize screen
        """
        self.sea = sea
        self.maxX = sea.getMaxX()
        self.maxY = sea.getMaxY()
        self.fileNumber = filenumber
        self.cellsize = 5
        self.screen = self.initScreen()
        pygame.display.set_caption("Wa-Tor")

        self.seaColor = 0x0000ff

    def initScreen(self):
        """
        Create a screen with dimensions x, y.
        Return the screen.
        Allows addition of new characteristics.
        """
        return pygame.display.set_mode((self.maxX*self.cellsize, self.maxY*self.cellsize))

    def setMaxX(self, x):
        self.maxX = x

    def setMaxY(self, y):
        self.maxY = y

    def setFileNumber(self, fileNumber):
        self.fileNumber = fileNumber

    def showImage(self, sea, save=False):
        """
        Show the sharks, fishes, empty sea as a red, green, or blue pixel, respectively.
        sea = array[x,y] of creatures.
        save = write to file if True (save as png).
        """
        result = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                result = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass

        if self.maxX != sea.getMaxX() or self.maxY != sea.getMaxY():
            self.setMaxX(sea.getMaxX())
            self.setMaxY(sea.getMaxY())
            self.screen = self.initScreen()
            
        screenArray = numpy.zeros((self.maxX,self.maxY))
        for y in range(self.maxY-1,-1,-1):
            for x in range(self.maxX):
                c = sea.getCell(x,y)
                pixelColor = self.seaColor
                if c is not None:
                    if c.isAlive(): # an empty cell 
                        pixelColor = c.getColor()
                screenArray[x][y] = pixelColor
                pygame.draw.rect(self.screen, pixelColor, 
                    [self.cellsize * x, 
                    self.cellsize * y, 
                    self.cellsize, self.cellsize])
#        pygame.surfarray.blit_array(self.screen, screenArray)
        pygame.display.flip()
        if save:
            pygame.image.save(self.screen, ("images/wator_%06d.png" % self.fileNumber))
        self.fileNumber += 1
        
        return result
    
    def Quit(self):
        pygame.quit()

    def exportDisplay(self):
        return [self.fileNumber]
