from util import * 

import argparse
import sys
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

import pickle

def guards(relays):
    """
    input a list of relays and filter out non-guard relays, return a list of guards

    :param relays: (list) list of relay objects

    :return: (list) list of relay objects that all has the guard flag
    """
    guards = []
    for relay in relays:
        if relay.is_guard:
            guards.append(relay)
    return guards
def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", help="list of concensus to graph roa coverage")
    parser.add_argument("guards", help="graph just guards (y/n)")
    return parser.parse_args(args)
def main(args):
    args = parse_arguments(args)
    months = args.filenames.split(",")
    guardsOnly = False
    if args.guards == 'y':
        guardsOnly = True
    print("called func")
    graph_roa_multi_months(months, guardsOnly)
    
def graph_roa_multi_months(months, guardsOnly):
    

    """
    sample call:
    python graph_multi_months_roa.py "2022-08-13-00, 2022-09-13-00, 2022-10-13-00, 2022-11-13-00, 
    2022-11-13-00, 2022-12-13-00, 2023-01-13-00, 2023-02-13-00" n
    """
    v4Protected = []
    v4BWProtected = []
    v4ProtectedTight = []
    validROA = []
    p = os.getcwd()
    subpath = os.path.split(p)[0]
    for month in months:
        
        path = subpath + "/processed/" + month.strip() + "-processed.pickle"
        with open(path, 'rb') as f2:
            relays = pickle.load(f2)
        if guardsOnly:
            relays = guards(relays)
        bad_as_set = 0
        nw_bandwidth = 0
        v4_bw_invalid = 0
        v4_invalid = 0
        bad_pl = 0
        invalids = dict()
        bad_asn_and_pl = 0
        bad_asn = 0   
        v4_covered = 0
        v4_bw_covered = 0
        v4_mlpl = 0
        v4_mlpl_valid = 0
        num_relays = len(relays) 
        for relay in relays:
            # bandwidth, num guards
            # total up all bandwidth
            nw_bandwidth += relay.bw
            # ipv4 calculations
            # do the following if this relay has ipv4 roa
            if relay.ipv4_roa is not None and len(relay.ipv4_prefix) != 0 :  # roa = [net(IPv4Network), max length(str), prefix length(str), asn]

                pre_len = relay.ipv4_prefix.split('/')[1]
                # e.g. 142.4.192.0/19 the above code will get the number after "/"
                # max length 
                ml = relay.ipv4_roa[1]    # max length of ROA network
                pl = relay.ipv4_roa[2]    # prefix length of ROA network
                # check if invalid
                
                # check if there is an roa and its validity
                if len(relay.asn) > 1:
                    # relay.asn return a list supposedly with 1 entry which is the asn
                    # make sure the format is valid, inherented this format from get_prefix_and_asn() in util.py
                    print("invalid multi asn")
                    bad_as_set += 1
                    v4_invalid += 1
                    v4_bw_invalid += relay.bw

                elif relay.asn[0] != relay.ipv4_roa[3] and int(pre_len) > int(ml):
                    # compare asn obtained from requesting website and the roa file
                    # relay.asn[0] obtain from web, relay.ipv4_roa[3] obtained from ROA file
                    # relay.ipv4_roa =  [IPv4Network('142.4.192.0/19'), '19', '19', '16276']
                    #                   [net(IPv4Network), max length(str), prefix length(str), asn]
                    # check if prefix is longer than max length
                    # defining a max length would be vulnerable to a more specific BGP hijack?

                    print("invalid")
                    if relay.asn[0] in invalids:
                        invalids[relay.asn[0]][0] += 1
                    else:
                        invalids.setdefault(relay.asn[0], [1, 0, 0])
                    bad_asn_and_pl += 1
                    v4_invalid += 1
                    v4_bw_invalid += relay.bw
                    if ml == pl: v4_mlpl += 1
                elif relay.asn[0] != relay.ipv4_roa[3]:
                    # check if asn from website mathces the asn from roa csv file
                    print("invalid")
                    if relay.asn[0] in invalids:
                        invalids[relay.asn[0]][1] += 1
                    else:
                        invalids.setdefault(relay.asn[0], [0, 1, 0])
                    bad_asn += 1
                    v4_invalid += 1
                    v4_bw_invalid += relay.bw
                    if ml == pl: v4_mlpl += 1
                elif int(pre_len) > int(ml):
                    # check if prefix length greater than maximum length
                    print("invalid")
                    if relay.asn[0] in invalids:
                        invalids[relay.asn[0]][2] += 1
                    else:
                        invalids.setdefault(relay.asn[0], [0, 0, 1])
                    bad_pl += 1
                    v4_invalid += 1
                    v4_bw_invalid += relay.bw
                    if ml == pl: v4_mlpl += 1
                else:
                    # if both length is within max range and the asn matches from the 2 sources, it is a valid roa
                    print("valid roa")
                    v4_covered += 1
                    v4_bw_covered += relay.bw
                    # max length == prefix length
                    if ml == pl:
                        v4_mlpl += 1
                        v4_mlpl_valid += 1
                    # max length distribution
                    # see how many relay has the same max length setting

        v4Protected.append((v4_covered/num_relays)*100)
        v4BWProtected.append((v4_bw_covered/nw_bandwidth)*100)
        v4ProtectedTight.append((v4_mlpl/num_relays)*100)
        validROA.append((v4_covered/(v4_invalid+v4_covered))*100)
    plt.xlabel('Date')
    plt.ylabel('Percentage')
    
    x = range(len(months))
    if guardsOnly:
        plt.title("ROA Coverage for Guard Relays")
    else:
        plt.title("ROA Coverage for All Relays")
    print(len(v4Protected))
    plt.plot(x,v4Protected, label = "Percent IPv4 Protected Relay")
    plt.plot(x, v4BWProtected, label = "Percent Bandwidth IPv4 Protected Relay")
    plt.plot(x,v4ProtectedTight,label = "Percent IPv4 Protected Relay (Tight ml == pl)")
    plt.plot(x, validROA, label = "Percent of Valid ROA")
    plt.xticks(x, months, rotation ='vertical')
    plt.legend(bbox_to_anchor=(0, 1.02, 0.8, 0.3), loc="upper center", ncol=1)
    if guardsOnly:
        plt.savefig('GuardOnlyROACoverage.png',bbox_inches='tight')
    else:
        plt.savefig('AllRelaysROACoverage.png',bbox_inches='tight')
        
            
            
        
def check_client():
    file =  open('/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/typicalTOR1000Clients2023.pickle', 'rb') #open a file where a list of ASN with ROV is kept 
    clients = pickle.load(file)
    roarov = 0
    roa = 0
    rov = 0
    neither = 0
    for c in clients:
        if check_rov(c.AS.ASN) and c.roaCovered:
            roarov += 1
        elif check_rov(c.AS.ASN):
            rov += 1
        elif c.roaCovered:
            roa += 1
        else:
            neither += 1
    print("roarov, roa, rov, neither")
    print(roarov, roa, rov, neither)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))