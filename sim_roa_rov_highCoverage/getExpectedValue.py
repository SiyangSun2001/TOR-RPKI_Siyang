import pickle
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from distributeUser import *
import pickle

UserPerCountry = {'US': 0.2429, 'RU': 0.1543, 'DE': 0.07980000000000001, 'NL': 0.040999999999999995, 'FR': 0.0346, 'ID': 0.0277, 'GB': 0.0256, 'IN': 0.0254, 'UA': 0.0215, 'LT': 0.0178}
countries = list(UserPerCountry.keys())
cweights = list(UserPerCountry.values())

#function that takes in an consensus file & discount value, then return the expected value for choosing an ROA covered guard
def get_Client_Coverage_ExpectedValue(consensus_date, discount):

    #path for processed pickle file
    p = '../processed/' + consensus_date + '-processed.pickle'

    #try to open the pickled file  
    try:
        file = open(p, 'rb')
    except FileNotFoundError:
        print(p, 'does not exist')
    

    rs = pickle.load(file) #list of all relay objects
    WGD = pickle.load(file) #weight in the consensus
    WGG = pickle.load(file) #weight in the consensus
    gs = [r for r in rs if r.is_guard] #get all the guards relay in a list
    
    ROAWeight = 0 #total weight of relay with ROA
    totalWeight = 0 #total weight of all relays 

    for r in gs: #iterate through all relays within the guards relays list
        if r.is_exit:  # if r is an exit
            if r.ipv4_roa != None: #the relay has roa 
                w = int(r.bw * WGD)  # wgd, g+e in g position
                ROAWeight += w #add weight to both var
                totalWeight += w
            else:
                w = int(r.bw * WGD)*float(discount) #does not have roa, so multiply discount and add to the total weight var 
                totalWeight += w
        else:
            if r.ipv4_roa != None:
                w = int(r.bw * WGG)  # wgg, g in g position
                ROAWeight += w
                totalWeight += w
            else:
                w = int(r.bw * WGG)*float(discount)
                totalWeight += w
    return ROAWeight, totalWeight


def get_LoadBalance_expectedValue(consensus_date, discount):
        #path for processed pickle file
    p = '../processed/' + consensus_date + '-processed.pickle'

    #try to open the pickled file  
    try:
        file = open(p, 'rb')
    except FileNotFoundError:
        print(p, 'does not exist')
    

    rs = pickle.load(file) #list of all relay objects
    WGD = pickle.load(file) #weight in the consensus
    WGG = pickle.load(file) #weight in the consensus
    gs = [r for r in rs if r.is_guard] #get all the guards relay in a list
    
    vanillaWeight = 0
    for r in gs:
        if r.is_exit:
            vanillaWeight += int(r.bw*WGD)
        else:
            vanillaWeight += int(r.bw * WGG)
    
    discountWeight = 0
    for r in gs: #iterate through all relays within the guards relays list
        if r.is_exit:  # if r is an exit
            if r.ipv4_roa != None: #the relay has roa 
                w = int(r.bw * WGD)  # wgd, g+e in g position
                discountWeight += w
                
            else:
                w = int(r.bw * WGD)*float(discount) #does not have roa, so multiply discount and add to the total weight var 
                discountWeight += w
        else:
            if r.ipv4_roa != None:
                w = int(r.bw * WGG)  # wgg, g in g position
                discountWeight += w
                
            else:
                w = int(r.bw * WGG)*float(discount)
                discountWeight += w
    return discountWeight, vanillaWeight


def get_LoadBalance_Matching(consensus_date, clientsFileName, roacsv, discountParams):
    #get the weight of relays assigned by all clients 
    #average all of client weight / vanilla weight 
    rovDiscount = discountParams[0]
    roaDiscount = discountParams[1]
    neitherDiscount = discountParams[2]
    
    with open(clientsFileName, 'rb') as f:
        clients = pickle.load(f)

            #path for processed pickle file
    p = 'HighROAROVConsensus/' + consensus_date + '-processed.pickle'

    #try to open the pickled file  
    try:
        file = open(p, 'rb')
    except FileNotFoundError:
        print(p, 'does not exist')
    
    rs = pickle.load(file) #list of all relay objects
    WGD = pickle.load(file) #weight in the consensus
    WGG = pickle.load(file) #weight in the consensus
    gs = [r for r in rs if r.is_guard] #get all the guards relay in a list
    vanillaWeight = 0
    for pg in gs:
        if pg.is_exit:  # if pg is an exit
            if pg.ipv4_roa == True:
                w = int(pg.bw * WGD)  # wgd, g+e in g position
            else:
                w = int(pg.bw * WGD)
        else:
            if pg.ipv4_roa == True:
                w = int(pg.bw * WGG)  # wgg, g in g position
            else:
                w = int(pg.bw * WGG)
        vanillaWeight += w
    numClients = len(clients)
    
#ROV and ROV & ROV case, discount all non ROA relay by 0.1
    ClientWeights = []
    roa = 0 
    rovROAROV = 0
    neither = 0
    for c in clients:
        weights = 0
        if check_rov(c.AS.ASN) or (check_rov(c.AS.ASN) and c.roaCovered == True): 
            rovROAROV += 1
            for pg in gs:
                if pg.is_exit:
                    consensusWeight = WGD
                else:
                    consensusWeight = WGG
                if pg.ipv4_roa == True:
                    w = int(pg.bw * consensusWeight)
                else:
                    w = int(pg.bw * consensusWeight)*rovDiscount
                weights += w


        #ROA case, discount non-rov relay by 0.6
        elif c.roaCovered == True:
            roa += 1
            for pg in gs:
                if pg.is_exit:
                    consensusWeight = WGD
                else:
                    consensusWeight = WGG
                if pg.asn != None:
                    if check_rov(pg.asn[0]):
                        w = int(pg.bw * consensusWeight)
                    else: 
                        w = int(pg.bw * consensusWeight)*roaDiscount
                weights += w

        #neither case, discount all relay with ROA or ROV by 0.1
        elif c.roaCovered == False and not check_rov(c.AS.ASN):
            neither += 1
            for pg in gs:
                if pg.is_exit:
                    consensusWeight = WGD
                else:
                    consensusWeight = WGG
                if pg.asn != None:
                    if not check_rov(pg.asn) and pg.ipv4_roa == None:
                        w = int(pg.bw * consensusWeight)
                    else:
                        w = int(pg.bw * consensusWeight)*neitherDiscount
                    weights += w
        ClientWeights.append(weights)

    totalLB = 0
    for w in ClientWeights:
        totalLB += w/vanillaWeight
    #tally up the bandwidth each from each client's prospective 
    #take the average of the bandwidth
    avgLB = totalLB/numClients
    print("Expected LoadBalancing for Matching Method: ", avgLB)
    print("%Clients w/ ROA: ", roa/numClients)
    print("%Clients w/ ROV or ROA_ROV: ", rovROAROV/numClients)
    print("%Clients with neither: ", neither/numClients)

    
def get_expectVal_wdiffLoad(consensus_date):
    discount = np.linspace(0.5,1,25)
    load = [ 0.8, 0.9, 1] # list of different network load 
    lb = {0.8:[],0.9:[], 1:[]} #load balance for each network load 

    performanceDecrease = [1]*25 #bound where mathcing performance is worse than vanilla 
    for l in load:
        
        for d in discount: 
            dis, van = get_LoadBalance_expectedValue(consensus_date, d)  
            lb[l].append(dis/(van*l))

    for key in lb.keys():
        calculated = False
        for i in range(len(lb[key])):      
            if lb[key][i] > 1 and not calculated:
                m = (lb[key][i] - lb[key][i-1])/(discount[i] - discount[i-1])
                b = lb[key][i] - m*discount[i]
                y = 1
                x = (y-b)/m

                lb[key][i] = 1
                discount[i] = x
                calculated = True
            elif lb[key][i] > 1 and calculated:
                lb[key][i] = 1

    
    # for l in load:
        
    #     for d in discount: 
    #         dis, van = get_LoadBalance_expectedValue(consensus_date, d)  
    #         lb1[l].append(dis/(van*l))
    # for k in lb1.keys():
    #     for i in range(len(lb1[k])):
    #         if lb1[k][i] != lb[k][i]:
    #             print("diff")
    #             print(lb1[k][i], lb[k][i])
                
            
    

    # print(lb)
    plt.figure(figsize = (8,8))#set figure size 
    plt.xlabel('Discount Value')
    plt.ylabel('Expected Value')
    plt.title('Expected Value of LoadBalance relative to Vanilla at diff network load' + consensus_date)
    
    #plot each network load's LB 
    for k in lb.keys():
        plt.plot(discount, lb[k], label = ("load: " + str(k)))
    plt.plot(discount, performanceDecrease, marker = '.',label = "Performance Benchmark", color = "black")
    plt.legend()
    
    plt.savefig('expectLBdiffLoad.png')


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("consensus_date", help="date in year-mo-da-hr format in which to calculate the expected value")
    parser.add_argument("numClients", help="number of client for sim (matching LB func)")
    parser.add_argument("roacsv", help="specify roa file to use when making clients")
    return parser.parse_args(args)

def main(args):
    # #parse arguments
    args = parse_arguments(args)
    consensus_date = args.consensus_date
    numClients = args.numClients
    roacsv = args.roacsv
    # # print(get_LoadBalance_Matching(consensus_date, numClients, roacsv ))
    # #get a list of value btw 0.5 and 1 for the discount 
    # discount = np.linspace(0.5,1,25)

    # # ExpectValROA = [] #ls for storing the expected value 

    # #iterate through all discount and calculate expected valq 
    # # for d in discount:
    # #     roaW, totalW = get_Client_Coverage_ExpectedValue(consensus_date, d)
    # #     ExpectValROA.append(roaW/totalW)

    # #graph the expected val v.s. discount
    # # plt.xlabel('Discount Value')
    # # plt.ylabel('Expected Value')
    # # plt.title('Expected Value of Choosing an ROA Covered Guard ' + consensus_date)
    # # plt.plot(discount, ExpectValROA)
    # # plt.savefig('expectROA.png')
    # # dis, van = get_LoadBalance_expectedValue(consensus_date, 0.7)
    # # print("at 0.7 the expected LB relative to vanilla is: ", dis/van)
    # load = [0.5, 0.6, 0.7, 0.8, 0.9, 1] # list of different network load 
    # lb = {0.5:[], 0.6:[],0.7:[],0.8:[],0.9:[], 1:[]} #load balance for each network load 
    # performanceDecrease = [1]*25 #bound where mathcing performance is worse than vanilla 
    
    # #get LB @ each different network load, store in dict 
    # for l in load:
        
    #     for d in discount: 
    #         dis, van = get_LoadBalance_expectedValue(consensus_date, d)  
    #         lb[l].append(dis/(van*l))
    
    # # print(lb)
    # plt.figure(figsize = (8,8))#set figure size 
    # plt.xlabel('Discount Value')
    # plt.ylabel('Expected Value')
    # plt.title('Expected Value of LoadBalance relative to Vanilla at diff network load' + consensus_date)
    
    # #plot each network load's LB 
    # for k in lb.keys():
    #     plt.plot(discount, lb[k], label = ("load: " + str(k)))
    # plt.plot(discount, performanceDecrease, marker = '.',label = "Performance Benchmark", color = "black")
    # plt.legend()
    
    # plt.savefig('expectLBdiffLoad.png')
    # get_expectVal_wdiffLoad(consensus_date)
    # get_LoadBalance_Matching(consensus_date, numClients, roacsv, [0.2,0.8,0.8])
    # print(get_LoadBalance_expectedValue(consensus_date, 0.8))
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


