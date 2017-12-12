#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 17:06:04 2017

@author: michael

The creatures that live in the sea.
SeaCreature is the supper class from which the creatures
in the simulation are created.
"""

from seaposition import *
from sea import *

class SeaCreature(object):
    """
    Super class of all sea creatures.
    """
    def __init__(self, sea, pos, traditional, spawnAge, starveAge, random):
        """
        Simple creature, reproduces quickly, does not eat, and never dies except if eaten.
        """
        self.sea = sea
        self.pos = pos
        self.traditional = traditional
        self.age = 0
        self.totalAge = self.age
        self.spawnAge = spawnAge
        self.starve = 0
        self.starveAge = starveAge # set but not used by basic creature
        self.alive = True
        self.random = random

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
            spawnX, spawnY = self.random.choice(free)
            self.sea.addCreature(spawnX, spawnY, type(self), self.traditional, self.spawnAge, self.starveAge)
            self.age = 0
            return True
        else:
            return False

    def move(self,empty):
        """
        Move to a space it is empty.
        """
        newX, newY = self.random.choice(empty)
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
            self.totalAge += 1
            empty, occupied = self.pos.getAdjacent(self.traditional)
            if len(empty) > 0:
                if not self.spawn(empty):
                    self.move(empty)

    def setAge(self,age):
        self.age = age
        self.totalAge = age

    def setStarve(self,starve):
        self.starve = starve

    def exportCreature(self):
        return [self.pos.getX(), self.pos.getY(), self.traditional, self.spawnAge, self.starveAge, self.alive, self.age, self.starve]

    def __str__(self):
        return "%s" % str(self.pos)

class Shark(SeaCreature):
    """
    Extend a regular sea creature to hunt and eat - be a shark
    """
    def __init__(self, sea, pos, traditional, spawnAge, starveAge, random):
        SeaCreature.__init__(self, sea, pos, traditional, spawnAge, starveAge, random)

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
            newX, newY = self.random.choice(fishes)
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
            self.totalAge += 1
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
                elif len(empty) > 0:
                    if not self.spawn(empty):
                        self.move(empty)
    
    def exportCreature(self):
        return [type(self)] + SeaCreature.exportCreature(self)

    def __str__(self):
        return "%s %s Alive: %s Age: %d Spawn: %d Starve: %d" % ('Shark', SeaCreature.__str__(self), str(self.alive), self.totalAge, self.spawnAge-self.age, self.starveAge-self.starve)

class Fish(SeaCreature):
    """
    Extend sea creature, and identify it as a fish. 
    """
    def __init__(self, sea, pos, traditional, spawnAge, starveAge, random):
        SeaCreature.__init__(self, sea, pos, traditional, spawnAge, starveAge, random)

    def exportCreature(self):
        return [type(self)] + SeaCreature.exportCreature(self)

    def __str__(self):
        return "%s %s Alive: %s Age: %d Spawn: %d Starve: %d" % ('Fish', SeaCreature.__str__(self), str(self.alive), self.totalAge, self.spawnAge-self.age, self.starveAge-self.starve)
