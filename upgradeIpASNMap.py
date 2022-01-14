from datetime import datetime, timedelta
import time
import csv
import os
import pickle
import ipaddress
import json
import requests
import urllib
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import csv





#original method of getting ASN from ip address 
def get_prefix_and_asn(ip):
    """
    old method of getting prefix and asn given ip, currently uses routeview data and searches offline
    see get_prefix_and_asn_local(ip) for new method in preprocess_consensus.py
    
    :param ip: (str) ip address in string format

    :return: (list) returns a list containing prefix and ASN of the ip address 

    """
    base_url = "https://stat.ripe.net/data/network-info/data.json?resource="
    url = base_url + ip
    try:
        response = urllib.request.urlopen(url).read()
    except requests.HTTPError as exception:
        print("errrrrrror")
        print(exception, 11111)
    data = json.loads(response)
    return data['data']['prefix'], data['data']['asns']



def preprocess_get_prefix_asn_local_v4():
    """
    preprocess the route view data
    return 2 dict: map_dict is the routeviews file in dictionary format: ip network -> asn 
    quick_dict: created to improve run time, first octet of the ip prefix -> index in the file 
    so only need to look at the first octet and beyond for a certain address ( assuming no asn annouces a prefix broader than /8)

    :return: (dict) 2 dictionary, ip network -> asn and ip prefix -> index

    """
    print("running v4 pre!!!")
    map_dict = dict() #store each entry of routeview data, ip network -> asn 
    quick_dict = dict() #store starting index of each octet 
    routeviewFile = "routeviews-rv2-20210722-0200.pfx2as"
    with open(routeviewFile) as tsv:
        count = 0
        num = 1
        quick_dict[num] = count
        for line in csv.reader(tsv, dialect = "excel-tab"):
            #iterate through each line in routeview data
            v4Network = ipaddress.IPv4Network(line[0] + '/' + line[1])
            map_dict[v4Network] = line[2] #network -> ASN 
            if int(line[0].split('.')[0]) != num:
                num += 1
                quick_dict[num] = count

            count += 1

    return map_dict, quick_dict



def get_prefix_and_asn_local_v4(qDict, mapdict, ipstr):

    """
    input the 2 required dict and an IP address, return the prefix and asn 
    first dictionary decide which line to start looking by mapping the 1st octet to the index 
    in routeview file, than iterate through one by one to see 
    which asn annouces a prefix containing the ip address we are looking for 

    :praram qDict: (dict) indirect dictionary to get starting index in mapdict 
    :param mapdict: (dict) dictionary containing network -> asn 
    :param ipstr: (string) ip address we are searching in string format 

    """
    ip = ipaddress.IPv4Address(ipstr) #convert ip address in string into Ipaddress object
    foundFirst = False #need to ignore the comparison with previous found, if its first round 
    start_index  = qDict[int(ipstr.split('.')[0])] #get the starting index from the indirect dictionary
    key_list = list(mapdict.keys()) #get list of all ip network

    while start_index < len(mapdict.keys()):
        #go through all ip network, find the one that fits and also has the biggest prefix
        n = key_list[start_index]
        #if did not yet found the first fit, do not check to check previous result to see if the network has passed the ip address
        if foundFirst == False:
            if ip in n:
                foundFirst = True
                tempFound = n
        else:
            #if fits store in tempFound
            if ip in n:
                tempFound = n
            else:
                #if doesnt fit check if the network has gone out of range 
                if type(n.hosts()) == list:
                    bound = n.hosts()[0]
                    #get the first host 
                else:
                    if len(list(n.hosts())) != 0:
                        bound  = next(n.hosts())
                    else:
                        #case of /32 only 1 host 
                        bound = ip
                #break loop if out of bound, tempfound becomes the tightest fit 
                if bound > ip:
                    break
        start_index += 1

    try:
        if '_' in mapdict[tempFound]:
            asn = mapdict[tempFound].split('_')
        else:
            asn = [mapdict[tempFound]]
        return tempFound.exploded, asn
    except:
        return '', []


#ipv6 version of the above methods
def preprocess_get_prefix_asn_local_v6():
    """
    same logic and process as the v4 version 
    """
    print("runniong v6 pre")
    map_dict = dict()
    quick_dict = dict()
    with open("routeviews-rv6-20210701-1200.pfx2as") as tsv:
        count = 0
        num = '2001'
        quick_dict[num] = count
        for line in csv.reader(tsv, dialect = "excel-tab"):
            map_dict[ipaddress.IPv6Network(line[0] + '/' + line[1])] = line[2]
            if str(line[0].split(':')[0]) != num:
                num = line[0].split(':')[0]
                quick_dict[num] = count

            count += 1

    return map_dict, quick_dict

#ipv6 version of the above methods 
def get_prefix_and_asn_local_v6(qDict, mapdict, ipstr):
    """
    same logic and process as the v4 version 
    """

    ip = ipaddress.IPv6Address(ipstr)
    foundFirst = False
    start_index  = qDict[ipstr.split(':')[0]] #first 4 digit of ipv6 address 

    #mapdict: maps ipv6 network to ASN
    key_list = list(mapdict.keys())
    #keylist has a list of ipv6 network 
    while start_index < len(mapdict.keys()):
        # print(start_index)
        #get the first ipv6 network in this first 4 digit
        n = key_list[start_index]
        # print(n.exploded)
        if foundFirst == False:
            # print("got in while")
            if ip in n:
                foundFirst = True
                tempFound = n
        else:
            if ip in n:
                tempFound = n
            else:
                # print("assign bound")
                if type(n.hosts()) == list:
                    # print("got in 1")
                    bound = n.hosts()[0]
                else:
                    # print("got in 2")
                    try:
                        bound  = next(n.hosts())
                    except:
                        bound = ip
                if bound > ip:
                    # print("got in 3")
                    break
                
        start_index += 1

    try:
        if '_' in mapdict[tempFound]:
            asn = mapdict[tempFound].split('_')
        else:
            asn = [mapdict[tempFound]]
        return tempFound.exploded, asn
    except:
        return '', []




#method used to compare the current method v.s. the old method of requesting an online database for every ip address
def compareLvI(ips):
    """
    testing function to check the difference between searching locally v.s. online 
    """
    print("start comparing")
    global v6QUICKDICT
    global v6MAPDICT
    global v4QUICKDICT
    global v4MAPDICT

    count  = 0
    for ip in ips:
        if count % 100 == 0:
            print("running at ", count)
        prefix, asn = get_prefix_and_asn(ip)
        prefixL, asnL = get_prefix_and_asn_local(ip)
        if prefix != prefixL or asn != asnL:
            if len(asn) != 0:
                file1 = open("difference.txt","a")
                file1.write("\n " + 'local: ' + prefixL  + ' asn: ' + asnL[0] +  ' internet: ' + prefix + ' asn: ' + asn[0])
                file1.close()
                print("file closed")
            else:
                file1 = open("difference.txt", "a")
                file1.write("\n" + "local: " + prefixL + "asn: " + asnL[0] + "internet: " + prefix + "asn: " + "not found" )
                file1.close()
                print("file closed")
        count += 1


# map, quick = preprocess_get_prefix_asn_local_v6()
# map1, quick1 = preprocess_get_prefix_asn_local_v4()

# print(get_prefix_and_asn_local_v4(quick1, map1, "95.217.42.50"))
# print(get_prefix_and_asn_local_v6(quick, map, "2a01:4f9:2a:2e8d::c0de"))


