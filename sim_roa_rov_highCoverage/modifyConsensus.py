import pickle
import csv
import time
import sys
from util import *

#change consensus roa coverage 
def modify_roa_coverage(roaASN):
    #the duration of consensus we are trying to change 
    start_date = datetime(2020, 9, 1, 00)
    end_date = datetime(2020, 9, 5, 00)
    resultLS = []
    pathBase = '/home/siyang/research/tor-rpki/processed/'
    #get a list of dates inside this duration 
    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
        resultLS.append(t.strftime('%Y')+'-'+t.strftime('%m') +'-'+ t.strftime('%d')+'-'+ t.strftime('%H')+'-'+'processed.pickle')

    #iterate through each date 
    for date in resultLS:
        path = pathBase + date
        #open the consensus in current date 
        with open(path, 'rb') as f:
            rs = pickle.load(f)
            WGD = pickle.load(f) #weight in the consensus
            WGG = pickle.load(f)
            gs = [r for r in rs if r.is_guard]
        #iterate through the guards to see if it has roa 
        for g in gs:
            if g.asn != None:
                gasn = g.asn[0]
            else:
                gasn = None
            if gasn in roaASN:
                g.ipv4_roa = 'has roa'
            else:
                g.ipv4_roa = None

        with open('HighROAROVConsensus/' + date, 'wb') as f:
            pickle.dump(gs,f)
            pickle.dump(WGD, f)
            pickle.dump(WGG, f)

def get_roa_asn(fname):
    roaASN = set()
    with open(fname, 'r') as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            roaASN.add(row[0])
    return list(roaASN)

def testChange(file):
    roa = 0
    with open(file, 'rb') as f:
        gs = pickle.load(f)

    for g in gs:
        if g.ipv4_roa == True:
            roa += 1
    print(roa/len(gs))

#add more asn to rov set 
def increaseROV(rovPickle):
    tier1AS = [7018, 3320, 3257, 6830, 3356, 3549, 2914, 5511, 3491, 1239, 6453, 6762, 1299, 12956, 701, 6461]
    with open(rovPickle, 'rb') as f:
        ROVlist = pickle.load(f)
    ROVset = set(ROVlist)
    for i in tier1AS:
        ROVset.add(str(i))
    result = list(ROVset)
    with open('ASNwROVHigh.pickle', 'wb') as f:
        pickle.dump(result, f)


def testConsensus(file):
    with open(file, 'rb') as f:
        rs = pickle.load(f)
        WGD = pickle.load(f) #weight in the consensus
        WGG = pickle.load(f)
        guard_rov = 0
        guard_roa = 0
        guard_roa_rov = 0
        gs = [r for r in rs if r.is_guard]
        totalGuard = len(gs)
        for g in gs:
            if g.asn != None:
                gasn = g.asn[0]
            else:
                gasn = None
            if check_rov(gasn) and g.ipv4_roa:
                guard_roa_rov += 1
            elif g.ipv4_roa != None:
                guard_roa += 1
            elif check_rov(gasn):
                guard_rov += 1
        print('percent guard with roa&rov:', guard_roa_rov/totalGuard)
        print('percent guard with rov:',guard_rov/totalGuard) 
        print('percent guard with roa:', guard_roa/totalGuard)
    
# newROA = get_roa_asn('/home/siyang/research/tor-rpki/20200913.csv')
# modify_roa_coverage(newROA)

testConsensus('/home/siyang/research/tor-rpki/processed/2020-09-01-00-processed.pickle')