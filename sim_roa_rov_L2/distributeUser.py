import random 
from utilExit    import *
import pickle
import ipaddress

#downloaded here:https://metrics.torproject.org/userstats-relay-table.html?start=2021-05-12&end=2021-08-10
UserPerCountry = {'US': 0.2429, 'RU': 0.1543, 'DE': 0.07980000000000001, 'NL': 0.040999999999999995, 'FR': 0.0346, 'ID': 0.0277, 'GB': 0.0256, 'IN': 0.0254, 'UA': 0.0215, 'LT': 0.0178}
countries = list(UserPerCountry.keys())
cweights = list(UserPerCountry.values())


def get_prefix_addresses_map():
    #maps prefix e.g. /19, /18, to the number of possible client within this prefix 
    #/32 -> 0 client 
    prefixMap = dict()
    for i in range(0,33):
        if 2**(32-i) - 2 > 0:
            prefixMap[i] = 2**(32-i) -2
        elif i == 32:
            prefixMap[i] = 0
        elif i == 30 or i == 31:
            prefixMap[i] = 2
    return prefixMap

def get_roas(filename):
    '''get roas from csv file
    returns lists of lists
    [ip, max length, prefix length, asn]
    '''
    # read csv file
    ipv4s = []
    with open(filename, 'r') as f:
        csvreader = csv.reader(f)
        # skip fields
        next(csvreader)
        # append ip to roas list
        for row in csvreader:
            try:
                ipv4 = ipaddress.IPv4Network(row[1])
                maxlen = row[2]
                prefixlen = row[1].split('/')[1]
                #to account for different ROA file format
                if 'AS' not in row[0]:
                    asn = row[0]
                else:
                    asn = row[2:]
                ipv4s.append([ipv4, maxlen, prefixlen, asn])
            except ipaddress.AddressValueError: 
                #ignore cases where the address is ipv6 
                continue



    return ipv4s

def coverage_dict(roas, ipv4s, make_pickle=False):
    '''

    if make_pickle = True, creates coveragev4.pickle and coveragev6.pickle to be used in update_consensus_pickle
    '''
    # get ROA nets
    v4nets = get_roas(roas) # [ip network obj, maxlen, prefixlen, asn]
    # set up coverage dicts
    v4coverage = dict()

    # loop through all ip addresses
    for ip in ipv4s:
        ip_addr = ipaddress.IPv4Address(ip)
        v4coverage.setdefault(ip, None)
        for net in v4nets:
            if ip_addr in net[0]:
                v4coverage[ip] = net
                break

    if make_pickle:
        with open('coverage.pickle', 'wb') as f_cd1:
            pickle.dump(v4coverage, f_cd1)
    return v4coverage



def assignCountry(numUsers, countries, cweights, selection_algo):
    chosenCountry =  random.choices(countries, weights = cweights, k =  numUsers) #choose country based on tor's user / country data weight
    clientList  =[] # list populated with client obj filled in with origin 

    #iterate through all chosen client location and create new client obj
    for i in chosenCountry:
        newClient = Client(selection_algo)
        newClient.origin = i
        clientList.append(newClient)
    return clientList

def assignASN(numUsers, countries, cweights, selection_algo, roaFile, make_pickle = True):


    prefixHosts = get_prefix_addresses_map() # prefix -> number of ip address
    clientList = assignCountry(numUsers, countries, cweights, selection_algo)
    ASdict = dict() #country -> list of AS object
    weightdict = dict() # country -> weight of each AS
 
    ClientListwASN = [] #resulting list of clients that has the ASN filled in 
    
    specs = [0,0,0,0] #roa_rov, roa, rov, neither

        
    #iterate through pickled file and group ASN by country and populate 2 dict
    #ASdict: origin-> list of AS
    #weightdict: origin -> number of IPv4 each AS announce (acts as the weight of the random selection)
    file =  open('ASNnumIP.pickle', 'rb')
    numIPdict = pickle.load(file) # open pickled file, ASN -> AS object with numIPv4 filled in 
    file.close()
    for i in numIPdict: 
        if numIPdict[i].origin not in ASdict.keys():
            ASdict[numIPdict[i].origin] = [numIPdict[i]] 
            weightdict[numIPdict[i].origin] = [numIPdict[i].numIPv4]
        else:
            ASdict[numIPdict[i].origin].append(numIPdict[i])
            weightdict[numIPdict[i].origin].append(numIPdict[i].numIPv4)
    #iterate through clientList chose from assignCountry, randomly chose an ASN within that country 
    ipv4s = []
    for c in clientList:
        c.AS = random.choices(ASdict[c.origin], weights = weightdict[c.origin], k = 1)[0]
        prefixWeights = []
        for i in c.AS.prefixes:
            prefix = i.split('/')[1]
            prefixWeights.append(prefixHosts[int(prefix)])
  
        IPaddressPrefix = random.choices(c.AS.prefixes, weights = prefixWeights, k  = 1)
        IP = IPaddressPrefix[0].split('/')[0].split(".")
        prefix = int(IPaddressPrefix[0].split('/')[1])
        ipBin = ""
        for oct in IP:
            ipBin += '{0:08b}'.format(int(oct))
        choiceBitslen = 32- prefix
        choiceBits = ""
        resultIPBin = ""
        while resultIPBin == "":
            for i in range(choiceBitslen):
                choiceBits += str(random.choices([0,1], k = 1)[0]) 
            if choiceBits != "1"*choiceBitslen or choiceBits != "0"*choiceBitslen:
                resultIPBin = ipBin[0:prefix] + choiceBits
        resultIP = str(int(resultIPBin[0:8], 2)) + '.' + str(int(resultIPBin[8:16], 2)) + '.' + str(int(resultIPBin[16:24], 2)) + '.' + str(int(resultIPBin[24:32], 2))
        c.ipaddress = resultIP
        ipv4s.append(c.ipaddress)
        c.prefix = IPaddressPrefix
        ClientListwASN.append(c)
    

    #get coverage dict from the roa csv file 
    if make_pickle == True:
        cdict = coverage_dict(roaFile, ipv4s, make_pickle=True)
    else:
        file = open('coverage.pickle', 'rb')
        cdict = pickle.load(file)
    

    #specs = [0,0,0,0] #roa_rov, roa, rov, neither
    #iterate through the clients 
    for c in ClientListwASN:
        #get the roa entry from csv from coverage dict which returns ip -> [ip network obj, maxlen, prefixlen, asn]
        c.roa = cdict[c.ipaddress]

        #if roa does not exist then its not covered 
        if c.roa == None:
            c.roaCovered = False
            if check_rov(c.AS.ASN):
                specs[2] += 1
            else:
                specs[3] += 1
        #if the asn announced does not match the asn from roa file the its invalid or if the prefix annouunced is more specific than the roa specified it is invalid 
        elif c.AS.ASN != c.roa[3] or c.roa[1] < c.prefix[0].split('/')[1]:
            c.roaCovered = False
            if check_rov(c.AS.ASN):
                specs[2] += 1
            else:
                specs[3] += 1
        #otherwise it is covered 
        else:
            c.roaCovered = True
            if check_rov(c.AS.ASN):
                specs[0] += 1
            else:
                specs[1] += 1

    return ClientListwASN, specs




def check_roa_pre(roaFile):
    roaDict = dict() #asn -> [ip prefix covered] 
    for i in range(1,256):
        roaDict[str(i)] = []
    with open(roaFile) as f1:
        f1.readline()
        for line in f1:
            line = line.split(',')
            if ":" not in line[1]:
                roaDict[line[1].split('.')[0]].append([int(line[0]), ipaddress.IPv4Network(line[1]), int(line[2])])
    
    return roaDict

def check_roa(client, roaDict):

    prefixes = roaDict[client.ipaddress.split('.')[0]]

    for prefix in prefixes:
        # print(client.ipaddress)
        if ipaddress.IPv4Address(client.ipaddress) in prefix[1]:
            if int(client.AS.ASN) == prefix[0] and int(client.prefix[0].split('/')[1]) <= prefix[2]:
                return True
            else:
                return False
     
    return False

def check_roa_debug(cip, cASN, cprefix, roaDict):

    prefixes = roaDict[cip.split('.')[0]]

    for prefix in prefixes:
        # print(client.ipaddress)
        if ipaddress.IPv4Address(cip) in prefix[1]:
            if int(cASN) == prefix[0] and int(cprefix.split('/')[1]) <= prefix[2]:
                return True
            else:
                return False
     
    return False

def get_user_wASN(numUsers, countries, cweights, selection_algo):


    prefixHosts = get_prefix_addresses_map() # prefix -> number of ip address
    clientList = assignCountry(numUsers, countries, cweights, selection_algo)
    ASdict = dict() #country -> list of AS object
    weightdict = dict() # country -> weight of each AS
    file =  open('ASNnumIP.pickle', 'rb')
    numIPdict = pickle.load(file) # open pickled file, ASN -> AS object with numIPv4 filled in 
    ClientListwASN = [] #resulting list of clients that has the ASN filled in 
    file.close()
    specs = [0,0,0,0] #roa_rov, roa, rov, neither

        
    #iterate through pickled file and group ASN by country and populate 2 dict
    #ASdict: origin-> list of AS
    #weightdict: origin -> number of IPv4 each AS announce (acts as the weight of the random selection)
    for i in numIPdict: 
        if numIPdict[i].origin not in ASdict.keys():
            ASdict[numIPdict[i].origin] = [numIPdict[i]] 
            weightdict[numIPdict[i].origin] = [numIPdict[i].numIPv4]
        else:
            ASdict[numIPdict[i].origin].append(numIPdict[i])
            weightdict[numIPdict[i].origin].append(numIPdict[i].numIPv4)
    #iterate through clientList chose from assignCountry, randomly chose an ASN within that country 
    ipv4s = []
    for c in clientList:
        c.AS = random.choices(ASdict[c.origin], weights = weightdict[c.origin], k = 1)[0]
        prefixWeights = []
        for i in c.AS.prefixes:
            prefix = i.split('/')[1]
            prefixWeights.append(prefixHosts[int(prefix)])
  
        IPaddressPrefix = random.choices(c.AS.prefixes, weights = prefixWeights, k  = 1)
        IP = IPaddressPrefix[0].split('/')[0].split(".")
        prefix = int(IPaddressPrefix[0].split('/')[1])
        ipBin = ""
        for oct in IP:
            ipBin += '{0:08b}'.format(int(oct))
        choiceBitslen = 32- prefix
        choiceBits = ""
        resultIPBin = ""
        while resultIPBin == "":
            for i in range(choiceBitslen):
                choiceBits += str(random.choices([0,1], k = 1)[0]) 
            if choiceBits != "1"*choiceBitslen or choiceBits != "0"*choiceBitslen:
                resultIPBin = ipBin[0:prefix] + choiceBits
        resultIP = str(int(resultIPBin[0:8], 2)) + '.' + str(int(resultIPBin[8:16], 2)) + '.' + str(int(resultIPBin[16:24], 2)) + '.' + str(int(resultIPBin[24:32], 2))
        c.ipaddress = resultIP
        ipv4s.append(c.ipaddress)
        c.prefix = IPaddressPrefix
        ClientListwASN.append(c)
    return ClientListwASN

def user_specified_client(roa, rov, roa_rov, neither, numClients, select_algo, roaFile):
    numClients = round(numClients * 1.3)
    clients = get_user_wASN(numClients, countries, cweights, select_algo )
    roaDict = check_roa_pre(roaFile)
    croa = 0
    crov = 0
    croa_rov = 0
    cneither = 0
    resultClientList = []
    for c in clients:
        if check_roa(c, roaDict) and check_rov(c.AS.ASN) and croa_rov < roa_rov:
            croa_rov += 1 
            resultClientList.append(c)
        elif check_roa(c, roaDict) and croa < roa:
            croa += 1
            resultClientList.append(c)
        elif check_rov(c.AS.ASN) and crov < rov:
            crov += 1
            resultClientList.append(c)
        elif cneither < neither:
            cneither += 1
            resultClientList.append(c)
        if croa == roa and crov == rov and croa_rov == roa_rov and cneither == neither:
            return resultClientList

    print("finish intiail round of selection clients")
    while croa < roa:
        client = get_user_wASN(1, countries, cweights, select_algo)[0]
        if check_roa(client, roaDict) and not check_rov(client.AS.ASN):
            croa += 1 
            resultClientList.append(client)
    while crov < rov:
        client = get_user_wASN(1, countries, cweights, select_algo)[0]
        if check_rov(client.AS.ASN) and not check_roa(client, roaDict):
            crov += 1 
            resultClientList.append(client)
    while croa_rov < roa_rov:
        client = get_user_wASN(1, countries, cweights, select_algo)[0]
        if check_roa(client, roaDict) and check_rov(client.AS.ASN):
            croa_rov += 1 
            resultClientList.append(client)
    while cneither < neither:
        client = get_user_wASN(1, countries, cweights, select_algo)[0]
        if not check_roa(client, roaDict) and not check_rov(client.AS.ASN):
            cneither += 1 
            resultClientList.append(client)

    return resultClientList 


def user_specified_client2(roa, rov, roa_rov, neither, numClients, select_algo, csvfile):
    global cweights
    global countries
    #pull in country data as global variable 


    resultClientList = []


    prefixHosts = get_prefix_addresses_map() # prefix -> number of ip address
    total = roa + rov + roa_rov + neither

    #round the number of client needed for each category 
    roa = round(numClients * (roa/total))
    rov = round(numClients * (rov/total))
    roa_rov = round(numClients * (roa_rov/total))
    neither = round(numClients * (neither/total))

    #current number of clients for each category 
    croa = 0
    crov = 0
    croa_rov = 0
    cneither = 0

    ASdict = dict()
    #country -> [list of AS obj] 
    weightdict = dict()
    #country -> [list of number of ipv4 address]

    file =  open('ASNnumIP.pickle', 'rb')
    numIPdict = pickle.load(file) # open pickled file, ASN -> AS object with numIPv4 filled in 
    file.close()

    roaDict = check_roa_pre(csvfile) #dict for checking roa 

    for i in numIPdict: 
        if numIPdict[i].origin not in ASdict.keys():
            ASdict[numIPdict[i].origin] = [numIPdict[i]]
            #country -> [list of AS obj] 
            weightdict[numIPdict[i].origin] = [numIPdict[i].numIPv4]
            #country -> [list of number of ipv4 address] corrsponding to the ASdict order

        else:
            ASdict[numIPdict[i].origin].append(numIPdict[i])
            weightdict[numIPdict[i].origin].append(numIPdict[i].numIPv4)
        
    while croa < roa or crov < rov or croa_rov < roa_rov or cneither < neither:
        #make new client obj
        c = Client(select_algo)
        #assign origin to client 
        c.origin =  random.choices(countries, weights = cweights, k = 1)[0]
     
        #assign AS to client 
        c.AS = random.choices(ASdict[c.origin], weights = weightdict[c.origin], k = 1)[0]
        
        #if an AS has multiple prefix, assign client to AS based on number of clients
        #available in the AS 
        prefixWeights = []
        for i in c.AS.prefixes:
            prefix = i.split('/')[1]
            prefixWeights.append(prefixHosts[int(prefix)])
  
        IPaddressPrefix = random.choices(c.AS.prefixes, weights = prefixWeights, k  = 1)
        IP = IPaddressPrefix[0].split('/')[0].split(".")
        prefix = int(IPaddressPrefix[0].split('/')[1])
        ipBin = ""
        for oct in IP:
            ipBin += '{0:08b}'.format(int(oct))
        choiceBitslen = 32- prefix
        choiceBits = ""
        resultIPBin = ""
        while resultIPBin == "":
            for i in range(choiceBitslen):
                choiceBits += str(random.choices([0,1], k = 1)[0]) 
            if choiceBits != "1"*choiceBitslen or choiceBits != "0"*choiceBitslen:
                resultIPBin = ipBin[0:prefix] + choiceBits
        resultIP = str(int(resultIPBin[0:8], 2)) + '.' + str(int(resultIPBin[8:16], 2)) + '.' + str(int(resultIPBin[16:24], 2)) + '.' + str(int(resultIPBin[24:32], 2))
        c.ipaddress = resultIP
        c.prefix = IPaddressPrefix
        if check_roa(c, roaDict) and check_rov(c.AS.ASN):
            c.roaCovered = True
            if croa_rov < roa_rov:
                resultClientList.append(c)
                croa_rov += 1
        elif check_roa(c, roaDict):
            c.roaCovered = True
            if croa < roa:
                resultClientList.append(c)
                croa += 1
        elif check_rov(c.AS.ASN):
            c.roaCovered = False
            if crov < rov:
                resultClientList.append(c)
                crov += 1
        elif cneither < neither:
            c.roaCovered = False
            resultClientList.append(c)
            cneither += 1
    
    return resultClientList


# specifiedClients = user_specified_client2(208, 17, 7, 768, 1000, 'matching', '/home/siyang/research/tor-rpki/20200913.csv')
# with open("typicalTOR1000Clients.pickle", 'wb') as f:
#     pickle.dump(specifiedClients, f)
test = get_prefix_addresses_map()
print(test)