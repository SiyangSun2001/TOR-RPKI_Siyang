import pickle
import itertools
from itertools import permutations
from util import *
import copy
import statistics

#takes in parameter list and change each client's matching select algo's param 
#param list: [rovDiscount, roaDiscount, neitherDiscount]
def change_client_matching_param(paramls, clients):
    """
    helper function to change client's discount parameter

    :param paramls: list for the parameters: roa, rov, neither discount 
    """
    for c in clients:
        c.rovDiscount = paramls[0]
        c.roaDiscount = paramls[1]
        c.neitherDiscount = paramls[2]

#give the permutation of parameters, the pool is the possible value to choose from 
#repeat is the number if param to permutate. 
def get_param_Permutation(pool):
    """
    given the possible values and number of item in each choice, return all possible permutations

    :param pool: *iterable, list, set or string etc 

    :return: (list) a list of the all possible permutations  
    """

    result = []
    for j in itertools.product(pool, repeat=2) :
        result.append(list(j))

    return result
    


def get_LoadBalance_Matching_multiParam(consensus_date, ClientFile, paramPermutations):
    """
    run load balance simulation on same client file and consensus file, but each time the parameter for guard selection are different. 

    :param consensus_date: (string) date for the consensus file to be used in the simulation 
    :param ClientFile: (string) path to the client file used in simulation 
    :param paramPermutation: (list) list of all parameters used in this simulation, could generate using get_param_Permutation(pool)

    :return: (list) return a list of Load Balance result for each of the parameter, each entry has following format: [param, avgLB]
    """
    #get the weight of relays assigned by all clients 
    #average all of client weight / vanilla weight 



    #path for consensus file 
    p = '../processed/' + consensus_date + '-processed.pickle'

    #try to open the pickled file  
    try:
        file = open(p, 'rb')
    except FileNotFoundError:
        print(p, 'does not exist')

    #open client file 
    try:
        filec = open(ClientFile, 'rb')
    except FileNotFoundError:
        print(ClientFile, 'not found')
    clients = pickle.load(filec)
    numClients = len(clients)
    #get these from the consensus file, client independent, but date depedent 
    rs = pickle.load(file) #list of all relay objects
    WGD = pickle.load(file) #weight in the consensus
    WGG = pickle.load(file) #weight in the consensus
    file.close()
    filec.close()

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

    result_ls = [] 

    #check is each client has ROV coverage 
    for c in clients:
        if check_rov(c.AS.ASN):
            c.rovCovered = True
        else:
            c.rovCovered = False
    
    #check if each guard has rov coverage 
    for pg in gs:
        # some guard dont have asn 
        if pg.asn != None:
            pgASN = pg.asn[0]
        else:
            pgASN = None
        if check_rov(pgASN):
            pg.rovCovered = True
        else:
            pg.rovCovered = False
    
    count = 0
    #iterate through all params 
    for param in paramPermutations:
        print(count)
        ClientWeights = []
        roa = 0 
        rovROAROV = 0
        neither = 0
        for c in clients:
            weights = 0

            #rov and roaRov case 
            if c.rovCovered or (c.rovCovered and c.roaCovered == True): 
                rovROAROV += 1
                for pg in gs:
                    if pg.is_exit:
                        consensusWeight = WGD
                    else:
                        consensusWeight = WGG
                    if pg.ipv4_roa != None:
                        w = int(pg.bw * consensusWeight)
                    else:
                        w = int(pg.bw * consensusWeight)*param[0]
                    weights += w

            #ROA case
            elif c.roaCovered == True:
                roa += 1
                for pg in gs:
                    if pg.is_exit:
                        consensusWeight = WGD
                    else:
                        consensusWeight = WGG
                    if pg.rovCovered:
                        w = int(pg.bw * consensusWeight)
                    else: 
                        w = int(pg.bw * consensusWeight)*param[1]
                    weights += w

            #neither case, discount all relay with ROA or ROV by 0.1
            elif c.roaCovered == False and not c.rovCovered:
                neither += 1
                for pg in gs:
                    if pg.is_exit:
                        consensusWeight = WGD
                    else:
                        consensusWeight = WGG
                    if not pg.rovCovered and pg.ipv4_roa == None:
                        w = int(pg.bw * consensusWeight)
                    else:
                        w = int(pg.bw * consensusWeight)*param[2]
                    weights += w
            ClientWeights.append(weights)

        totalLB = 0
        for w in ClientWeights:
            totalLB += w/vanillaWeight
        #tally up the bandwidth each from each client's prospective 
        #take the average of the bandwidth
        avgLB = totalLB/numClients
        result_ls.append([param, avgLB])
        count += 1

    return result_ls

#get roa rov matching rate from multiple parameter 
def get_roarov_matching_multiParam(consensus_date, ClientFile, perm):
    """
    run ROA ROV matching simulation on same client file and consensus file, but each time the parameter for guard selection are different. 

    :param consensus_date: (string) date for the consensus file to be used in the simulation 
    :param ClientFile: (string) path to the client file used in simulation 
    :param perm: (list) list of all parameters used in this simulation, could generate using get_param_Permutation(pool)

    :return: (list) return a list of ROA ROV matching result for each of the parameter, each entry has following format: [param, percent of ROA ROV matching]
    """

    #open client file and prepare path to consensus 
    try:
        filec = open(ClientFile, 'rb')
    except FileNotFoundError:
        print(ClientFile, 'not found')
    clients = pickle.load(filec)
    p = os.getcwd()
    path = os.path.split(p)[0]
    path = path + '/rpkicoverage/processed/'
    consensus_date = consensus_date.split('-')
    

    #call on_consensus for every client, populate their guard list 

    p_roa_rov_covered = 0
    totalROV = 0
    #keep track of total rov and number of roa_rov matches

    t  = datetime(int(consensus_date[0]),int(consensus_date[1]),int(consensus_date[2]),int(consensus_date[3]))
    #assign each clients rov status 
    for c in clients:
        if check_rov(c.AS.ASN):
            c.rovCovered = True
        else:
            c.rovCovered = False

    resultls = []
    count = 0
    for p in perm:
        count += 1
        print(count)
        clientsCopy = copy.deepcopy(clients)
        load_consensus(path, consensus_date[0], consensus_date[1], consensus_date[2], consensus_date[3]) 
        #change the clients matching discount into current discount 
        change_client_matching_param(p, clientsCopy)
        p_roa_rov_covered = 0
        # totalROV = 0
        
   
        #call on consensus on copied client to populate their client list 
        for client in clientsCopy:
            client.on_consensus(t)

        
        for client in clientsCopy:
                #get clients roa 
                roa = client.guard_list[-1].ipv4_roa
                #get the asn of guard of current client 
                if client.guard_list[-1].asn != None:
                    guardASN = client.guard_list[-1].asn[0]
                else:
                    guardASN = None
                #see if either guard or 
                # if client.rovCovered:
                #     totalROV += 1
                # if  check_rov(guardASN):
                #     totalROV += 1
                
                #if client has rov, guard has roa, add 1 matched connection 
                if client.rovCovered and roa != None:
                    p_roa_rov_covered += 1 
                #if guard has rov and client has roa, add 1 to matched 
                elif check_rov(guardASN) and client.roaCovered:
                    p_roa_rov_covered += 1 
        resultls.append([p,p_roa_rov_covered/len(clientsCopy)])
    return resultls
    

#get the percent of client with a roa covered guard 
def get_proa_multiparam(consensus_date, ClientFile, perm):
    """
    run percent of client w/ ROA coverage simulation on same client file and consensus file, but each time the parameter for guard selection are different. 

    :param consensus_date: (string) date for the consensus file to be used in the simulation 
    :param ClientFile: (string) path to the client file used in simulation 
    :param perm: (list) list of all parameters used in this simulation, could generate using get_param_Permutation(pool)

    :return: (list) return a list of percent ROA coverage result for each of the parameter, each entry has following format: [param, %ROA covered]
    """
    #open client file and prepare path for consensus 
    try:
        filec = open(ClientFile, 'rb')
    except FileNotFoundError:
        print(ClientFile, 'not found')
    clients = pickle.load(filec)
    num_clients = len(clients)
    p = os.getcwd()
    path = os.path.split(p)[0]
    path = path + '/rpkicoverage/processed/'
    consensus_date = consensus_date.split('-')
    
    t  = datetime(int(consensus_date[0]),int(consensus_date[1]),int(consensus_date[2]),int(consensus_date[3]))
    #assign each clients rov status 
    for c in clients:
        if check_rov(c.AS.ASN):
            c.rovCovered = True
        else:
            c.rovCovered = False
    
    resultls = []
    count = 0

    #iterate through each permutation 
    for p in perm:
        count += 1
        print(count)
        #create deep copy of client object 
        clientsCopy = copy.deepcopy(clients)
        #load consensus and update gobal var in util file 
        load_consensus(path, consensus_date[0], consensus_date[1], consensus_date[2], consensus_date[3]) 

        #change the client's discount param 
        change_client_matching_param(p, clientsCopy)
        roa_covered = 0
        totalROV = 0

        #call on consensus on each client and populate their guard list 
        for client in clientsCopy:
            client.on_consensus(t)

        #go through all client and see if their guard has roa coverage 
        for client in clientsCopy:
                roa = client.guard_list[-1].ipv4_roa
                if roa != None:
                    roa_covered += 1 
   
        resultls.append([p,roa_covered/num_clients])
    return resultls

# perm = get_param_Permutation((0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9))
# print(len(perm))
# for i in perm:
#     i.append(1)

# ROA_ROVResult = get_roarov_matching_multiParam('2020-09-01-00', 'typicalTOR1000Clients.pickle', perm)
# with open("PermROA_ROVResult.pickle", 'wb') as f:
#     pickle.dump(ROA_ROVResult, f)
# print("finish roa rov")
# LB = get_LoadBalance_Matching_multiParam('2020-09-01-00', 'typicalTOR1000Clients.pickle', perm)
# with open("PermLBResult.pickle", 'wb') as f:
#     pickle.dump(LB, f)
# print("finish LB")
# pROA = get_proa_multiparam('2020-09-01-00', 'typicalTOR1000Clients.pickle', perm)
# with open("Perm_pROA_Result.pickle", 'wb') as f:
#     pickle.dump(pROA, f)

# print("finished")


#run a list of param multiple times and get their mean 
def param_multi_run(paramfname, repeat, fromPickle = True):
    """
    run each parameter in a list multiple times and get the mean of each parameter 

    :param paramfname: name to pickled parameter if fromPickle = True, else input a list of possible parameters 
    :param repeat: (int) number of time to repeat for each parameter 
    :param fromPickle: (boolean) true if select parameter list from pickled file, otherwise false 
    """
    if fromPickle:
        with open(paramfname, 'rb') as f:
            params = pickle.load(f)
    else:
        params = paramfname
    result = []
    for p in params:
        count = 0
        pROAls = []
        roaROVls = []
        LBls = []
        while count < repeat:
            pROA = get_proa_multiparam('2020-09-01-00', 'typicalTOR1000Clients.pickle', [p])
            roaROV = get_roarov_matching_multiParam('2020-09-01-00', 'typicalTOR1000Clients.pickle', [p])
            LB = get_LoadBalance_Matching_multiParam('2020-09-01-00', 'typicalTOR1000Clients.pickle', [p])
            pROAls.append(pROA[0][1])
            roaROVls.append(roaROV[0][1])
            LBls.append(LB[0][1])
            count += 1
        result.append([p,statistics.mean(pROAls), statistics.mean(roaROVls),statistics.mean(LBls) ])
    print(result)
    with open("qualifiedParam10runs.pickle", 'wb') as f2:
        pickle.dump(result, f2)


def get_consensus_data(file):
    """
    draw percent roa, ROA ROV match, ROV from a consensus file 

    :param file: path to consensus file 

    :return: print out the above specs on a consensus 
    """
    with open(file, 'rb') as f:
        rs = pickle.load(f) #list of all relay objects
        WGD = pickle.load(f) #weight in the consensus
        WGG = pickle.load(f) #weight in the consensus
        gs = [r for r in rs if r.is_guard]
    roa = 0
    roarov = 0
    rov = 0
    for g in gs:
        if g.asn != None:
            gasn = g.asn[0]
        else:
            gasn = None
        if check_rov(gasn) and g.ipv4_roa != None:
            roarov += 1
        elif check_rov(gasn):
            rov += 1
        elif g.ipv4_roa != None:
            roa += 1
    totalGuard = len(gs)
    print('percent roa:', roa/totalGuard)
    print('percent roa rov:', roarov/totalGuard)
    print('percent rov:', rov/totalGuard)

# param_multi_run([[1,1,1]], 10, fromPickle = False)
# get_consensus_data('/home/siyang/research/tor-rpki/processed/2020-09-01-00-processed.pickle')

