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

import argparse
import numpy
import pygame
import random 
random = random.SystemRandom()
import sys
import time

class SeaPosition(object):
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
    
    def getAdjacent(self):
        """
        Returns an array of tuples for the positions adjacent to the current position. 
        Includes diagonal positions, that is the eight surrounding Pos. below:
            (-1,+1) (0,+1) (+1,+1)
            (-1, 0)  Pos.  (+1, 0)
            (-1,-1) (0,-1) (+1,-1)
        """
        empty = []
        occupied = []
        for deltaX in (-1, 0, 1):
            for deltaY in (-1, 0, 1):
                if not (deltaX == 0 and deltaY == 0):
                    newX = (self.x + deltaX + self.sea.getMaxX()) % self.sea.getMaxX()
                    newY = (self.y + deltaY + self.sea.getMaxY()) % self.sea.getMaxY()
                    if self.sea.isCellEmpty(newX,newY):
                        empty.append((newX, newY))
                    else:
                        occupied.append((newX, newY))
        return(empty,occupied)
    
    
    
    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)

class Sea(object):
    '''
    A sea of x by y cells.
    A cell can hold one thing or be empty (None).
    '''
    def __init__(self, x, y):
        '''
        Initialize and empty sea.
        '''
        self.filenumber = 0
        self.creatures = {}
        self.creatureTag = 0
        self.maxX = x
        self.maxY = y
        self.sea = [[ None for Y in range(self.maxY)] for X in range(self.maxX)]
        self.screen = pygame.display.set_mode((x,y))
        self.sharks = 0
        self.fishes = 0

    def getMaxX(self):
        return self.maxX
        
    def getMaxY(self):
        return self.maxY
        
    def isCellEmpty(self, x, y):
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
        '''
        Put creature c in cell (x,y) of the sea, if the cell is empty
        Return True if possible and false if not.
        '''
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
        
    def addCreature(self, x, y, newCreature):
        '''
        If creature can be added to sea, add it to the list of creatures
        '''
        if self.isCellEmpty(x, y):
            pos = SeaPosition(x,y,self)
            creature = newCreature(self, pos)
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
        
    def __str__(self):
        sharks = self.getSharks()
        fishes = self.getFishes()
        positions = self.maxX * self.maxY 
        empty = positions - sharks - fishes
        return "maxX: %d maxY: %d Positions: %d Sharks: %d Fishes: %d Empty: %d" % (self.maxX, self.maxY, positions, sharks, fishes, empty)
                    

class Creature(object):
    def __init__(self, sea, pos, spawnAge=2):
        '''
        Simple creature, reproduces quickly, does not eat, and never dies except if eaten.
        '''
        self.sea = sea
        self.pos = pos
        self.age = 0
        self.spawnAge = spawnAge
        self.alive = True
    
    def getPosition(self):
        return self.pos
    
    def setPosition(self, pos):
        self.pos = pos
        
    def isAlive(self):
        return self.alive

    def died(self):
        '''
        remove from sea, and set dead
        '''
        x,y = self.pos.getSeaPosition()
        self.sea.emptyCell(x,y)
        self.alive = False
        
    def spawn(self,free):
        if self.age >= self.spawnAge:
            spawnX, spawnY = random.choice(free)
            self.sea.addCreature(spawnX, spawnY, type(self))
            self.age = 0
            return True
        else:
            return False
    
    def move(self,empty):
        '''
        move to an empty space.
        '''
        newX, newY = random.choice(empty)
        oldX, oldY = self.pos.getSeaPosition()
        if self.sea.setCell(newX, newY, self):
            self.sea.emptyCell(oldX, oldY)
            self.pos = SeaPosition(newX, newY, self.sea)
            
        
    def turn(self):
        if self.alive:
            self.age += 1
            empty, occupied = self.pos.getAdjacent()
            if len(empty) > 0:
                if not self.spawn(empty):
                    self.move(empty)
    
    def __str__(self):
        return "%s" % str(self.pos)
    
class Shark(Creature):
    def __init__(self, sea, pos, spawnAge=5, starveAge=3):
        Creature.__init__(self, sea, pos, spawnAge)
        self.starveAge = starveAge
        self.starve = 0
        
    def eat(self,occupied):
        '''
        Either find something to eat, or move (randomly) to a free adjacent spot.
        '''
        fishes = []
        for cell in occupied:
            x,y = cell[0],cell[1]
            if type(self.sea.getCell(x,y)) is Fish:
                fishes.append(cell)
        if len(fishes) > 0:
            newX, newY = random.choice(fishes)
            self.sea.getCell(newX,newY).died()
            self.sea.emptyCell(newX, newY)
            oldX, oldY = self.pos.getSeaPosition()
            if self.sea.setCell(newX, newY, self):
                self.setPosition(SeaPosition(newX,newY,self.sea))
                self.sea.emptyCell(oldX, oldY)
                self.starve = 0
                return True
        
    def turn(self):
        if self.alive:
            self.age += 1
            self.starve += 1
            if self.starve > self.starveAge:
                self.died()
            else:
                spawnX, spawnY = self.pos.getSeaPosition()
                empty, occupied = self.pos.getAdjacent()
                if len(occupied) > 0:
                    if self.eat(occupied):
                        self.spawn([(spawnX, spawnY)])
                elif len(empty) > 0:
                    if not self.spawn(empty):
                        self.move(empty)
    
    def __str__(self):
        return "%s %s Alive: %s" % ('Shark', Creature.__str__(self), str(self.alive))
    
class Fish(Creature):
    def __init__(self, sea, pos, spawnAge=2):
        Creature.__init__(self, sea, pos, spawnAge)
    
    def __str__(self):
        return "%s %s Alive: %s  Age: %d" % ('Fish', Creature.__str__(self), str(self.alive), self.age)
    
def wator(x,y,s,f,d='y'):
    '''
    x =  width of sea, y the height
    s = number of sharks, f the number of fishes
    d = y, display screen. if anything else, then give text output only.
    '''
    
    if (s+f) > x*y:
        print('Too many creatures')
        exit(2)
    
    aSea = Sea(x,y)
    
    for shark in range(s):
        noCell = True
        while noCell:
            xS = random.randint(0,x-1)
            yS = random.randint(0,y-1)
            if aSea.addCreature(xS,yS, Shark):
                noCell = False

    for fish in range(f):
        noCell = True
        while noCell:
            xF = random.randint(0,x-1)
            yF = random.randint(0,y-1)
            if aSea.addCreature(xF,yF, Fish):
                noCell = False

    if d == 'y':
        display = True
    else:
        display = False
    tick = 0
    while aSea.getSharks() != 0 and aSea.getFishes() != 0:  # in range(200):
        before = time.clock()
        if display:
            aSea.display()
        elapsedDisp = time.clock() - before
        tick += 1
        theCreatures = aSea.creatures.copy()
        before = time.clock()
        for c in theCreatures.values():
            c.turn()
        aSea.cleanCreatures()
        elapsedTurn = time.clock() - before
        print("Tick: %d ElapsedDisp: %2.4f ElapsedTurn: %2.4f %s"
              % (tick,elapsedDisp,elapsedTurn,aSea) )
            
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fishes", type=int,
                    help="initial number of fishes",
                    default=0)
parser.add_argument("-s", "--sharks", type=int,
                    help="initial number of sharks",
                    default=0)
parser.add_argument("-x", type=int,
                    help="number of horizontal cells",
                    default=200)
parser.add_argument("-y", type=int,
                    help="number of vertical cells",
                    default=200)
args = parser.parse_args()
total_cells = args.x * args.y
if args.sharks == 0:
    sharks = int(total_cells/10)
else:
    sharks = args.sharks
    
if args.fishes == 0:
    fishes = int(total_cells/4)
else:
    fishes = args.fishes 
    
wator(args.x, args.y, sharks, fishes)
