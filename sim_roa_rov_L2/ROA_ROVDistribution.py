import ipaddress
from util import *
from distributeUser import *
import numpy

#make roa dict, ip prefix -> [asn, max length]
#check if rv2 data is in the roa Dict, if its in than add the num hosts into roa covered field 
#if not check to see it 
def getROA_ROV_freq(numRuns, clientSize):
    """
    analyzes the roa, rov, roa_rov coverage for randomly generated clients

    :param numRuns: number of times the function runs the client generation function 
    :clientSize: number of clients generated each time 
    """
    roa = []
    rov = []
    roa_rov = []
    neither = []
    count = numRuns
    while count > 0:
        print(count)
        clients, specs = assignASN(clientSize, countries, cweights, 'matching', '/home/siyang/research/tor-rpki/20200913.csv')
        roa.append(specs[1])
        rov.append(specs[2])
        neither.append(specs[3])
        roa_rov.append(specs[0])
        count -= 1
    
    return roa, rov, roa_rov, neither
                
        
roa, rov, roa_rov, neither = getROA_ROV_freq(30, 1000)
# with open('returnSpecs.pickle', 'wb') as f1:
#     pickle.dump("the pickle for 50 run", f1)
#     pickle.dump(roa, f1)
#     pickle.dump(rov, f1)
#     pickle.dump(roa_rov, f1)
#     pickle.dump(neither, f1)

f = open('returnSpecs.pickle', 'rb') 
pickle.load(f)
roa = pickle.load(f)
rov = pickle.load(f)
roa_rov = pickle.load(f)
neither = pickle.load(f)

# print(round(numpy.mean(roa)),round(numpy.mean(rov)),round(numpy.mean(roa_rov)),round(numpy.mean(neither)))
# print(x)
# print(y)
#result 1000 of running 10 times:
# roa, rov, roa_rov, neither
# roa = [241, 209, 215, 233, 208, 223, 223, 216, 186, 221]
# rov = [7, 18, 14, 26, 15, 16, 15, 11, 11, 19]
# roa_rov = [9, 8, 11, 2, 5, 7, 3, 12, 5, 7]
# neither = [743, 765, 760, 739, 772, 754, 759, 761, 798, 753]
# all = [roa, rov, roa_rov, neither]

# avg = []
# for i in all:
#     localAvg = 0
#     for e in range(0,10):
#         localAvg += i[e]
#     avg.append(round(localAvg/10))
# print(avg)
#roa, rov, roa_rov, neither 
# avg = [218, 15, 7, 760]
# total = 0
# for i in avg:
#     total += i
# print(total)