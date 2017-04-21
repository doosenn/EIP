# -*- coding: utf-8 -*-
"""
Created on Tue Dec 8th, 2016

@author: huangzhen

Models used to calculate expectation
"""

import numpy as np
import pandas as pd

emptyEvent = ' ' # string representing an empty event
msupp = 20

class ProbModel:
    def __init__(self, patterncsv, seqdat):
        """
        Type:
        patterncsv: csv filename
        fListcsv: csv filename
        indprobcsv: csv filename
        seqdat: dat filename
        """
        self.patterns = pd.read_csv(patterncsv, dtype = {"patterns": np.str, \
                                                    "positions": np.str})
        self.patterns["patterns"] = self.patterns["patterns"].str.split(";").apply(tuple)
        self.patterns["positions"] = self.patterns["positions"].str.split(";")
        self.patterns["freq"] = self.patterns["positions"].apply(len)
        self.patterns["len"] = self.patterns["patterns"].apply(len)
        self.patterns = self.patterns[self.patterns["freq"] >= msupp]
        self.patterns.sort_values(by = "len", inplace = True) # sort with len
        
        self.seqLen = 0
        self.fList = {}
        for line in open(seqdat, 'r'):
            stamp = line.rstrip()
            if len(stamp) == 0:
                break
            [time, events] = stamp.split("\t")
            self.seqLen = max(int(time), self.seqLen)
            
            events = events.split(",")
            for event in events:
                if event not in self.fList:
                    self.fList[event] = []
                self.fList[event].append(time)
                    
        self.indProbs = {}
        for event in self.fList:
            self.indProbs[event] = len(self.fList[event]) / self.seqLen
                
        self.lift = {}
        self.indLift = {}
        
    def getEventsProb(self, events, fixedevents, at):
        """
        Type:
        events: array of event
        fixedevents: events that are fixed
        return: float, probability
        """
        probs = {}
        for event in events:
            if event in fixedevents:
                if str(at) in self.fList[event]:
                    probs[event] = 1.0
                else:
                    probs[event] = 0.0
            else:
                probs[event] = self.indProbs[event]

        return probs
            
    def getFreqPatterns(self):
        """
        return: series of frequent patterns and frequencies
        """
        freqPatterns = self.patterns[self.patterns["freq"] >= msupp]
        return freqPatterns.set_index("patterns")["freq"]
    
    def setLift(self, pattern, lift, indLift):
        """
        Type:
        pattern: array of event
        lift: float
        """
        self.lift[tuple(pattern)] = lift
        self.indLift[tuple(pattern)] = indLift

    def getLift(self, pattern):
        """
        Type:
        pattern: array of event
        return: float, lift
        """
        return self.lift[tuple(pattern)]
    
    def getIndProbs(self):
        """
        return: dict, keys: all events, values: probabilities for each event
        """
        return self.indProbs

class FiniteStateMachine:
    """
    List implementation
    """
        
    def __init__(self, pattern):
        """
        Type:
        pattern: array of event
        """
        self.pattern = pattern

    def getState(self, index):
        """
        Type:
        index: int, range [0, len-1]
        return: events, state
        """
        return self.pattern[0:index]
            
    def getEvent(self, index):
        """
        Type:
        index: int, range [0, len-1]
        return: event, next event
        """
        if index < len(self.pattern):
            return self.pattern[index]
        else:
            return emptyEvent

    def getLength(self):
        """
        return: length of the machine
        """
        return len(self.pattern)
        
         
class StateHistory:
    def __init__(self, episode, states = {0}):
        """
        Type:
        episode: the episode we are investigating, array of events
        states: set of int, int range [0, len(machine)-1]
        """
        self.machine = FiniteStateMachine(episode)
        self.states = states
        
    def toTuple(self):
        """
        return: tuple of states
        """
        return tuple(self.states)
       
    def updateEvents(self, events):
        """
        Type:
        events: list of event
        return: the number of sank states
        """
        eventset = set(events)
        sanks = 0
            
        states = self.states.copy()
        for state in states:
            if self.machine.getEvent(state) in eventset: # event match
                if(state == 0):
                    self.states.add(1)
                else:
                    self.states.remove(state) # remove old state
                    self.states.add(state + 1) # add new state
                if(state + 1 == self.machine.getLength()):
                    sanks += 1
                
        return sanks
                    
    def copy(self):
        """
        return: a copy of StateHistory
        """
        nStates = self.states.copy()
        return StateHistory(self.machine.pattern, nStates)
                
    def Transferevents(self):
        """
        return: events that can transfer any machine in history
        """
        
        events = []
        for state in self.states:
            event = self.machine.getEvent(state)
            if(event != emptyEvent and event not in events):
                events.append(event)
                
        return events
        
    """
    Depreciated
    def __calcProbs(self, eventset, eventDict):
        \"""
        eventset: list of event
        eventDict: a dictionary of events and probs
        return the prob of the eventset based on eventDict
        \"""
        prob = 1.0
        for event in eventDict.keys():
            if event in eventset:
                prob *= eventDict[event]
            else:
                prob *= (1 - eventDict[event])
        return prob
        
        
    def __TransferEventProbs(self):
        \"""
        return: dict of events and probs
        \"""
        events = {}
        for state in self.states:
            event = self.machine.getEvent(state)
            if(event != emptyEvent and event not in events):
                events[event] = self.machine.getProb(state)
                
        return events
    """
        
