import pickle
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from distributeUser import *
import pickle
from numpy import ones,vstack
from numpy.linalg import lstsq

UserPerCountry = {'US': 0.2429, 'RU': 0.1543, 'DE': 0.07980000000000001, 'NL': 0.040999999999999995, 'FR': 0.0346, 'ID': 0.0277, 'GB': 0.0256, 'IN': 0.0254, 'UA': 0.0215, 'LT': 0.0178}
countries = list(UserPerCountry.keys())
cweights = list(UserPerCountry.values())

#function that takes in an consensus file & discount value, then return the expected value for choosing an ROA covered guard
def get_Client_Coverage_ExpectedValue(consensus_date, discount):
    """
    find the expected value of choosing an ROA covered guard (ROAweight/totalWeight) given a specific consensus date and the discount applied to non_ROA guards. 
    

    :param consensus_date: (string) date of the consensus 
    :param discount: (float) discount to non_ROA guard so it gets less likely to be chosen 

    :return: ROAweight, total weight of relay with ROA, totalWeight, total weight of all relays 
    """
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
    """
    tallies up the weight using the vanilla calculation and again using the discount calculation. 
    The expected load balance will be discountWeight/vanillaWeight. 

    
    :param consensus_date: (string) date of the consensus 
    :param discount: (float) discount to non_ROA guard so it gets less likely to be chosen 

    :return: discountWeight, total weight of relay with discount mutiplier, vanillaWeight, total weight of all relays using vanilla calculation
    """
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
    """
    Tallies up weight in consensus using vanilla calculation as a reference point.
    Then, each client in the list tallies up the weight in their coverage status. The result of indivudual 
    client's weight in divided by the vanilla weight, which forms each client's individual 
    load balance. The average load balance is calculated by taking the mean of each client's individual 
    load balance. 

    :param consensus_date: (string) date of the consensus 
    :param clientsFileName: (string) path to the pickled file with clients 
    :param roacsv: (string) path to the .csv file storing roa information (e.g. home/tor-rpki/20200913.csv)
    :param discountParams: (list) list containing the 3 param for matching: [rovDiscount, roaDiscount, neitherDiscount]

    return: prints out the expected value for load balance

    """
    #get the weight of relays assigned by all clients 
    #average all of client weight / vanilla weight 
    rovDiscount = discountParams[0]
    roaDiscount = discountParams[1]
    neitherDiscount = discountParams[2]
    
    with open(clientsFileName, 'rb') as f:
        clients = pickle.load(f)

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
    for pg in gs:
        if pg.is_exit:  # if pg is an exit
            if pg.ipv4_roa != None:
                w = int(pg.bw * WGD)  # wgd, g+e in g position
            else:
                w = int(pg.bw * WGD)
        else:
            if pg.ipv4_roa != None:
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
                if pg.ipv4_roa != None:
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
                if check_rov(pg.asn):
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
    """
    graph the load balance with different network load using get_LoadBalance_Matching() 

    :param consensus_date: (string) date of the consensus 

    :return: graph of load balance with different network load 

    """
    discount = np.linspace(0.5,1,25)

    load = [ 0.8, 0.9, 1] # list of different network load 
    lb = {0.8:[],0.9:[], 1:[]} #load balance for each network load 

    performanceDecrease = [1]*25 #bound where mathcing performance is worse than vanilla 
    for l in load:
        
        for d in discount: 
            dis, van = get_LoadBalance_expectedValue(consensus_date, d)  
            lb[l].append(dis/(van*l))
    
    # print(lb) 
    formatlb = {0.8:[[], []], 0.9:[[], []], 1:[[], []]}
    for l in load:
        print(lb[l][0])
        points = [(discount[0],lb[l][0]),( discount[1],lb[l][1])]
        x_coords, y_coords = zip(*points)
        A = vstack([x_coords,ones(len(x_coords))]).T
        m, c = lstsq(A, y_coords)[0]
        print(m,c)
        for y in range(len(lb[l])):
            if lb[l][y] < 1:
                formatlb[l][0].append(discount[y])
                formatlb[l][1].append(lb[l][y])
            else:
                x = (1-c)/m
                formatlb[l][0].append(x)
                formatlb[l][1].append(1)
                break
    print(formatlb[0.8])
    print(lb[0.8])

    # print(lb)
    plt.figure(figsize = (8,8))#set figure size 
    plt.xlabel('Discount Value')
    plt.ylabel('Expected Value')
    plt.title('Expected Value of LoadBalance relative to Vanilla at Different Network Load' + consensus_date)
    
    #plot each network load's LB 
    for l in load:
        plt.plot(formatlb[l][0], formatlb[l][1], label = ("load: " + str(l)))
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
    # get_LoadBalance_Matching(consensus_date, numClients, roacsv, [0.1,0.1,1])
    get_expectVal_wdiffLoad(consensus_date)
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


