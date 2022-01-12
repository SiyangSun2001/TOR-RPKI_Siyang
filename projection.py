from util import *
import matplotlib.pyplot as plt
import sys

def adl_cov2(num_relays, v4_covered, top_num_nc, asn4s):
    # Top ASNs stacked bar for number of relays
    d = dict()
    dd = dict()
    all_sum = 0
    nc_sum = 0
    current = v4_covered / num_relays
    covered = []
    covered.append(current)

    for a in top_num_nc:
        all_relays = asn4s[a]['relays']
        nc = asn4s[a]['relays_nc']
        all_sum += all_relays
        nc_sum += nc
        d.setdefault(a, (all_relays-nc))
        dd.setdefault(a, nc)
        adl_cov = covered[-1] + (nc / num_relays)
        covered.append(adl_cov)

    c_other = (v4_covered - (all_sum - nc_sum))
    nc_other = ((num_relays - v4_covered) - nc_sum)
    d.setdefault('Current', c_other)
    dd.setdefault('Other', nc_other)

    num_cov = list(d.values())
    num_ncov = list(dd.values())

    labels_temp = list(d.keys())

    ordering = []
    for x in range(len(num_cov)):
        ordering.append(num_cov[x] + num_ncov[x])
    z1 = sorted(zip(ordering, num_cov), key=lambda t:t[0], reverse=True)
    uz1 = list(zip(*z1))
    z2 = sorted(zip(ordering, num_ncov), key=lambda t:t[0], reverse=True)
    uz2 = list(zip(*z2))
    z3 = sorted(zip(ordering, labels_temp), key=lambda t:t[0], reverse=True)
    uz3 = list(zip(*z3))
    labels = uz3[1]

    cov = uz1[1]
    ncov = uz2[1]

    ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


    fig, ax = plt.subplots(1, sharex=True)
    ax.plot(ind, covered, 'o-')
    ax.set_ylabel('% Relays Covered if AS Fully Deploys ROA')
    #ax.set_ylim(top=.8)
    for x,y in zip(ind, covered):
        label = "{:.1f}".format(y *100) + '%'
        ax.annotate(label, (x,y), textcoords="offset points", xytext=(0,10), ha='center')

    plt.setp(ax, xticks=ind, xticklabels=labels)
    # plt.legend((ax1[0], ax2[0]), ('Covered', 'Not Covered'))
    plt.show()


def adl_cov(num_relays, v4_covered, top_num_nc, asn4s):
    """
    graph the projection of ROA coverage if top TOR relay AS would cover their whole IP space
    """
    # Top ASNs stacked bar for number of relays
    d = dict()      # covered
    dd = dict()     # not covered
    all_sum = 0
    nc_sum = 0
    current = v4_covered / num_relays
    covered = []
    covered.append(current)

    for a in top_num_nc[:5]:
        all_relays = asn4s[a]['relays']
        nc = asn4s[a]['relays_nc']
        all_sum += all_relays
        nc_sum += nc
        d.setdefault(a, (all_relays-nc))
        dd.setdefault(a, nc)
        adl_cov = covered[-1] + (nc / num_relays)
        covered.append(adl_cov)

    c_other = (v4_covered - (all_sum - nc_sum))
    nc_other = ((num_relays - v4_covered) - nc_sum)
    d.setdefault('Other', c_other)
    dd.setdefault('Other', nc_other)

    num_cov = list(d.values())
    num_ncov = list(dd.values())

    labels_temp = list(d.keys())
    # print(labels_temp)
    ordering = []
    for x in range(len(num_cov)):
        #ordering.append(num_cov[x] + num_ncov[x])
        ordering.append(num_ncov[x])
    z1 = sorted(zip(ordering, num_cov), key=lambda t:t[0], reverse=True)
    uz1 = list(zip(*z1))
    z2 = sorted(zip(ordering, num_ncov), key=lambda t:t[0], reverse=True)
    uz2 = list(zip(*z2))
    z3 = sorted(zip(ordering, labels_temp), key=lambda t:t[0], reverse=True)
    uz3 = list(zip(*z3))
    labels = uz3[1]
    # print(labels)
    cov = uz1[1]
    ncov = uz2[1]

    #ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ind = [0, 1, 2, 3, 4, 5]

    # line
    fig, ax = plt.subplots(2, sharex=True)
    ax[0].plot(ind, covered, 'o-')
    ax[0].set_ylabel('% ROA Coverage')
    ax[0].set_ylim(top=1)
    for x,y in zip(ind, covered):
        label = "{:.2f}".format(y *100) + '%'
        ax[0].annotate(label, (x,y), textcoords="offset points", xytext=(0,10), ha='center')
    # bar
    ax1 = ax[1].bar(ind, cov)
    ax2 = ax[1].bar(ind, ncov, bottom=cov, color='green')
    # labeling 
    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        if h1 == 3:
            ax[1].text(r1.get_x() + r1.get_width() / 2., h1 + 3, "%d" % h1, ha="center", va="top", color="black", fontsize=10)
        elif h1 != 0:
            ax[1].text(r1.get_x() + r1.get_width() / 2., 6, "%d" % h1, ha="center", va="top", color="black", fontsize=10)
        if h2 != 0:
            ax[1].text(r2.get_x() + r2.get_width() / 2., h1 + h2 - ((h1 + h2) * .05), "%d" % h2, ha="center", va="top", color="black", fontsize=10)
    # bax = brokenaxes.brokenaxes(ylims=((0, 650), (3000, 5500)), hspace=.05)
    ax[1].set_ylabel('# of Relays')
    ax[1].set_xlabel('ASN')
    #ax3 = ax[1].twinx()
    #ax4 = ax[1].twinx()
    #ax3 = ax[1].bar(ind[0], c_other, color='blue')
    #ax4 = ax[1].bar(ind[0], nc_other, bottom=c_other, color='green')
    ax[1].set_yscale('log')
    plt.setp(ax, xticks=ind, xticklabels=labels)
    plt.legend((ax1[0], ax2[0]), ('Covered', 'Not Covered'))
    plt.show()


def adl_cov_guards(num_relays, v4_covered, top_num_nc, asn4s, asn4s_nc, n2):
 

    all_nc = sorted(n2, key=n2.get, reverse=True)
    covered = []
    covered.append(v4_covered / num_relays)
    d = dict()
    print(len(all_nc))
    for a in all_nc:
        nc = asn4s_nc[a][0]
        d.setdefault(a, nc)
        adl_cov = covered[-1] + (nc / num_relays)
        covered.append(adl_cov)

    labels = list(d.keys())[:20]

    x = np.arange(1,21)
    plt.plot(x, covered[:20])

    plt.ylabel('Percent of Guard Relays Covered')
    plt.xlabel('ASN')
    plt.suptitle('Network Coverage if AS Adopts ROA 2020-10-13')
    plt.xticks(x, labels, rotation=70)
    #plt.setp(xticks=ind, xticklabels=labels)
    plt.show()


def adl_cov_bw(nw_bandwidth, v4_bw_covered, top_bw_nc, asn4s, asn4s_nc):
        # Top ASNs stacked bar for number of relays
    bw_c = dict()
    bw_nc = dict()
    bw_all_sum = 0
    bw_nc_sum = 0
    covered = [(v4_bw_covered / nw_bandwidth)]

    for a in top_bw_nc:
        all = asn4s[a][1]
        nc = asn4s_nc[a][1]
        bw_all_sum += all
        bw_nc_sum += nc
        bw_c.setdefault(a, (all-nc))
        bw_nc.setdefault(a, nc)
        adl_cov = covered[-1] + (nc / nw_bandwidth)
        covered.append(adl_cov)

    c_other = (v4_bw_covered - (bw_all_sum - bw_nc_sum))
    nc_other = ((nw_bandwidth - v4_bw_covered) - bw_nc_sum)
    bw_c.setdefault('Other', c_other)
    bw_nc.setdefault('Other', nc_other)

    bw_cov = list(bw_c.values())
    bw_ncov = list(bw_nc.values())

    labels = list(bw_c.keys())
    print(labels)

    ordering = []
    for x in range(len(bw_cov)):
        ordering.append(bw_cov[x] + bw_ncov[x])
    print(ordering)
    z1 = sorted(zip(ordering, bw_cov), key=lambda t:t[0], reverse=True)
    uz1 = list(zip(*z1))
    z2 = sorted(zip(ordering, bw_ncov), key=lambda t:t[0], reverse=True)
    uz2 = list(zip(*z2))
    z3 = sorted(zip(ordering, labels), key=lambda t:t[0], reverse=True)
    uz3 = list(zip(*z3))
    print(uz3[1])
    labels = uz3[1]

    ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    fig, ax = plt.subplots(2, sharex=True)

    ax[0].plot(ind, covered, 'o-')
    ax[0].set_ylabel('% Bandwidth Covered if AS Fully Adds ROA')
    ax[0].set_ylim(top=1)
    for x,y in zip(ind, covered):
        label = "{:.2f}".format(y *100) + '%'
        ax[0].annotate(label, (x,y), textcoords="offset points", xytext=(0,10), ha='center')

    ax1 = ax[1].bar(ind, uz1[1])
    ax2 = ax[1].bar(ind, uz2[1], bottom=uz1[1], color='green')

    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        h1_l = float((float(h1) / float(nw_bandwidth)) * 100.0)
        h2_l = float((float(h2) / float(nw_bandwidth)) * 100.0)
        if h1 != 0:
            plt.text(r1.get_x() + r1.get_width() / 2., h1 + 100, "{:.2f}".format(h1_l), ha="center", va="top", color="black", fontsize=10)
        if h2 != 0:
            plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2, "{:.2f}".format(h2_l), ha="center", va="top", color="black", fontsize=10)

    ax[1].set_ylabel('Bandwidth (labeled: % Tor BW)')
    ax[1].set_xlabel('ASN')
    ax[1].set_yscale('log')
    plt.suptitle('ASNs Ranked By Percent of Tor Bandwidth 2020-10-13')
    plt.setp(ax, xticks=ind, xticklabels=labels)
    plt.legend((ax1[0], ax2[0]), ('Covered', 'Not Covered'))
    plt.show()


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
    
    # initialize variables
    num_relays = len(relays)
    num_relays_w_ipv6 = 0
    nw_bandwidth = 0
    ipv6_bandwidth = 0

    v4_covered = 0
    v4_invalid = 0
    v4_bw_covered = 0
    v4_bw_invalid = 0
    v4_mlpl = 0
    v4_ml = dict()
    v4_pl = dict()

    v6_covered = 0
    v6_bw_covered = 0
    v6_mlpl = 0
    v6_ml = dict()
    v6_pl = dict()

    asn4s = dict()
    asn6s = dict()

    bad_asn = 0 
    bad_as_set = 0  
    bad_pl = 0
    bad_asn_and_pl = 0

    rs = dict()
    # loop through all relays again 
    for relay in relays:
        if relay.ipv4_prefix == '':
            # num_relays -= 1
            continue
        rs.setdefault(relay.fp, 'nc')
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
            if len(relay.asn) > 1:
                bad_as_set += 1 
                v4_invalid += 1
                v4_bw_invalid += relay.bw
                rs[relay.fp] = 'set'
            elif relay.asn[0] != relay.ipv4_roa[3] and int(pre_len) > int(ml):
                bad_asn_and_pl += 1
                v4_invalid += 1
                v4_bw_invalid += relay.bw
                rs[relay.fp] = 'iap'
            elif relay.asn[0] != relay.ipv4_roa[3]:
                bad_asn += 1
                v4_invalid += 1
                v4_bw_invalid += relay.bw
                rs[relay.fp] = 'ia'
            elif int(pre_len) > int(ml):
                bad_pl += 1
                v4_invalid += 1
                v4_bw_invalid += relay.bw
                rs[relay.fp] = 'ip'
            else: 
                rs[relay.fp] = 'v'
                v4_covered += 1
                v4_bw_covered += relay.bw
                # max length == prefix length
                if ml == pl: v4_mlpl += 1
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
                d = dict()
                d.setdefault('relays', 1)
                d.setdefault('bw', relay.bw)
                d.setdefault('relays_nc', 0)
                d.setdefault('bw_nc', 0)
                d.setdefault('relays_iv', 0)
                d.setdefault('bw_iv', 0)
                asn4s.setdefault(asn[0], d)
            else:
                asn4s[asn[0]]['relays'] += 1
                asn4s[asn[0]]['bw'] += relay.bw  
            if relay.ipv4_roa is None:
                asn4s[asn[0]]['relays_nc'] += 1
                asn4s[asn[0]]['bw_nc'] += relay.bw
            else:
                if relay.asn[0] != relay.ipv4_roa[3] or int(pre_len) > int(ml):
                    asn4s[asn[0]]['relays_iv'] += 1
                    asn4s[asn[0]]['bw_iv'] += relay.bw 
    #asn4s
    n = dict()
    b = dict()
    n_nc = dict()
    b_nc = dict()
    for k, v in asn4s.items():
        n.setdefault(k, v['relays'])
        b.setdefault(k, v['bw'])
        n_nc.setdefault(k, v['relays_nc'])
        b_nc.setdefault(k, v['bw_nc'])
    top_num = sorted(n, key=n.get, reverse=True)[:10]
    top_bw = sorted(b, key=b.get, reverse=True)[:10]
    top_num_nc = sorted(n_nc, key=n_nc.get, reverse=True)[:10]
    top_bw_nc = sorted(b_nc, key=b_nc.get, reverse=True)[:10]

    ret = dict()
    ret.setdefault('relays', relays)
    ret.setdefault('rs', rs)
    ret.setdefault('num_relays', num_relays)
    ret.setdefault('num_relays_w_ipv6', num_relays_w_ipv6)
    ret.setdefault('nw_bandwidth', nw_bandwidth)
    ret.setdefault('ipv6_bandwidth', ipv6_bandwidth)
    ret.setdefault('v4_covered', v4_covered)
    ret.setdefault('v4_invalid', v4_invalid)
    ret.setdefault('v4_bw_covered', v4_bw_covered)
    ret.setdefault('v4_bw_invalid', v4_bw_invalid)
    ret.setdefault('bad_asn', bad_asn)
    ret.setdefault('bad_as_set', bad_as_set)
    ret.setdefault('bad_pl', bad_pl)
    ret.setdefault('bad_asn_and_pl', bad_asn_and_pl)
    ret.setdefault('top_num', top_num)
    ret.setdefault('top_bw', top_bw)
    ret.setdefault('top_num_nc', top_num_nc)
    ret.setdefault('top_bw_nc', top_bw_nc)
    ret.setdefault('asn4s', asn4s)

    return ret


def mar_guards_analysis(mar, mar_guards):
    mg_asns = mar_guards['asn4s'].keys()
    mg_a = []
    mg_a_none = []
    all_rs = mar['asn4s']
    for asn in mg_asns:
        r = mar_guards['asn4s'][asn]['relays']
        r_nc = mar_guards['asn4s'][asn]['relays_nc']
        if r == r_nc:
            all_r = all_rs[asn]['relays']
            mg_a_none.append([asn, r, all_r])
        mg_a.append([asn, r, r_nc])
    mg_a.sort(key=lambda x:x[2], reverse=True)
    #print(mg_a[:10])
    mg_a.sort(key=lambda x:x[1], reverse=True)
    #print(mg_a[:10])
    mg_a_none.sort(key=lambda x:x[1], reverse=True)
    print(mg_a_none)


def main(): 
    with open("archive_pickles/2020-12-13.pickle", 'rb') as f1:
        relays = pickle.load(f1)
        sept = get_data(relays)
    with open("archive_pickles/2021-01-13.pickle", 'rb') as f2:
        relays = pickle.load(f2)
        octo = get_data(relays)
    with open("archive_pickles/2021-02-13.pickle", 'rb') as f3:
        relays = pickle.load(f3)
        nov = get_data(relays)
    with open("archive_pickles/2021-03-13.pickle", 'rb') as f4:
        relays = pickle.load(f4)
        dec = get_data(relays)
    with open("archive_pickles/2021-04-13.pickle", 'rb') as f5:
        relays = pickle.load(f5)
        jan = get_data(relays)
    with open("archive_pickles/2021-05-13.pickle", 'rb') as f6:
        relays = pickle.load(f6)
        feb = get_data(relays)
    with open("archive_pickles/2021-06-13.pickle", 'rb') as f7:
        relays = pickle.load(f7)
        mar = get_data(relays, guards=False)
        mar_guards = get_data(relays, guards=True)
    
    adl_cov(mar['num_relays'], (mar['v4_covered'] + mar['v4_invalid']), mar['top_num_nc'], mar['asn4s'])
    
    months = [sept, octo, nov, dec, jan, feb, mar]
    #labels = ['2020-09-13', '2020-10-13', '2020-11-17', '2020-12-13', '2021-01-13', '2021-02-17', '2021-03-13']

    # time = []
    # fps = set()
    # for mon in months:
    #     relays = mon['relays']
    #     fps.update([r.fp for r in relays])
    #     time.append(mon['rs'])
    # over_time = []
    # for fp in fps:
    #     fp_c = [fp]
    #     for t in time:
    #         if fp not in t:
    #             fp_c.append('x')
    #         else:
    #             fp_c.append(t[fp])
    #     over_time.append(fp_c)

    # added = []
    # added_fps = set()
    # for a in over_time:
    #     fp = a[0]
    #     cur = a[1]
    #     for i in range(2, 8):
    #         if cur == 'nc' and a[i] in ['v', 'ia', 'iap', 'ip']:
    #             added.append(a)
    #             added_fps.add(a[0])
    #             continue
    #         cur == a[i]
    # print(len(added))
    # now_have = 0
    # now = set()
    # for ad in added:
    #     if ad[0] in now:
    #         continue
    #     now.add(ad[0])
    #     if ad[7] in ['v', 'ia', 'iap', 'ip']:
    #         now_have += 1
    # print(now_have)

    # fs = []
    # ps = []
    # ns = []
    # aa = []
    # for mon in months:
    #     full = set()
    #     partial = set()
    #     none = set()
    #     asns = mon['asn4s'].keys()
    #     a = []
    #     for asn in asns:
    #         r = mon['asn4s'][asn]['relays']
    #         r_nc = mon['asn4s'][asn]['relays_nc']
    #         if r_nc == 0:
    #             full.add(asn)
    #         elif r == r_nc:
    #             none.add(asn)
    #         else:
    #             partial.add(asn)
    #         a.append([asn, r, r_nc])
    #     f = len(full)
    #     p = len(partial)
    #     n = len(none)
    #     a = len(asns)
    #     c = f + p
    #     # print('full: {} ({} / {}), partial: {} ({} / {}), none: {} ({} / {}))'.format((f/c), f, c, (p/c), p, c, (n/a), n, a))
    #     fs.append(full)
    #     ps.append(partial)
    #     ns.append(none)
    #     aa.append(a)
    
    
    # mar_as_by_nc = aa[-1]
    # mar_as_by_nc.sort(key=lambda x:x[2], reverse=True)
    # print(mar_as_by_nc[:10])
    # mar_as_by_r = aa[-1]
    # mar_as_by_r.sort(key=lambda x:x[1], reverse=True)
    # print(mar_as_by_r[:10])

    # num_relays = mar['num_relays']
    # v4_covered = mar['v4_covered'] + mar['v4_invalid']
    # v4_uncovered = num_relays - v4_covered
    # #print('# IPv4 Protected Relays: {} ({} / {})'.format((v4_covered / num_relays), v4_covered, num_relays))
    
    # num_relays = mar_guards['num_relays']
    # v4_covered = mar_guards['v4_covered'] + mar_guards['v4_invalid']
    # v4_covered_w_partial = v4_covered 
    # n_partial = 0
    # for asn in partial:
    #     if asn not in mar_guards['asn4s']:
    #         continue
    #     v4_covered_w_partial += mar_guards['asn4s'][asn]['relays_nc']
    #     n_partial += mar_guards['asn4s'][asn]['relays_nc']
    
    # v4_covered_w_partial = v4_covered 
    # n_partial = 0
    # for asn in partial:
    #     v4_covered_w_partial += mar['asn4s'][asn]['relays_nc']
    #     n_partial += mar['asn4s'][asn]['relays_nc']
    # #print('# IPv4 Uncovered Relays: {} ({} / {})'.format((n_partial / v4_uncovered), n_partial, v4_uncovered) )
    # #print('# IPv4 Protected Relays (if partial coverage becomes full): {} ({} / {})'.format((v4_covered_w_partial / num_relays), v4_covered_w_partial, num_relays) )
    

if __name__ == '__main__':
    sys.exit(main())