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
from seadisplay import *

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
        [aSea, aSeaView, chronon] = restoreSea(random)
        args.Save = True # if restored, implies that commits need to continue.
    else:
        aSea = generateSea(args.x, args.y, args.sharks, args.fishes, args.traditional, args.sharkspawn, args.sharkstarve, args.fishspawn, random)
        aSeaView = SeaDisplay(aSea)

        
    # run the simulation
    run_simulation(aSea, aSeaView, args.chronons, args.Save, args.Commit, chronon, args.verbose)

def restoreSea(random,save_s="commits/save_sea.p",save_c="commits/save_creatures.p"):
    """
    Restore from the file.
    """
    nextid = 0
    try:
        [x, y, lastid, fileNumber, chronon] = pickle.load(open(save_s, "rb" ))
        theSea = Sea(x, y, random)
        theDisplay = SeaDisplay(theSea, fileNumber)
        nextid = lastid
    except FileNotFoundError:
        print("Restore file", save_s, "not found")
        exit(3)
    except Exception as A:
        print("Restore Failure A:", repr(A))

    # using a generator, so that creatures can be iterated
    try:
        for [creature, ID, parent, x, y, traditional, spawnAge, starveAge, alive, totalage, age, starve] in readCreatures(save_c):
            c = theSea.addCreature(x,y,creature,traditional,spawnAge,parent,starveAge)
            if c != None:
                c.setAge(age)
                c.setTotalAge(totalage)
                c.setStarve(starve)
                c.setCreatureID(ID)
                c.setNextID(nextid)
    except FileNotFoundError:
        print("Restore file", save_c, "not found")
        exit(3)
    except Exception as B:
        print("Restore Failure B:", repr(B))

    return [theSea, theDisplay, chronon]

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
        
def saveSea(saveSea, saveDisplay, chronon,save_s="commits/save_sea.p",save_c="commits/save_creatures.p"):
    """
    Save sea and creatures for later restore.
    """
    seaFH  = open(save_s, "wb")
    pickle.dump(saveSea.exportSea() + [saveSea.creatures[0].getNextID()] + saveDisplay.exportDisplay() + [chronon], seaFH)
    seaFH.close()
    
    creatureFH = open(save_c, "wb")
    for c in saveSea.creatures:
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

    defaultParent = 0
    for shark in range(s):
        noCell = True
        while noCell:
            xS = random.randint(0,x-1)
            yS = random.randint(0,y-1)
            newShark = aSea.addCreature(xS,yS,Shark,traditional,sharkspawn, defaultParent, sharkstarve)
            if newShark != None:
                sharkAge = random.randint(0, sharkspawn - 1)
                newShark.setAge(sharkAge)
                newShark.setTotalAge(sharkAge)
                newShark.setStarve(random.randint(0, sharkstarve - 1))
                noCell = False

    for fish in range(f):
        noCell = True
        while noCell:
            xF = random.randint(0,x-1)
            yF = random.randint(0,y-1)
            newFish = aSea.addCreature(xF,yF,Fish,traditional,fishspawn, defaultParent)
            if newFish != None:
                fishAge = random.randint(0, fishspawn - 1)
                newFish.setAge(fishAge)
                newFish.setTotalAge(fishAge)
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
    parser.add_argument("-v", "--verbose", action="count",
                        help="-v creature summary per chronon, -vv all creatures per chronon",
                        default=False)
    parser.add_argument("-x", type=int,
                        help="number of horizontal cells, default 200",
                        default=200)
    parser.add_argument("-y", type=int,
                        help="number of vertical cells, default 200",
                        default=200)
    # get the arguments
    args = parser.parse_args()
    
    # check the number of chronons to run.
    # 999,999 is over 11 hours at 24fps, and most likely far beyond.
    # the storage space.
    if args.chronons < 1 or args.chronons > 999999:
        print("Chronons must be in range 1 - 999999")
        quit(3)

    # check the number of chronons to run.
    # 999,999 is over 11 hours at 24fps, and most likely far beyond.
    # the storage space.
    if args.verbose > 4:
        print("Warning: verbosity can only be set to -vvvv, or --verbose --verbose --verbose --verbose")
        args.verbose = 4
    
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
    

def run_simulation(aSea, seaView, chronons, save, commit, firstChronon=0, verbosity=0):
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
    simulating  = True
    while simulating and tick < firstChronon+chronons and aSea.getSharks() != 0 and aSea.getFishes() != 0:  # in range(200):
        before = time.clock()
        theCreatures = aSea.creatures.copy()
        for c in theCreatures:
            c.turn()
        aSea.cleanCreatures()
        elapsedTurn = time.clock() - before
        before = time.clock()
        simulating = seaView.showImage(aSea,True)
        elapsedDisp = time.clock() - before
        if save:
            if tick % commit == 0:
                saveSea(aSea, seaView, tick)
        tick += 1
        if verbosity > 0:
            print("Chronon: %06d Turn: %3.4f Display: %3.4f %s"
                  % (tick,elapsedTurn,elapsedDisp,aSea) )
        if verbosity > 1:
            verbalSharks = {}
            for creature in aSea.creatures:
                if type(creature) is Shark:
                    try:
                        verbalSharks[creature.getAge()] += 1
                    except:
                        verbalSharks[creature.getAge()] = 1
            for summary in sorted(verbalSharks):                        
                print("Chronon: %06d Shark Age: %d Count: %d" % (tick, summary, verbalSharks[summary]))
        if verbosity > 2:
            verbalFishes = {}
            for creature in aSea.creatures:
                if type(creature) is Fish:
                    try:
                        verbalFishes[creature.getAge()] += 1
                    except:
                        verbalFishes[creature.getAge()] = 1
            for summary in sorted(verbalFishes):                        
                print("Chronon: %06d Fish Age: %d Count: %d" % (tick, summary, verbalFishes[summary]))
        if verbosity > 3:
            for creature in aSea.creatures:
                print("Chronon: %06d %s" % (tick, creature))

    endTime = time.clock()
    # final commit
    if save:
        saveSea(aSea, seaView, tick)
    
    # print final message
    hours, remainingSeconds = divmod(endTime-startTime, 3600)
    minutes, seconds = divmod(remainingSeconds, 60)
    print("END -:- Simulation complete after %d chronons. Ran for %d:%02d:%02d" % (tick, hours, minutes, seconds))

    # terminate display
    seaView.Quit()

wator()
