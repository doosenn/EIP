# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 14:54:48 2016

@author: huangzhen

Main algorithms to calculate expectation
"""

from models import StateHistory
from itertools import combinations

def ExpectedSupport(episode, model):
    """
    Type:
    episode: array of events
    model: ProbModel
    return: float, expected support of pattern based on model 
    """
    
    maximum = 0.0
    ind = 0.0
    subepisodes = getSubepisodes(episode)
    
    for subepisode in subepisodes:
        expected = calcExpectedSupport(subepisode, episode, model)
        if expected > maximum:
            maximum = expected
        if len(subepisode) == 0:
            ind = expected
            
    return (maximum, ind)
           
def calcExpectedSupport(subepisode, episode, model):
    """
    Type:
    subepisode: the fixed subepisode
    episode: array of events
    model: a model to calculate expectations
    return: expected support
    
    """
    startState = StateHistory(episode)
    
    possibleStates = [startState]
    probs = {(startState.toTuple(), 0): 1.0}
    expectedSupport = 0.0
             
    for point in range(0, model.seqLen - 1): # seq_len
        "Use point to update point+1"
        nPossibleStates = []
        for state in possibleStates: # O(2^(pattern_len))
            
            events = set(state.Transferevents())
            eventsetProbs = getEventsetProbs(model.getEventsProb(events, subepisode\
                                                                 , point + 1))
            
            for eventset in eventsetProbs: # O(2^(pattern_len))
                nState = state.copy()
                sankNum = nState.updateEvents(eventset)
                prob = probs[(state.toTuple(), point)] * eventsetProbs[eventset]

                if (nState.toTuple(), point+1) not in probs:
                    nPossibleStates.append(nState)
                    probs[(nState.toTuple(), point+1)] = 0
                probs[(nState.toTuple(), point+1)] += prob
                if sankNum > 0:
                    expectedSupport += prob
                
        possibleStates = nPossibleStates
        
    return expectedSupport
    
    
def getEventsetProbs(eventProbs):
    """
    Type:
    eventProbs: dict, keys: events, values: prob
    return: dict, keys: eventsets, values: probs
    
    """
    events = eventProbs.keys()
    eventsets = combs(events, proper = False)
    probs = {}
    for eventset in eventsets:
        prob = CalcProbs(eventset, eventProbs)
        if prob > 0.0:
            probs[eventset] = prob
    return probs

def CalcProbs(eventset, eventProbs):
    """
    Type:
    eventset: list of event
    eventProbs: a dictionary of events and probs
    return the prob of the eventset based on eventProbs
    """
    prob = 1.0
    for event in eventProbs.keys():
        if event in eventset:
            prob *= eventProbs[event]
        else:
            prob *= (1 - eventProbs[event])
    return prob
    
def combs(events, proper = True):
    """
    Type:
    events: list of anything
    proper: whether to use proper subset
    return: combinations of events
    """
    eventsets = []
    l = len(events)
    if proper == False:
        l = l + 1
    for n in range(l):
        for eventset in set(combinations(events, n)):
            eventsets.append(eventset)
    return eventsets
    
def getSubepisodes(episode):
    """
    Type:
    episode: array of events
    model: ProbModel
    return: list of episodes, informative subepisodes of episode 
    """
    events = set(episode)
    return combs(events)
