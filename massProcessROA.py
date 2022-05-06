from util import *
import sys
import argparse
import shutil
import time
import upgradeIpASNMap
import os
import csv

def get_roas(filename):
    '''parse roa file in .csv format, put each entry in a list, then append to a list containing all entries.
    each line in the file converts into [ipv4, maxlen, prefixlen, asn]

    :param filename: (string) name of the csv file to parse 
    :return: 2 lists of list for ipv4 and ipv6 addresses, entry in each list is [ipv4, maxlen, prefixlen, asn]
    ''' 
    # read csv file
    ipv4s = []
    ipv6s = []
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
                    asn = row[0][2:]
                ipv4s.append([ipv4, maxlen, prefixlen, asn])
            except ipaddress.AddressValueError:
                ipv6 = ipaddress.IPv6Network(row[1])
                maxlen = row[2]
                prefixlen = row[1].split('/')[1]
                if 'AS' not in row[0]:
                    asn = row[0]
                else:
                    asn = row[0][2:]
                ipv6s.append([ipv6, maxlen, prefixlen, asn])

    return ipv4s, ipv6s



def main():
    v4nets = []
    v6nets = []
    v4nets, v6nets = get_roas("/home/siyang/research/tor-rpki/20200913.csv")
    inputfile = open('/home/siyang/research/tor-rpki/testinput.csv', 'r')
    Lines = inputfile.readlines()

    for line in Lines: 
        ip_addr = ipaddress.IPv4Address(line[0:line.find("\n")])
        hasROA = False
        for roa in v4nets:
            if ip_addr in roa[0]:
                print("1")
                hasROA = True
                break
        if hasROA == False:
            print("0")




if __name__ == "__main__":
    main()