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
import time

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

class Sea(object):
    """
    A sea of x by y cells.
    A cell can hold one thing or be empty (None).
    """
    def __init__(self, x, y):
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
            creature = newCreature(self, pos, t, spawn, starve)
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

    def __str__(self):
        sharks = self.getSharks()
        fishes = self.getFishes()
        positions = self.maxX * self.maxY
        empty = positions - sharks - fishes
        return "Sharks: %d Fishes: %d Empty: %d" % (sharks, fishes, empty)


class Creature(object):
    """
    Super class of all sea creatures.
    """
    def __init__(self, sea, pos, traditional, spawnAge, starveAge):
        """
        Simple creature, reproduces quickly, does not eat, and never dies except if eaten.
        """
        self.sea = sea
        self.pos = pos
        self.traditional = traditional
        self.age = 0
        self.spawnAge = spawnAge
        self.starveAge = starveAge # set but not used by basic creature
        self.alive = True

    def getPosition(self):
        return self.pos

    def setPosition(self, pos):
        self.pos = pos

    def isAlive(self):
        return self.alive

    def died(self):
        """
        Remove from sea, and set dead (alive = False)
        """
        x,y = self.pos.getSeaPosition()
        self.sea.emptyCell(x,y)
        self.alive = False

    def spawn(self,free):
        """
        If old enough, and there is free space, spawn.
        """
        if self.age >= self.spawnAge:
            spawnX, spawnY = random.choice(free)
            self.sea.addCreature(spawnX, spawnY, type(self), self.traditional, self.spawnAge, self.starveAge)
            self.age = 0
            return True
        else:
            return False

    def move(self,empty):
        """
        Move to a space it is empty.
        """
        newX, newY = random.choice(empty)
        oldX, oldY = self.pos.getSeaPosition()
        if self.sea.setCell(newX, newY, self):
            self.sea.emptyCell(oldX, oldY)
            self.pos = SeaPosition(newX, newY, self.sea)

    def turn(self):
        """
        The basic creature moves or spawns and moves.
        """
        if self.alive:
            self.age += 1
            empty, occupied = self.pos.getAdjacent(self.traditional)
            if len(empty) > 0:
                if not self.spawn(empty):
                    self.move(empty)

    def __str__(self):
        return "%s" % str(self.pos)

class Shark(Creature):
    """
    Extend a regular sea creature to hunt and eat - be a shark
    """
    def __init__(self, sea, pos, traditional, spawnAge, starveAge):
        Creature.__init__(self, sea, pos, traditional, spawnAge, starveAge)
        self.starve = 0

    def eat(self,occupied):
        """
        Either find something to eat, or move (randomly) to a free adjacent spot.
        """
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
        """
        Sharks can die of starvation. If it has not starved try to eat
        after eating spawn (if possible). If there are no fish nearby, and 
        spawning is possible, spawn, otherwise move.
        """
        if self.alive:
            self.age += 1
            self.starve += 1
            if self.starve > self.starveAge:
                self.died()
            else:
                spawnX, spawnY = self.pos.getSeaPosition()
                empty, occupied = self.pos.getAdjacent(self.traditional)
                if len(occupied) > 0:
                    if self.eat(occupied):
                        self.spawn([(spawnX, spawnY)])
                elif len(empty) > 0:
                    if not self.spawn(empty):
                        self.move(empty)

    def __str__(self):
        return "%s %s Alive: %s" % ('Shark', Creature.__str__(self), str(self.alive))

class Fish(Creature):
    """
    Extend sea creature, and identify it as a fish. 
    """
    def __init__(self, sea, pos, traditional, spawnAge, starveAge):
        Creature.__init__(self, sea, pos, traditional, spawnAge, starveAge)

    def __str__(self):
        return "%s %s Alive: %s  Age: %d" % ('Fish', Creature.__str__(self), str(self.alive), self.age)

def run_simulation(x,y,s,f,traditional,chronons,sharkspawn,sharkstarve,fishspawn, commit, file, restore, save):
    """
    x =  width of the sea, y the height of the sea - longitude and latitude.
    s = number of sharks, f the number of fishes - all creaturs (so far).
    traditional = traditional creature movement - n,e,s,w.
        default is new - n, ne, e, se, s, sw, w, ne.
    chronons = maximum number of chronons to run.
    sharkspawn = age at which a shark breeds.
    sharkstarve = age at which a shark dies if it has not eaten.
    fishspawn = age at which a fish spawns.
    """

    # the number of sharks and fishes cannot be greater than the
    # size of the sea
    if (s+f) > x*y:
        print('Too many creatures')
        exit(2)
    # check the number of chronons to run.
    # 999,999 is over 11 hours at 24fps, and most likely far beyond.
    # the storage space.
    if chronons < 1 or args.chronons > 999999:
        print("Chronons must be in range 1 - 999999")
        quit(3)

    # check sharkspawn
    if sharkspawn < 1:
        print("Shark spawn age must be greater than zero.")
        quit(4)

    # check sharkspawn
    if sharkstarve < 1:
        print("Shark starve time must be greater than zero.")
        quit(4)

    # check fishpawn
    if fishspawn < 1:
        print("Fish spawn age must be greater than zero.")
        quit(4)

    aSea = Sea(x,y)

    for shark in range(s):
        noCell = True
        while noCell:
            xS = random.randint(0,x-1)
            yS = random.randint(0,y-1)
            if aSea.addCreature(xS,yS,Shark,traditional,sharkspawn,sharkstarve):
                noCell = False

    for fish in range(f):
        noCell = True
        while noCell:
            xF = random.randint(0,x-1)
            yF = random.randint(0,y-1)
            if aSea.addCreature(xF,yF,Fish,traditional,fishspawn):
                noCell = False

    # print first message
    print("BEGIN -:- maxX: %d maxY: %d Positions: %d" % (aSea.getMaxX(), aSea.getMaxY(), aSea.getMaxX() * aSea.getMaxY()))

    startTime = time.clock()
    tick = 0
    while tick < chronons and aSea.getSharks() != 0 and aSea.getFishes() != 0:  # in range(200):
        before = time.clock()
        theCreatures = aSea.creatures.copy()
        for c in theCreatures.values():
            c.turn()
        aSea.cleanCreatures()
        elapsedTurn = time.clock() - before
        before = time.clock()
        aSea.display()
        elapsedDisp = time.clock() - before
        tick += 1
        print("Chronon: %06d Turn: %3.4f Display: %3.4f %s"
              % (tick,elapsedTurn,elapsedDisp,aSea) )
    endTime = time.clock()

    # print final message
    hours, remainingSeconds = divmod(endTime-startTime, 3600)
    minutes, seconds = divmod(remainingSeconds, 60)
    print("END -:- Simulation complete after %d chronons. Ran for %d:%02d:%02d" % (tick, hours, minutes, seconds))


# Parse options, then call wator()
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--chronons", type=int,
                    help="maximum number of chronons to calculate, default 999999",
                    default=999999)
parser.add_argument("-C", "--Commit", type=int,
                    help="chronons between checkpoint saves, range 5 - 200, default 100",
                    default=100)
parser.add_argument("-F", "--File", type=str,
                    help="name of the checkpoints file, default save.p",
                    default='save.p')
parser.add_argument("-f", "--fishes", type=int,
                    help="initial number of fishes",
                    default=0)
parser.add_argument("--fishspawn", type=int,
                    help="age that a fish spawns at, default 2, must be greater than 0",
                    default=2)
group = parser.add_mutually_exclusive_group()
group.add_argument("-R", "--Restore", action='store_true',
                   help="restore from --File",
                   default=False)
group.add_argument("-S", "--Save", action='store_true',
                   help="save to --File",
                   default=False)
parser.add_argument("-s", "--sharks", type=int,
                    help="initial number of sharks",
                    default=0)
parser.add_argument("--sharkspawn", type=int,
                    help="age that a sharks spawns at, default 5, must be greater than 0",
                    default=5)
parser.add_argument("--sharkstarve", type=int,
                    help="chronons that a shark can live without eating, default 3, must be greater than 0",
                    default=3)
parser.add_argument("--system", action="store_true",
                    help="use SystemRandom giving unique runs, otherwise, default to a seed of 42",
                    default=False)
parser.add_argument("-t", "--traditional", action="store_true",
                    help="traditional search pattern",
                    default=False)
parser.add_argument("-x", type=int,
                    help="number of horizontal cells, default 200",
                    default=200)
parser.add_argument("-y", type=int,
                    help="number of vertical cells, default 200",
                    default=200)
# get the arguments
args = parser.parse_args()
# calculate the size of the sea
total_cells = args.x * args.y

if args.sharks == 0:
    sharks = int(total_cells/10)
else:
    sharks = args.sharks
if args.fishes == 0:
    fishes = int(total_cells/4)
else:
    fishes = args.fishes
# determine RNG
if args.system:
    random = random.SystemRandom()
else:
    random.seed(42)

run_simulation(args.x, args.y, sharks, fishes, args.traditional, args.chronons, args.sharkspawn, args.sharkstarve, args.fishspawn, args.Commit, args.File, args.Restore, args.Save)
