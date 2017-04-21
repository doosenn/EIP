# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 15:09:29 2016

@author: huangzhen

Main execution file
"""

from algorithms import ExpectedSupport
from models import ProbModel
#import time
import pandas as pd
import sys
#from joblib import Parallel, delayed
#import multiprocessing

#fListcsv = "flist.csv"
#indprobcsv = "indprobs.csv"
#seqdat = "seqFile.dat"

def processPattern(pattern, frequency, model):
    (expected, independent) = ExpectedSupport(pattern, model)
    return (frequency / expected, frequency / independent)
    
if __name__ == "__main__":
    patterncsv = sys.argv[1]
    seqdat = sys.argv[2]
    resultcsv = sys.argv[3]
    
    model = ProbModel(patterncsv, seqdat)
    freqPatterns = model.getFreqPatterns()
    
    counter = 0
    for pattern, frequency in freqPatterns.iteritems():
        # print("checking pattern: ", pattern)
        counter += 1
        (lift, indLift) = processPattern(pattern, frequency, model)
        model.setLift(pattern, lift, indLift)
        if counter % 500 == 0:
            print("checking", counter, "patterns")
        print(pattern, lift, indLift)
    
    "storing results:"
    result =  pd.DataFrame(list(model.lift.items()), columns=['pattern', 'lift'])
    result_ind = pd.DataFrame(list(model.indLift.items()), columns=['pattern', 'ind_lift'])
    result = result.merge(result_ind, how = "left", on = "pattern")
    result.to_csv(resultcsv, index = False)
    
    