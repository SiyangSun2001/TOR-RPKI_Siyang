from util import *
import ipaddress
import re
import time


# map prefix to number of possible ipaddresses within this prefix
# return prefix -> num of ipv4 addresses 
def get_prefix_addresses_map():
    prefixMap = dict()
    for i in range(0,33):
        if 2**(32-i) - 2 > 0:
            prefixMap[i] = 2**(32-i) -2
        elif i == 32:
            prefixMap[i] = 0
        elif i == 30 or i == 31:
            prefixMap[i] = 2
    return prefixMap


# in put ip prefix and return the max and min addresses within this prefix 
def get_max_min(ipPrefix):
    range = [8,16,24,32] # used in the for loop below 

    ip  = ipPrefix.split('/')[0].split('.') #ip prefix before the slash and split between the dots 
    ipBin = '' #binary rep of the ip address
    prefix  = int(ipPrefix.split('/')[1]) # the prefix in int 

    #check if the prefix is 32, if it is 32 then there is no hosts and no max and mins 
    if prefix != 32:

        #get first part of ip prefix in binary form
        for oct in ip:
            ipBin += '{0:08b}'.format(int(oct))
            #got the above dec -> int operation from here: https://www.techiedelight.com/how-to-convert-an-integer-to-a-binary-string-in-python/
        

        temp = 0

        #max and min ip in binary form
        min = ipBin[0:prefix] + (32-prefix)*'0'
        max = ipBin[0:prefix] + (32-prefix)*'1'

        rmin = ''
        rmax = ''

        #get ip address in dot notation again 
        #convert ip address bin -> dotted
        for i in range:
            if i != 32:
                rmin += x + '.'
                rmax +=str(int(max[temp:i], 2)) + '.'
                temp = i
            else:
                rmin += str(int(min[temp:i], 2)+1) 
                rmax += str(int(max[temp:i], 2)-1)
        
        return ipaddress.IPv4Address(rmax), ipaddress.IPv4Address(rmin)
    else:
        return None, None

# function that calculates the difference between 2 ip addresses and tries to get the number of addresses in between 
#later found out its easier to just use the map to find num of ip addresses
def get_ip_difference(ip1, ip2):
    ip1 = ip1.split('.')
    ip2 = ip2.split('.')
    # split 2 addresses by the dot

    ip1Bin = ''
    for oct in ip1:
        ip1Bin += '{0:08b}'.format(int(oct))

    ip2Bin = ''
    for oct in ip2:
        ip2Bin += '{0:08b}'.format(int(oct))
    # get the 2 addresses in decimals

    diff = abs(int(ip2Bin, 2) - int(ip1Bin, 2)) 
    # get the difference between 2 addresses
    return diff


#discarded function, b/c does not account for multi-origin ip prefix 
def getAllAS():
    ASDict = dict()
    with open("/home/siyang/research/tor-rpki/demoRouteView.pfx2as") as tsv:

        prevASN = 0
        prevIP = {}
        prevNumIP = 0
        count  = 0
        for line in csv.reader(tsv, dialect = "excel-tab"):
            if count % 1000 == 0:
                print(count)
            if ',' not in line[2]:
                curASN = int(line[2])
            else:
                curASN = int(line[2].split(',')[0])
            if line[0] == '0':
                ASDict[prevASN].numIPv4 += prevNumIP
            elif "_" in line[2]:
                continue
            elif curASN == prevASN:
                i = set(ipaddress.IPv4Network(line[0] + '/' +  line[1]).hosts())
                prevIP = prevIP.union(i)
                prevNumIP = len(prevIP)
            else:
                i = set(ipaddress.IPv4Network(line[0] + '/' +  line[1]).hosts())
                if prevASN != 0:
                    ASDict[prevASN].numIPv4 += prevNumIP
                prevASN = curASN
                prevIP = i
                prevNumIP = len(i)
                if curASN not in ASDict.keys():
                    ASDict[curASN] = AS(ASN = curASN)

            count += 1
    return ASDict


#discarded function, too slow. uses python ipaddress library 
def getAllAS2():
    ASDict = dict()
    count =  0
    with open("/home/siyang/research/tor-rpki/demoRouteView.pfx2as") as tsv:
        for line in csv.reader(tsv, dialect = "excel-tab"):
            if count % 1000 == 0:
                print(count)
            count += 1
            curNetwork = set(ipaddress.IPv4Network(line[0] + '/' + line[1]).hosts())
            if ',' not in line[2] and '_' not in line[2]:
                curASN = line[2]
                # print(type(curASN))
                if curASN not in ASDict.keys():
                    ASDict[curASN] = AS(ASN  =curASN)
                if ASDict[curASN].prevNetwork == None:
                    ASDict[curASN].numIPv4 = len(curNetwork)
                    ASDict[curASN].prevNetwork = curNetwork
                else:
                    ASDict[curASN].numIPv4 += len(curNetwork.difference(ASDict[curASN].prevNetwork))
            else:
                ASNList = re.split(',|_' ,line[2])

                for i in ASNList:
                    curASN = i
                    if curASN not in ASDict.keys():
                        ASDict[curASN] = AS(ASN  = curASN)
                    if ASDict[curASN].prevNetwork == None:
                        ASDict[curASN].numIPv4 = len(curNetwork)
                        ASDict[curASN].prevNetwork = curNetwork
                    else:
                        ASDict[curASN].numIPv4 += len(curNetwork.difference(ASDict[curASN].prevNetwork))
    return ASDict

def getAllAS3():

    #get the prefix -> num of ip addresses map 
    prefix_hosts_map = get_prefix_addresses_map()

    #dictionary for storing result, ASN -> ASN object 
    ASDict = dict() 
    count = 0

    #open the route view data
    #IP address -> ASN map 
    #https://www.caida.org/catalog/datasets/routeviews-prefix2as/#H2838
    with open("/home/siyang/research/tor-rpki/routeviews-rv2-20210722-0200.pfx2as") as tsv:
        #retrieve the tab separated data 
        for line in csv.reader(tsv, dialect = "excel-tab"):

            #print the progress while running
            if count % 10000 == 0:
                print(count)
            count += 1
            
            #get the max and min of the current ip prefix 
            cmax, cmin = get_max_min(line[0] + '/' + line[1])

            #check to see if prefix is 32, b/c 32 does not have any addresses
            if cmax != None and cmin != None:

                #account for multi-origin prefix 
                ASNList = re.split(',|_' ,line[2])      

                for cASN in ASNList:
                    
                    #create new entry in dict if ASN does not exist, also assign numIPv4 and prevmax 
                    if cASN not in ASDict.keys():
                        ASDict[cASN] = AS( ASN = cASN)
                        ASDict[cASN].prevMax = cmax
                        ASDict[cASN].numIPv4 =  prefix_hosts_map[int(line[1])]
                        ASDict[cASN].prefixes.append(line[0] + '/' + line[1])
                    #compare with the prevMax address to avoid double counting. some entries are just more specific than previous entries 
                    if cmin > ASDict[cASN].prevMax:
                        #if the prev entry doesnt contain current entry, add the num of hosts into the numIPv4 field 
                        ASDict[cASN].numIPv4 +=  prefix_hosts_map[int(line[1])]
            else:
                continue


    return ASDict

def preprocess_asn_origin():
    orgID_origin = dict()
    #map orginzation id to origin country
    #https://www.caida.org/catalog/datasets/as-organizations/
    asn_orgID  =dict()
    
    with open('/home/siyang/research/tor-rpki/20210701.as-org2info.txt') as f1:
        for line in f1:
            if not (line.startswith("#")):
                tempList = line.split('|')
               
                if '-' in tempList[0]:
                    orgID_origin[tempList[0]] = tempList[-2]
                else:
                    asn_orgID[tempList[0]] = tempList[3]
    return asn_orgID, orgID_origin

def get_origin(asn_orgID, orgID_origin, ASNnumIP):
    for asn in ASNnumIP.keys():
        try:
            ASNnumIP[asn].origin = orgID_origin[asn_orgID[asn]]
        except KeyError:
            ASNnumIP[asn].origin = 'NA'
    return ASNnumIP

def main():
    start2 = time.perf_counter()
    ASNnumIP = getAllAS3()
    end2 = time.perf_counter()


    print('takes ', (end2 - start2), 'secs to tally up number of ip address each ASN announces')

    asn_orgID, orgID_origin = preprocess_asn_origin()
    result_dict = get_origin(asn_orgID, orgID_origin, ASNnumIP)
    with open('ASNnumIP.pickle', 'wb') as pf:
        pickle.dump(result_dict, pf)


if __name__ == "__main__":
    main()
