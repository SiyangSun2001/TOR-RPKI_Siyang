from util import *
import matplotlib.pyplot as plt
import sys

# given a list of relays return a list of relay that only contains guards
def get_guards(relays):
    """
    filter out guard relay from a list of relays 

    :param relays: (list) list of TOR relay object 

    :return: (list) list of TOR relay that has the guard flag
    """
    guards = []
    for relay in relays:
        if relay.is_guard:
            guards.append(relay)
    return guards


# given list of relay, return 2 dicts for ipv4, ipv6 addresses. key is the 
# ASN and value if the freq of relay not covered by bandwidth and number
# ASN -> [num relay not covered, bw not covered]
def not_covered(relays):
    # get ASNs / prefixes of relays that aren't covered
    """
    input a list of relay objects and find those that are not covered by ROA. Also record how many bandwith 
    and relay are not covered within the same ASN. 

    :param relays: (list) list of relay objects to be analyzed 

    :return: (dict) ASN -> [number of relay not covered in the ASN, bandwidth not covered in ASN] 

    """
    not_covered_v4 = []
    not_covered_v6 = []
    for relay in relays:
        if relay.ipv4_roa is None:
            not_covered_v4.append(relay)
        if relay.ipv6 != '':
            if relay.ipv6_roa is None:
                not_covered_v6.append(relay)
    
    asn4s_nc = dict() # IPv4 not covered ASNs (no. and bw)
    for relay in not_covered_v4:
        asn = relay.asn
        if asn is None: pass
        else:
            if asn[0] not in asn4s_nc:
                asn4s_nc.setdefault(asn[0], [1, relay.bw])
            else:
                asn4s_nc[asn[0]][0] += 1
                asn4s_nc[asn[0]][1] += relay.bw
    asn6s_nc = dict() # IPv6 not covered ASNs (no. and bw)
    for relay in not_covered_v6:
        asn = relay.ipv6_asn
        if asn is None: pass
        else:
            if asn[0] not in asn6s_nc:
                asn6s_nc.setdefault(asn[0], [1, relay.bw])
            else:
                asn6s_nc[asn[0]][0] += 1
                asn6s_nc[asn[0]][1] += relay.bw
    return asn4s_nc, asn6s_nc


def get_data(relays, guards=False):
    """
    input a list of relay objects and analyze the bandwith of coverage, invalid reason etc for all relays 
    and record the percentage of each spec. The graphing functions visualizes specs calculated here. 

    :param relays: (list) list of relay objects
    :param guards: (bool) boolean specify whether to only analyze guard relay 

    :return: (dict) spec -> value of spec   

    """
    # if guards 
    if guards == True:
        relays = get_guards(relays)
    # not covered relays
    asn4s_nc, asn6s_nc = not_covered(relays) 
    #both dict above maps asn -> [number of not covered relay, total non covered bw]
    # initialize variables
    num_relays = len(relays)
    num_relays_w_ipv6 = 0
    nw_bandwidth = 0
    ipv6_bandwidth = 0
    # IPv4 ROA
    v4_covered = 0
    v4_invalid = 0
    v4_bw_covered = 0
    v4_bw_invalid = 0
    v4_mlpl = 0
    v4_mlpl_valid = 0
    v4_ml = dict()
    v4_pl = dict()
    bad_asn = 0 
    #bad_as_set = 0  
    bad_pl = 0
    bad_asn_and_pl = 0
    # IPv6 ROA
    v6_covered = 0
    v6_invalid = 0
    v6_bw_covered = 0
    v6_bw_invalid = 0
    v6_mlpl = 0
    v6_mlpl_valid = 0
    v6_ml = dict()
    v6_pl = dict()
    v6_bad_asn = 0 
    #v6_bad_as_set = 0  
    v6_bad_pl = 0
    v6_bad_asn_and_pl = 0
    # ASNs
    asn4s = dict()
    asn6s = dict()
    # loop through all relays again 
    for relay in relays:
        if relay.ipv4_prefix == '':
            # num_relays -= 1
            continue
        # bandwidth, num guards
        nw_bandwidth += relay.bw
        # ipv4 calculations
        if relay.ipv4_roa is not None:  # roa = [net(IPv4Network), max length(str), prefix length(str), asn]
            # relay's prefix length
            pre_len = relay.ipv4_prefix.split('/')[1]
            # max length 
            ml = relay.ipv4_roa[1]    # max length of ROA network
            pl = relay.ipv4_roa[2]    # prefix length of ROA network
            # check if invalid
            '''
            if len(relay.asn) > 1:
                bad_as_set += 1 
                v4_invalid += 1
                v4_bw_invalid += relay.bw
            '''
            if relay.asn[0] != relay.ipv4_roa[3] and int(pre_len) > int(ml):
                #case of unmatch ASN and prefix > max length 
                bad_asn_and_pl += 1
                v4_invalid += 1
                v4_bw_invalid += relay.bw
                if ml == pl: v4_mlpl += 1
            elif relay.asn[0] != relay.ipv4_roa[3]:
                #unmatch ASN
                bad_asn += 1
                v4_invalid += 1
                v4_bw_invalid += relay.bw
                if ml == pl: v4_mlpl += 1
            elif int(pre_len) > int(ml):
                #prefix > max length 
                bad_pl += 1
                v4_invalid += 1
                v4_bw_invalid += relay.bw
                if ml == pl: v4_mlpl += 1
            else: 
                #valid roa coverage 
                v4_covered += 1
                v4_bw_covered += relay.bw
                # max length == prefix length
                if ml == pl: v4_mlpl += 1
                if ml == pl: v4_mlpl_valid += 1
                # max length distribution
                if ml in v4_ml: v4_ml[ml] += 1
                else: v4_ml.setdefault(ml, 1)
                # prefix length distribution
                if pl in v4_pl: v4_pl[pl] += 1
                else: v4_pl.setdefault(pl, 1)   
        # asn ipv4
        asn = relay.asn
        if asn is None:
            pass
        else:
            if asn[0] not in asn4s:
                asn4s.setdefault(asn[0], [1, relay.bw])
            else:
                asn4s[asn[0]][0] += 1
                asn4s[asn[0]][1] += relay.bw  
        # ipv6
        if relay.ipv6 != '':
            num_relays_w_ipv6 += 1
            ipv6_bandwidth += relay.bw
            if relay.ipv6_prefix == '':
                continue
            # ipv6 calculations
            if relay.ipv6_roa is not None:
                pre_len = relay.ipv6_prefix.split('/')[1]
                ml = relay.ipv6_roa[1]    # max length of ROA network
                pl = relay.ipv6_roa[2]    # prefix length of ROA network
                if relay.ipv6_asn[0] != relay.ipv6_roa[3] and int(pre_len) > int(ml):
                    v6_bad_asn_and_pl += 1
                    v6_invalid += 1
                    v6_bw_invalid += relay.bw
                    if ml == pl: v6_mlpl += 1
                elif relay.ipv6_asn[0] != relay.ipv6_roa[3]:
                    v6_bad_asn += 1
                    v6_invalid += 1
                    v6_bw_invalid += relay.bw
                    if ml == pl: v6_mlpl += 1
                elif int(pre_len) > int(ml):
                    v6_bad_pl += 1
                    v6_invalid += 1
                    v6_bw_invalid += relay.bw
                    if ml == pl: v6_mlpl += 1
                else: 
                    v6_bw_covered += relay.bw
                    v6_covered += 1
                    # max length == prefix length
                    if ml == pl: v6_mlpl += 1
                    if ml == pl: v6_mlpl_valid += 1
                    # max length distribution
                    if ml in v6_ml: v6_ml[ml] += 1
                    else: v6_ml.setdefault(ml, 1)
                    # prefix length distribution
                    if pl in v6_pl: v6_pl[pl] += 1
                    else: v6_pl.setdefault(pl, 1)    
            # asn ipv6
            asn6 = relay.ipv6_asn
            if asn6 is None:
                pass
            else: 
                if asn6[0] not in asn6s:
                    asn6s.setdefault(asn6[0], [1, relay.bw])
                else:
                    asn6s[asn6[0]][0] += 1
                    asn6s[asn6[0]][1] += relay.bw   
    #asn4s
    n = dict()
    b = dict()
    for k, v in asn4s.items():
        n.setdefault(k, v[0])
        b.setdefault(k, v[1])
    top_num = sorted(n, key=n.get, reverse=True)[:10]
    top_bw = sorted(b, key=b.get, reverse=True)[:10]
    #asn4s_nc
    n2 = dict()
    b2 = dict()
    for k, v in asn4s_nc.items():
        n2.setdefault(k, v[0])
        b2.setdefault(k, v[1])
    top_num_nc = sorted(n2, key=n2.get, reverse=True)[:10]
    top_bw_nc = sorted(b2, key=b2.get, reverse=True)[:10]
    #asn6s
    n6 = dict()
    b6 = dict()
    for k, v in asn6s.items():
        n6.setdefault(k, v[0])
        b6.setdefault(k, v[1])
    v6_top_num = sorted(n6, key=n6.get, reverse=True)[:10]
    v6_top_bw = sorted(b6, key=b6.get, reverse=True)[:10]
    #asn4s_nc
    n62 = dict()
    b62 = dict()
    for k, v in asn6s_nc.items():
        n62.setdefault(k, v[0])
        b62.setdefault(k, v[1])
    v6_top_num_nc = sorted(n62, key=n62.get, reverse=True)[:10]
    v6_top_bw_nc = sorted(b62, key=b62.get, reverse=True)[:10]
    # return dictionary of values
    ret = dict()
    ret.setdefault('num_relays', num_relays)
    ret.setdefault('nw_bandwidth', nw_bandwidth)
    ret.setdefault('v4_covered', v4_covered)
    ret.setdefault('v4_invalid', v4_invalid)
    ret.setdefault('v4_bw_covered', v4_bw_covered)
    ret.setdefault('v4_bw_invalid', v4_bw_invalid)
    ret.setdefault('bad_asn', bad_asn)
    # ret.setdefault('bad_as_set', bad_as_set)
    ret.setdefault('bad_pl', bad_pl)
    ret.setdefault('bad_asn_and_pl', bad_asn_and_pl)
    ret.setdefault('top_num', top_num)
    ret.setdefault('top_bw', top_bw)
    ret.setdefault('top_num_nc', top_num_nc)
    ret.setdefault('top_bw_nc', top_bw_nc)
    ret.setdefault('asn4s_nc', asn4s_nc)
    # ipv6
    ret.setdefault('num_relays_w_ipv6', num_relays_w_ipv6)
    ret.setdefault('ipv6_bandwidth', ipv6_bandwidth)
    ret.setdefault('v6_covered', v6_covered)
    ret.setdefault('v6_invalid', v6_invalid)
    ret.setdefault('v6_bw_covered', v6_bw_covered)
    ret.setdefault('v6_bw_invalid', v6_bw_invalid)
    ret.setdefault('v6_bad_asn', v6_bad_asn)
    # ret.setdefault('v6_bad_as_set', v6_bad_as_set)
    ret.setdefault('v6_bad_pl', v6_bad_pl)
    ret.setdefault('v6_bad_asn_and_pl', v6_bad_asn_and_pl)
    ret.setdefault('v6_top_num', v6_top_num)
    ret.setdefault('v6_top_bw', v6_top_bw)
    ret.setdefault('v6_top_num_nc', v6_top_num_nc)
    ret.setdefault('v6_top_bw_nc', v6_top_bw_nc)
    ret.setdefault('v6_mlpl', v6_mlpl)
    ret.setdefault('v6_mlpl_valid', v6_mlpl_valid)
    ret.setdefault('asn6s_nc', asn6s_nc)
    return ret


def print_v6_data(num_relays, ipv6_bandwidth, num_relays_w_ipv6, v6_covered, v6_invalid, v6_bw_covered, v6_bw_invalid, v6_mlpl, v6_mlpl_valid):
    """
    print out IPv6 relay information in text format
    """
    
    print('# Relays w/ IPv6: {} ({} / {})'.format((num_relays_w_ipv6 / num_relays), num_relays_w_ipv6, num_relays) )
    print('# IPv6 Protected Relays: {} ({} / {})'.format(((v6_covered+v6_invalid) / num_relays_w_ipv6), (v6_covered+v6_invalid), num_relays_w_ipv6) )
    print('BW IPv6 Protected Relays: {} ({} / {})'.format(((v6_bw_covered+v6_bw_invalid) / ipv6_bandwidth), v6_bw_covered, ipv6_bandwidth) )
    print('# IPv6 Protected Relays (Tight): {} ({} / {})'.format((v6_mlpl / num_relays_w_ipv6), v6_mlpl, num_relays_w_ipv6) )
    print('# IPv6 Protected Relays (valid): {} ({} / {})'.format((v6_covered / num_relays_w_ipv6), v6_covered, num_relays_w_ipv6) )
    print('BW IPv6 Protected Relays(valid): {} ({} / {})'.format((v6_bw_covered / ipv6_bandwidth), v6_bw_covered, ipv6_bandwidth) )
    print('# IPv6 Protected Relays (Tight) (valid): {} ({} / {})'.format((v6_mlpl_valid / num_relays_w_ipv6), v6_mlpl_valid, num_relays_w_ipv6) )
    print('Valid ROAs: {} ({} / {})'.format((v6_covered / (v6_invalid+v6_covered)), v6_covered, (v6_invalid+v6_covered)) )
    print('Invalid ROAs: {} ({} / {})'.format((v6_invalid / (v6_invalid+v6_covered)), v6_invalid, (v6_invalid+v6_covered)) )


def all_relays(valid, invalid, unknown, labels):
    """
    graph the percentage of all relays that either has valid, invalid or not found ROA
    in a graph with time on the x-axis and coverage percentage on the y-axis
    """
    plt.clf()
    x = [0, 1, 2, 3, 4, 5, 6,7]
    plt.plot(x, valid, color='green')
    plt.plot(x, invalid, color='red')
    plt.plot(x, unknown, color='yellow')
    plt.xticks(x, labels, rotation=90)
    plt.xlim(0, 7)
    plt.yticks([0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6])
    plt.legend(('valid', 'invalid', 'not-found'), bbox_to_anchor=(0, 1.02, 1.02, .1), loc="upper center", ncol=3)
    #plt.ylabel('% Relays')
    plt.ylabel('% Guards')
    #plt.xlabel('Month')
    plt.grid(color='.9')
    plt.savefig("all_relay.png")


def roas(good, wrong_as, wrong_as_pl, wrong_pl, labels):

    """
    graph the invalid reasons either invalid ASN, prefix max length violation or 
    both for ROAs, with percentage of ROA on the y-axis and time on the x-axis. 
    """
    plt.clf()
    x = [0, 1, 2, 3, 4, 5, 6,7]
    #plt.plot(x, good, color='green')
    plt.plot(x, wrong_as, color='red')
    plt.plot(x, wrong_pl, color='yellow')
    plt.plot(x, wrong_as_pl, color='orange')
    # plt.plot(x, as_set, color='darkred')
    plt.xticks(x, labels, rotation=90)
    plt.xlim(0, 7)
    #plt.yticks([0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6])
    plt.legend(('AS', 'ML', 'AS-ML', 'AS-SET'), bbox_to_anchor=(0, 1.02, 1.02, .1), loc="upper center", ncol=4)
    plt.ylabel('% ROAs')
    #plt.ylabel('# Guards')
    #plt.xlabel('Month')
    plt.grid(color='.9')
    plt.savefig("roas.png")


# used the following format to graph data pickled from multiple months
def main(): 
    """
    uses functions declared above and processed consensus pickles to graph ROA coverage 
    information on relays. To use other graphing function, simple add to the end of main
    function and put in the matching parameters. 
    """
    # with open("processed/2020-09-13-00-processed.pickle", 'rb') as f1:
    #     relays = pickle.load(f1)
    #     sept = get_data(relays)
    # with open("processed/2020-10-13-00-processed.pickle", 'rb') as f2:
    #     relays = pickle.load(f2)
    #     octo = get_data(relays)
    # with open("processed/2020-11-17-00-processed.pickle", 'rb') as f3:
    #     relays = pickle.load(f3)
    #     nov = get_data(relays)
    with open("processed/2020-12-13-00-processed.pickle", 'rb') as f4:
        relays = pickle.load(f4)
        dec = get_data(relays)
    with open("processed/2021-01-13-00-processed.pickle", 'rb') as f5:
        relays = pickle.load(f5)
        jan = get_data(relays)
    with open("processed/2021-02-13-00-processed.pickle", 'rb') as f6:
        relays = pickle.load(f6)
        feb = get_data(relays)
    with open("processed/2021-03-13-00-processed.pickle", 'rb') as f7:
        relays = pickle.load(f7)
        mar = get_data(relays)
    with open("processed/2021-04-13-00-processed.pickle", 'rb') as f8:
        relays = pickle.load(f8)
        apr = get_data(relays)
    with open("processed/2021-05-13-00-processed.pickle", 'rb') as f9:
        relays = pickle.load(f9)
        may = get_data(relays)
    with open("processed/2021-06-13-00-processed.pickle", 'rb') as f10:
        relays = pickle.load(f10)
        june = get_data(relays)
    with open("processed/2021-07-13-00-processed.pickle", 'rb') as f11:
        relays = pickle.load(f11)
        july = get_data(relays)
    # with open("processed/2021-08-13-00-processed.pickle", 'rb') as f12:
    #     relays = pickle.load(f12)
    #     aug = get_data(relays)
    # with open("processed/2021-09-13-00-processed.pickle", 'rb') as f13:
    #     relays = pickle.load(f13)
    #     sep = get_data(relays)
    
    # do things here
    num_relays = mar['num_relays']
    num_relays_w_ipv6 = mar['num_relays_w_ipv6']
    nw_bandwidth = mar['nw_bandwidth']
    ipv6_bandwidth = mar['ipv6_bandwidth']
    v6_covered = mar['v6_covered']
    v6_invalid = mar['v6_invalid']
    v6_bw_covered = mar['v6_bw_covered']
    v6_bw_invalid = mar['v6_bw_invalid']
    v6_bad_asn = mar['v6_bad_asn']
    v6_bad_pl = mar['v6_bad_pl']
    v6_bad_asn_and_pl = mar['v6_bad_asn_and_pl']
    asn6s_nc = mar['asn6s_nc']
    v6_mlpl = mar['v6_mlpl']
    v6_mlpl_valid = mar['v6_mlpl_valid']

    months = [dec, jan, feb, mar, apr, may, june, july]#[sept, octo, nov, dec, jan, feb, mar, apr, may, june, july, aug, sep]
    labels = ['2020-12-13', '2021-01-13', '2021-02-13', '2021-03-13','2021-04-13','2021-05-13','2021-06-13','2021-07-13']
    valid = []
    invalid = []
    covered = []
    unknown = []
    good = []
    wrong_as = []
    wrong_pl = []
    wrong_as_pl = []
    # as_set = []
    v6 = False
    for mon in months:
        if v6 == True:
            nr = mon['num_relays_w_ipv6']
            nv = mon['v6_covered']
            ni = mon['v6_invalid']
            wa = mon['v6_bad_asn']
            wp = mon['v6_bad_pl']
            wap = mon['v6_bad_asn_and_pl']
        else:
            nr = mon['num_relays']
            nv = mon['v4_covered']
            ni = mon['v4_invalid']
            wa = mon['bad_asn']
            wp = mon['bad_pl']
            wap = mon['bad_asn_and_pl']
            # was = mon['bad_as_set']
        print(wp / ni)
        nu = nr - (nv + ni)
        valid.append(nv/nr)
        invalid.append(ni/nr)
        c = nv + ni
        # c is total number of relays
        wrong_as.append(wa/c)
        wrong_pl.append(wp/c)
        wrong_as_pl.append(wap/c)
        # as_set.append(was)
        good.append(nv)
        unknown.append(nu/nr) 
    
    roas(good, wrong_as, wrong_as_pl, wrong_pl, labels)
    all_relays(valid, invalid, unknown, labels)
        

if __name__ == '__main__':
    sys.exit(main())