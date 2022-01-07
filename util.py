from datetime import datetime, timedelta
import csv
import os
import pickle
import ipaddress
import json
import requests
import urllib
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

class Relay:
    '''
    Relay Object to store information on each relay parsed from consensus file 
    stores the relay's ip, fingerprint etc. 
    '''
    def __init__(self, fp, ip):
        # relay info
        self.fp = fp #fingerprint of relay
        self.ip = ip #ip address of relay
        # fingerprint and ip passed in as param and assigned to the proper fields
        self.ipv6 = '' #ipv6 address
        self.bw = 0 #bandwidth
        self.is_guard = False # true if has guard flag in consensus 
        self.is_exit = False # true if has exit flag in consensus 
        # set all above fields to default val


        # preprocessing ROA coverage info
        self.asn = None #asn of the relay, found in routeview data
        self.ipv4_prefix = None #prefix found in routeview data 
        self.ipv4_roa = None   # if roa, = [net(IPv4Network), max length(str), prefix length(str), asn]
        #same info in ipv6
        self.ipv6_asn = None
        self.ipv6_prefix = None
        self.ipv6_roa = None 

        # persistently record
        self.sampled_on = datetime(1, 1, 1, 0)
        self.listed = True
        self.unlisted_since = datetime(1, 1, 1, 0)
        # set time object to default value

    # define equal function as if 2 relay has same fingerprint they are the same
    def __eq__(self, other):
        """
        comparison function to see if 2 relay object are the same through
        comparing their fingerprint 
        """
        return self.fp == other.fp

    # toString function returns the fingerprint
    def __str__(self):
        """
        return the fingerprint of relay
        """
        return self.fp

    # hash function hashes the fp to an integer
    def __hash__(self):
        """
        hash relay through their fingerprint
        """
        return hash(self.fp)


def datespan(start_date, end_date, delta=timedelta(hours=1)):
    '''
    Function to iterate through each hour in a given timespan and out put each iteraton

    :param start_date: (datetime object) start date of the duration
    :param end_date: (datetime object) end date of the duration
    :param delta: (timedelta) the interval of each iteration, default to 1 hour
    '''
    # e.g. 8:30 -> 9:30 ->10:30 until the specified end time
    # from https://stackoverflow.com/questions/153584/how-to-iterate-over-a-timespan-after-days-hours-weeks-and-months
    current_date = start_date
    while current_date < end_date:
        yield current_date
        #outputs current date each cycle before reaching the end date
        # yield key word: outputs the value of cd each cycle but carries on from where it left off
        # do not have to store a huge list in memory before processing
        current_date += delta
        # add the amount of time between each iteration


def get_all_ips(start_date, end_date):
    """
    get all ip addresses of relays in a duration of consensus files, draw data from the archive_pickle folder

    :param start_date: (datetime object) start date of the duration 
    :param end_date: (datetime object) end date of the duration 

    :return: (set) return 2 sets containing ip address, for IPv4 and IPv6 addresses 
    """
    #sets storing the ip addresses 
    all_ipv4s = set()
    all_ipv6s = set()
    #path where we obtain the data 
    p = os.getcwd()
    path = p + '/archive_pickles/'
    #iterate through a duration of date 
    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
        #get the relay list 
        rs, wgd, wgg = load_consensus(path, t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), t.strftime('%H'))
        if rs:
            ipv4s = [r.ip for r in rs]
            # short hand way of for loop, append r.ip to ipv4s list
            ipv6s = [r.ipv6 for r in rs if r.ipv6 != '']
            # append r.ipv6 to ipv6s if r.ipv6 is not empty string
            all_ipv4s.update(ipv4s)
            # update func adds all entry in ipv4s into the set
            all_ipv6s.update(ipv6s)
    return all_ipv4s, all_ipv6s


def load_consensus(p, year, month, date, hour):
    """
    (same as the function in process_consensus.py)
    pulls list of relay object, weight info (wgd, wgg) from pickled file

    :param p: (str) path of pickle directory 
    :param year: (str) year of the consensus
    :param month: (str) month of the consensus
    :param date: (str) date of the consensus
    :param hour: (str) hour of the consensus

    :return: list of relay objects, wgd, wgg
    """
    # load .pickle file
    filename = p + year + '-' + month + '-' + date + '-' + hour + '.pickle'
    try:
        file = open(filename, 'rb')
        rs = pickle.load(file)
        wgd = pickle.load(file)
        wgg = pickle.load(file)
        return rs, wgd, wgg
    # if it doesn't exist
    except FileNotFoundError:
        print('Consensus for ' + year + '-' + month + '-' + date + '-' + hour + ' doesn\'t exist.')
        return [], 0, 0


def recent_relays_hour(year, month, date, hour):
    """
    Gets relays info from one consensus file (one hour duration)

    :param year: (str) year
    :param month: (str) month
    :param date: (str) date
    :param hour: (str) hour

    :return: (list) list of relays objects 
    """
    baseurl = 'https://collector.torproject.org/recent/relay-descriptors/consensuses/'
    # this above url is the TOR consensus website
    url = baseurl + year + '-' + month + '-' + date + '-' + hour + '-00-00-consensus'
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'lxml')
    text = soup.get_text().split('\n')
    rs = []
    for line in text:
        # Bandwidth weights for this consensus
        if line.startswith('bandwidth-weights'):
            bw_info = line.split()
            wgd = (int(bw_info[12].split('=')[1]))  # WGD: weight for Guard+Exit-flagged nodes in guard position
            wgg = (int(bw_info[13].split('=')[1]))  # WGG: weight for Guard-flagged nodes in guard position
            break

        # relay info into Relay object
        elif line[0] == 'r' and line[1] == ' ':
            r_info = line.split('r ', 1)[1].split()
            r = Relay(r_info[1], r_info[5])  # fp and ip

        elif line[0] == 'a' and line[1] == ' ':
            a_info = line.split('a [', 1)[1].split(']', 1)[0]
            r.ipv6 = a_info

        elif line[0] == 's' and line[1] == ' ':
            s_info = line.split('s ', 1)[1].split()  # s_info : list of flags
            if all(f in s_info for f in ('Fast', 'Guard', 'Stable', 'V2Dir')):
                r.is_guard = True
            if 'Exit' in s_info:
                r.is_exit = True

        elif line[0] == 'w' and line[1] == ' ':
            bw = line.split('=')[1]  # bandwidth
            if 'Unmeasured' not in bw:
                r.bw = int(bw)
            # append relay to list
            rs.append(r)
    return rs

# faster if BGP dumps used
def get_prefix_and_asn(ip):
    """
    old method of getting prefix and asn given ip, currently uses routeview data and searches offline
    see get_prefix_and_asn_local(ip) for new method in preprocess_consensus.py
    
    :param ip: (str) ip address in string format

    :return: (list) returns a list containing prefix and ASN of the ip address 

    """
    # what the AS is trying to advertise themselves with?
    base_url = "https://stat.ripe.net/data/network-info/data.json?resource="
    url = base_url + ip
    try:
        response = urllib.request.urlopen(url).read()
    except requests.HTTPError as exception:
        print(exception)
    data = json.loads(response)
    # group ip into group
    # create a dictionary to store IP address already queried and check new IP to see if it exists in the dict
    
    return data['data']['prefix'], data['data']['asns']


def get_roas(filename):
    """
    parse roa file in .csv format, put each entry in a list, then append to a list containing all entries.
    each line in the file converts into [ipv4, maxlen, prefixlen, asn]

    :param filename: (string) name of the csv file to parse 
    :return: (list) 2 lists of list for ipv4 and ipv6 addresses, entry in each list is [ipv4, maxlen, prefixlen, asn]
    """
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
                asn = row[0]
                ipv4s.append([ipv4, maxlen, prefixlen, asn])
            except ipaddress.AddressValueError:
                ipv6 = ipaddress.IPv6Network(row[1])
                maxlen = row[2]
                prefixlen = row[1].split('/')[1]
                if 'AS' not in row[0]:
                    asn = row[0]
                else:
                    asn = row[2:]
               
                ipv6s.append([ipv6, maxlen, prefixlen, asn])

    return ipv4s, ipv6s
