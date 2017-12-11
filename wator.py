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
import time
import pickle

from sea import *

def wator():
    import random
    
    args = command_line()

    # set the RNG
    if args.system:
        random = random.SystemRandom()
    else:
        random.seed(42)
        
    # check --Commit > 0
    if args.Save:
        if args.Commit < 1:
            print("--Commit must be greater than zero")
            exit(2)
    # restore, or start new
    chronon = 0
    if args.Restore:
        [aSea, chronon] = restoreSea(random)
        args.Save = True # if restored, implies that commits need to continue.
    else:
        aSea = generateSea(args.x, args.y, args.sharks, args.fishes, args.traditional, args.sharkspawn, args.sharkstarve, args.fishspawn, random)
        
    # run the simulation
    run_simulation(aSea, args.chronons, args.Save, args.Commit, chronon)

def restoreSea(random,save_s="commits/save_sea.p",save_c="commits/save_creatures.p"):
    """
    Restore from the file.
    """
    try:
        [x, y, creatureTag, fileNumber, chronon] = pickle.load(open(save_s, "rb" ))
        theSea = Sea(x, y, random)
        theSea.setCreatureTag(creatureTag)
        theSea.setFileNumber(fileNumber)
    except FileNotFoundError:
        print("Restore file save_sea.p not found")
        exit(3)
    except Exception as e:
        print(repr(e))
    
    # using a generator, so that creatures can be iterated
    try:
        for [creature, x, y, traditional, spawnAge, starveAge, alive, age, starve] in readCreatures(save_c):
            c = theSea.addCreature(x,y,creature,traditional,spawnAge,starveAge)
            if c != None:
                c.setAge(age)
                c.setStarve(starve)
    except Exception as f:
        print('f', repr(f))

    return [theSea, chronon]

def readCreatures(pickleFile):
        try:
            with open(pickleFile, "rb" ) as pickleFH:
                while True:
                    yield pickle.load(pickleFH)
        except FileNotFoundError:
            print("Restore file save_creatures.p not found")
            exit(3)
        except EOFError:
            pass
        
def saveSea(saveSea, chronon,save_s="commits/save_sea.p",save_c="commits/save_creatures.p"):
    """
    Save sea and creatures for later restore.
    """
    seaFH  = open(save_s, "wb")
    pickle.dump(saveSea.exportSea() + [chronon], seaFH)
    seaFH.close()
    
    creatureFH = open(save_c, "wb")
    for c in saveSea.creatures.values():
        pickle.dump(c.exportCreature(), creatureFH)
    creatureFH.close()    

        
def generateSea(x,y,s,f,traditional,sharkspawn,sharkstarve,fishspawn, random):
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
#    # check the number of chronons to run.
#    # 999,999 is over 11 hours at 24fps, and most likely far beyond.
#    # the storage space.
#    if chronons < 1 or chronons > 999999:
#        print("Chronons must be in range 1 - 999999")
#        quit(3)

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

    aSea = Sea(x,y,random)

    for shark in range(s):
        noCell = True
        while noCell:
            xS = random.randint(0,x-1)
            yS = random.randint(0,y-1)
            if aSea.addCreature(xS,yS,Shark,traditional,sharkspawn,sharkstarve) != None:
                noCell = False

    for fish in range(f):
        noCell = True
        while noCell:
            xF = random.randint(0,x-1)
            yF = random.randint(0,y-1)
            if aSea.addCreature(xF,yF,Fish,traditional,fishspawn) != None:
                noCell = False
    
    return aSea

def command_line():                
    # Parse options, then run simulation()
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--chronons", type=int,
                        help="maximum number of chronons to calculate, default 999999",
                        default=999999)
    parser.add_argument("-C", "--Commit", type=int,
                        help="number of chronons between saving to file, default 25",
                        default=25)
    parser.add_argument("-f", "--fishes", type=int,
                        help="initial number of fishes, default 1/4 of the sea",
                        default=0)
    parser.add_argument("--fishspawn", type=int,
                        help="age that a fish spawns at, default 2, must be greater than 0",
                        default=2)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-R", "--Restore", action="store_true",
                        help="restore a saved sea",
                        default=False)
    group.add_argument("-S", "--Save", action="store_true",
                        help="save the sea at --Commit intervals",
                        default=False)
    parser.add_argument("-s", "--sharks", type=int,
                        help="initial number of sharks, default 1/10 of the sea",
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
        args.sharks = int(total_cells/10)
    else:
        args.sharks = args.sharks
    if args.fishes == 0:
        args.fishes = int(total_cells/4)
    else:
        args.fishes = args.fishes

    return args    
    

def run_simulation(aSea, chronons, save, commit, firstChronon=0):
    """
    aSea = sea containing all creatures.
    chronons = maximum number of chronons to run.
    save = if True save to file.
    commit = number of chronons between commits.
    """

    # print first message
    print("BEGIN -:- maxX: %d maxY: %d Positions: %d" % (aSea.getMaxX(), aSea.getMaxY(), aSea.getMaxX() * aSea.getMaxY()))

    startTime = time.clock()
    tick = firstChronon
    while tick < firstChronon+chronons and aSea.getSharks() != 0 and aSea.getFishes() != 0:  # in range(200):
        before = time.clock()
        theCreatures = aSea.creatures.copy()
        for c in theCreatures.values():
            c.turn()
        aSea.cleanCreatures()
        elapsedTurn = time.clock() - before
        before = time.clock()
        aSea.display()
        elapsedDisp = time.clock() - before
        if save:
            if tick % commit == 0:
                saveSea(aSea, tick)
        tick += 1
        print("Chronon: %06d Turn: %3.4f Display: %3.4f %s"
              % (tick,elapsedTurn,elapsedDisp,aSea) )
    endTime = time.clock()
    # final commit
    if save:
        saveSea(aSea, tick)

    # print final message
    hours, remainingSeconds = divmod(endTime-startTime, 3600)
    minutes, seconds = divmod(remainingSeconds, 60)
    print("END -:- Simulation complete after %d chronons. Ran for %d:%02d:%02d" % (tick, hours, minutes, seconds))


wator()
