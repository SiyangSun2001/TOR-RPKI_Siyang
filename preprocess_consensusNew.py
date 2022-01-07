

from util import *
import sys
import argparse
import shutil
import time
import upgradeIpASNMap

# place archived consensuses in folder called archive
def archive_consensus(year, month, date, hour):
    '''Pulls relay info from consensus file
    helper for pickle_consensus
    
    Parameters
    ----------
    year : (str) 'year'
    month : (str) 'mm'
    date : (str) 'dd'
    hour : (str) 'hr'

    Returns
    ----------
    list of Relay objects, (int) wgd, (int), wgg
    '''
    # Set up path
    p = os.getcwd()
    #p = os.path.split(p)[0]
    #p = os.path.split(p)[0]
    f1 = r'/consensuses-' + year + '-' + month
    f2 = '/' + date
    f3 = '/' + year + '-' + month + '-' + date + '-' + hour + '-00-00-consensus'
    path = p + r'/archive' + f1 + f2 + f3
    # If file exists, open it
    try:
        with open(path, 'r') as f:
            lines = f.read().split('\n')
            rs = []
            for line in lines:
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
                    r.ipv6 = a_info # ipv6 if it exists
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
    # If file does not exist, do nothing
    except FileNotFoundError:
        print(f3 + ' not found.')
        return False, False, False      
    return rs, wgd, wgg


def get_all_ips(start_date, end_date):
    all_ipv4s = set()
    all_ipv6s = set()
    p = os.getcwd()
    path = p + '/archive_pickles/'
    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
        rs, wgd, wgg = load_consensus(path, t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), t.strftime('%H'))
        if rs:
            ipv4s = [r.ip for r in rs]
            ipv6s = [r.ipv6 for r in rs if r.ipv6 != '']
            all_ipv4s.update(ipv4s)
            all_ipv6s.update(ipv6s)    
    return all_ipv4s, all_ipv6s

# need directory called archive_pickles for intermediate pickles w/o ROA info + asn/prefix info
def pickle_consensus(start_date, end_date, gen_all_ip_pickles=False):   
    '''creates .pickle for each consensus
    if gen_all_ip_pickles = True, creates all-ips.pickle for all ips b/t start and end date
    requires directory called archive_pickles to put consensus pickles in
    '''
    path = os.getcwd()
    # path = os.path.split(path)[0] + '/archive/'
    path = path + '/archive_pickles/'
    all_ipv4s = set()
    all_ipv6s = set()
    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
        rs, wgd, wgg = archive_consensus(t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), t.strftime('%H'))
        if rs:
            ipv4s = [r.ip for r in rs]
            ipv6s = [r.ipv6 for r in rs if r.ipv6 != '']
            all_ipv4s.update(ipv4s)
            all_ipv6s.update(ipv6s)
            filename = t.strftime('%Y') + '-' + t.strftime('%m') + '-' + t.strftime('%d') + '-' + t.strftime('%H') + '.pickle'
            with open(filename, 'wb') as f_pc1:
                pickle.dump(rs, f_pc1)
                pickle.dump(wgd, f_pc1)
                pickle.dump(wgg, f_pc1)
            # moves file into directory archive
            shutil.move(filename, path)
    if gen_all_ip_pickles:
        filename2 = 'all-ips.pickle'
        with open(filename2, 'wb') as f_pc2:
            pickle.dump(all_ipv4s, f_pc2)
            pickle.dump(all_ipv6s, f_pc2)
    return all_ipv4s, all_ipv6s

# could be done faster if you just used BGP dumps to find what prefix / asn each relay is announced with
def get_pre_asn(ipv4s, ipv6s, make_pickle=False, existing_file=False):
    # set up dicts
    ipv4s_asns = dict()
    ipv6s_asns = dict()
    # loop through ips
    if existing_file:
        new_ipv4s = set()
        new_ipv6s = set()
        with open('relay_asns.pickle', 'rb') as ef:
            v4_asns = pickle.load(ef)
            v6_asns = pickle.load(ef)
        for ip in ipv4s:
            if ip in v4_asns:
                pre_asn = v4_asns[ip]
                ipv4s_asns.setdefault(ip, pre_asn)
            else:
                new_ipv4s.add(ip)
        for ip in ipv6s:
            if ip in v6_asns:
                pre_asn = v6_asns[ip]
                ipv6s_asns.setdefault(ip, pre_asn)
            else:
                new_ipv6s.add(ip)
        ipv4s = new_ipv4s
        ipv6s = new_ipv6s
    for ip in ipv4s:
        pre, asn = get_prefix_and_asn(ip)
        if len(asn) != 1:
            print(ip + ' is in ' + str(len(asn)) + ' ASes')
        if len(asn) == 0:
            ipv4s_asns.setdefault(ip, [pre, None])
        ipv4s_asns.setdefault(ip, [pre, asn])
    # ipv6s
    for ip in ipv6s:
        pre, asn = get_prefix_and_asn(ip)
        if len(asn) != 1:
            print(ip + ' is in ' + str(len(asn)) + ' ASes')
        if len(asn) == 0:
            ipv6s_asns.setdefault(ip, [pre, None])
        ipv6s_asns.setdefault(ip, [pre, asn])
    if make_pickle:
        with open('relay_asns.pickle', 'wb') as f_pa:
            pickle.dump(ipv4s_asns, f_pa)
            pickle.dump(ipv6s_asns, f_pa)
    return ipv4s_asns, ipv6s_asns


def get_roas(filename):
    '''get roas from csv file
    returns two lists of lists
    [ip, max length, prefix length]
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
                asn = row[0]
                ipv4s.append([ipv4, maxlen, prefixlen, asn])
            except ipaddress.AddressValueError:
                ipv6 = ipaddress.IPv6Network(row[1])
                maxlen = row[2]
                prefixlen = row[1].split('/')[1]
                asn = row[0]
                ipv6s.append([ipv6, maxlen, prefixlen, asn])
    #v4s = sorted(ipv4s, key=lambda x:x[0])
    #v6s = sorted(ipv6s, key=lambda x:x[0])
    return ipv4s, ipv6s


def coverage_dict(roas, ipv4s, ipv6s, make_pickle=False):
    '''
    uses roa csv file downloaded from https://rpki-validator.ripe.net/roas
    if make_pickle = True, creates coveragev4.pickle and coveragev6.pickle to be used in update_consensus_pickle
    '''
    # get ROA nets
    v4nets, v6nets = get_roas(roas) # [ip, maxlen, prefixlen, asn]
    # set up coverage dicts
    v4coverage = dict()
    v6coverage = dict()
    # loop through all ip addresses
    for ip in ipv4s:
        ip_addr = ipaddress.IPv4Address(ip)
        v4coverage.setdefault(ip, None)
        for net in v4nets:
            if ip_addr in net[0]:
                v4coverage[ip] = net
                break
    for ip in ipv6s:
        ip_addr = ipaddress.IPv6Address(ip)
        v6coverage.setdefault(ip, None)
        for net in v6nets:
            if ip_addr in net[0]:
                v6coverage[ip] = net
                break
    if make_pickle:
        with open('coverage.pickle', 'wb') as f_cd1:
            pickle.dump(v4coverage, f_cd1)
            pickle.dump(v6coverage, f_cd1)
    return v4coverage, v6coverage


def load_consensus(p, year, month, date, hour):
    '''pulls relay data from pickled file'''
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

# need directory called processed
def update_consensus_pickle(start_date, end_date, v4coverage, v6coverage, ipv4_asns, ipv6_asns):
    ''' updates allguards.pickle to contain ROA coverage'''
    p = os.getcwd()
    path = p + '/archive_pickles/'
    path2 = p + '/processed/'
    # iterate through consensus pickles
    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
        # load old pickle
        rs, wgd, wgg = load_consensus(path, t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), t.strftime('%H'))
        if rs:
            updated_rs = []
            for r in rs:
                r.ipv4_prefix = ipv4_asns[r.ip][0]
                r.asn = ipv4_asns[r.ip][1]
                r.ipv4_roa = v4coverage[r.ip]
                if r.ipv6 != '':
                    r.ipv6_prefix = ipv6_asns[r.ipv6][0]
                    r.ipv6_asn = ipv6_asns[r.ipv6][1]
                    r.ipv6_roa = v6coverage[r.ipv6]
                    #if r.ipv6_asn != r.asn:
                    #    print(r.ip + ' in ' + str(r.asn) + '. ' + r.ipv6 + ' in ' + str(r.ipv6_asn))
                updated_rs.append(r)
            filename = t.strftime('%Y') + '-' + t.strftime('%m') + '-' + t.strftime('%d') + '-' + t.strftime('%H') + '-processed.pickle'
            with open(filename, 'wb') as f_ucp:
                pickle.dump(updated_rs, f_ucp)
                pickle.dump(wgd, f_ucp)
                pickle.dump(wgg, f_ucp) 
            shutil.move(filename, path2)
    return


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("start_date", help="date in year-mo-da-hr format")
    parser.add_argument("end_date", help="date in year-mo-da-hr format (not inclusive)")
    parser.add_argument("roas", help="csv file of validated ROAs")
    return parser.parse_args(args)


def main(args):
    start_time = time.time()
    args = parse_arguments(args)
    start_date = args.start_date.split('-')
    end_date = args.end_date.split('-')
    for i in range(4):
        start_date[i] = int(start_date[i])
        end_date[i] = int(end_date[i])
    start_date = datetime(start_date[0], start_date[1], start_date[2], start_date[3])
    end_date = datetime(end_date[0], end_date[1], end_date[2], end_date[3])
     
    # pickle consensus
    all_ipv4s, all_ipv6s = pickle_consensus(start_date, end_date)   # set of all ip addresses
#    upgradeIpASNMap.compareLvI(all_ipv4s)

    upgradeIpASNMap.compareLvI(all_ipv6s)
 
    print("--- %s seconds to preprocess consensuses ---" % (time.time() - start_time))
    start_time = time.time()

    with open('all-ips.pickle', 'rb') as f:
       all_ipv4s = pickle.load(f)
       all_ipv6s = pickle.load(f)
    all_ipv4s, all_ipv6s = get_all_ips(start_date, end_date)
    
    # get prefix and asn for each relay
    get_pre_asn(ipv4s, ipv6s, make_pickle=False, existing_file=False)
    ipv4_asns, ipv6_asns = get_pre_asn(all_ipv4s, all_ipv6s, False, True)        # dicts: key: ip -> value: [prefix, asn]
    print("--- %s seconds to get prefix and ASN ---" % (time.time() - start_time))
    start_time = time.time()

    # create coverage dict -> only uses one set of ROAs
    v4, v6 = coverage_dict(args.roas, all_ipv4s, all_ipv6s)         # dicts: key: ip -> value: [ip, maxlen, prefixlen, asn] (ROA)
    print("--- %s seconds to create coverage dict ---" % (time.time() - start_time))
    start_time = time.time()

    with open('relay_asns.pickle', 'rb') as f3:
       ipv4_asns = pickle.load(f3)
       ipv6_asns = pickle.load(f3)     
    
    # create consensus pickle with ROA coverage
    update_consensus_pickle(start_date, end_date, v4, v6, ipv4_asns, ipv6_asns)
    print("--- %s seconds to update consensus pickles ---" % (time.time() - start_time))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))




