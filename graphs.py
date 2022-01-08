from util import * 
import argparse
import sys
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

def print_data(num_relays, nw_bandwidth, v4_covered, v4_invalid, v4_bw_covered, v4_bw_invalid, v4_mlpl, v4_mlpl_valid, num_relays_w_ipv6, v6_covered, v6_mlpl, guards=False):
    if guards:
        # print out info if input file contains only guard
        print('# IPv4 Protected Guards: {} ({} / {})'.format((v4_covered / num_relays), v4_covered, num_relays) )
        print('BW IPv4 Protected Guards: {} ({} / {})'.format((v4_bw_covered / nw_bandwidth), v4_bw_covered, nw_bandwidth) )
        print('# IPv4 Protected Guards (Tight Equal length): {} ({} / {})'.format((v4_mlpl / num_relays), v4_mlpl, num_relays) )
        print('Valid ROAs: {} ({} / {})'.format((v4_covered / (v4_invalid+v4_covered)), v4_covered, (v4_invalid+v4_covered)) )

        
        # print('# Guards w/ IPv6 Address: {} ({} / {})'.format((num_relays_w_ipv6 / num_relays), num_relays_w_ipv6, num_relays) )
        # print('# IPv6 Protected Guards: {} ({} / {})'.format((v6_covered / num_relays_w_ipv6), v6_covered, num_relays_w_ipv6) )
        # print('# IPv6 Protected Guards (Tight): {} ({} / {})'.format((v6_mlpl / num_relays_w_ipv6), v6_mlpl, num_relays_w_ipv6) )
    else:
        # print out info for relays
        #ipv6_distribution = [v6_covered, (num_relays_w_ipv6 - v6_covered), (num_relays - num_relays_w_ipv6)]
        # print('# IPv4 Protected Relays: {} ({} / {})'.format(((v4_covered+v4_invalid) / num_relays), v4_covered, num_relays) )
        # print('BW IPv4 Protected Relays: {} ({} / {})'.format(((v4_bw_covered+v4_bw_invalid) / nw_bandwidth), v4_bw_covered, nw_bandwidth) )
        # print('# IPv4 Protected Relays (Tight Equal Length): {} ({} / {})'.format((v4_mlpl / num_relays), v4_mlpl, num_relays) )
        # print('# IPv4 Protected Relays (valid): {} ({} / {})'.format((v4_covered / num_relays), v4_covered, num_relays) )
        # print('BW IPv4 Protected Relays(valid): {} ({} / {})'.format((v4_bw_covered / nw_bandwidth), v4_bw_covered, nw_bandwidth) )
        # print('# IPv4 Protected Relays (Tight) (valid): {} ({} / {})'.format((v4_mlpl_valid / num_relays), v4_mlpl, num_relays) )
        # print('Valid ROAs: {} ({} / {})'.format((v4_covered / (v4_invalid+v4_covered)), v4_covered, (v4_invalid+v4_covered)) )
        # print('Invalid ROAs: {} ({} / {})'.format((v4_invalid / (v4_invalid+v4_covered)), v4_invalid, (v4_invalid+v4_covered)) )
        # print('# Relays w/ IPv6 Address: {} ({} / {})'.format((num_relays_w_ipv6 / num_relays), num_relays_w_ipv6, num_relays) )
        # print('# IPv6 Protected Relays: {} ({} / {})'.format((v6_covered / num_relays_w_ipv6), v6_covered, num_relays_w_ipv6) )
        # print('# IPv6 Protected Relays (Tight): {} ({} / {})'.format((v6_mlpl / num_relays_w_ipv6), v6_mlpl, num_relays_w_ipv6) )


        print('# IPv4 Protected Guards: {} ({} / {})'.format((v4_covered / num_relays), v4_covered, num_relays) )
        print('BW IPv4 Protected Guards: {} ({} / {})'.format((v4_bw_covered / nw_bandwidth), v4_bw_covered, nw_bandwidth) )
        print('# IPv4 Protected Guards (Tight Equal length): {} ({} / {})'.format((v4_mlpl / num_relays), v4_mlpl, num_relays) )
        print('Valid ROAs: {} ({} / {})'.format((v4_covered / (v4_invalid+v4_covered)), v4_covered, (v4_invalid+v4_covered)) )

    


def top_by_bw(top_bw_nc, asn4s, asn4s_nc, v4_bw_covered, nw_bandwidth, guards=False):
    # Top ASNs stacked bar for bandwdith
    bw_c = dict()
    # bandwidth with covered
    bw_nc = dict()
    # bandwidth not covered
    bw_all_sum = 0
    bw_nc_sum = 0

    # top_bw_nc: ASN->bandwidth
    # a is current ASN inside the dict
    # the following for loop tally up total bw and total bandwidth not covered
    for a in top_bw_nc:
        all = asn4s[a][1]
        nc = asn4s_nc[a][1]
        # asn -> [num relay, bandwidth]
        bw_all_sum += all
        bw_nc_sum += nc
        bw_c.setdefault(a, (all-nc))
        bw_nc.setdefault(a, nc)
    # v4_bw_covered is total covered bw, nw_bandwidth is total not covered bandwidth
    c_other = (v4_bw_covered - (bw_all_sum - bw_nc_sum))
    nc_other = ((nw_bandwidth - v4_bw_covered) - bw_nc_sum)
    # calculate how much total bandwith is covered or not covered among top 10 AS

    bw_c.setdefault('Other', c_other)
    bw_nc.setdefault('Other', nc_other)
    # add to top 10 dict of bandwith coverage

    bw_cov = list(bw_c.values())
    bw_ncov = list(bw_nc.values())
    # list of bandwith for covered and not covered

    labels = list(bw_c.keys())
    # print(labels)

    ordering = []
    for x in range(len(bw_cov)):
        ordering.append(bw_cov[x] + bw_ncov[x])
    # get the total bandwith covered+not covered and store in list called ordering
    # print(ordering)
    z1 = sorted(zip(ordering, bw_cov), key=lambda t:t[0], reverse=True)
    uz1 = list(zip(*z1))
    z2 = sorted(zip(ordering, bw_ncov), key=lambda t:t[0], reverse=True)
    uz2 = list(zip(*z2))
    z3 = sorted(zip(ordering, labels), key=lambda t:t[0], reverse=True)
    uz3 = list(zip(*z3))
    # print(uz3[1])
    labels = uz3[1]

    ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    fig, ax = plt.subplots()

    ax1 = ax.bar(ind, uz1[1])
    ax2 = ax.bar(ind, uz2[1], bottom=uz1[1], color='green')

    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        h1_l = float((float(h1) / float(nw_bandwidth)) * 100.0)
        h2_l = float((float(h2) / float(nw_bandwidth)) * 100.0)
        if h1 != 0:
            plt.text(r1.get_x() + r1.get_width() / 2., h1 + 100, "{:.2f}".format(h1_l), ha="center", va="top", color="black", fontsize=10)
        if h2 != 0:
            plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2, "{:.2f}".format(h2_l), ha="center", va="top", color="black", fontsize=10)

    ax.set(ylabel='Bandwidth (labeled: % Tor BW)', xlabel='ASN')
    ax.set_yscale('log')
    if guards:
        plt.suptitle('ASNs Ranked By Percent of Guard Bandwidth 2020-10-13')
    else:
        plt.suptitle('ASNs Ranked By Percent of Tor Bandwidth 2020-10-13')
    plt.setp(ax, xticks=ind, xticklabels=labels)
    plt.legend((ax1[0], ax2[0]), ('Covered', 'Not Covered'))
    plt.savefig("topbbw.jpg")


def top_by_relays(top_num_nc, asn4s, asn4s_nc, v4_covered, num_relays, guards=False):
    # Top ASNs stacked bar for number of relays
    d = dict()
    dd = dict()
    all_sum = 0
    nc_sum = 0
    p_all_sum = 0
    p_nc_sum = 0

    for i in range (0, 4):
        a = top_num_nc[i]
        # print(a)
        all = asn4s[a][0]
        nc = asn4s_nc[a][0]
        all_sum += all
        nc_sum += nc
        d.setdefault(a, (all-nc))
        dd.setdefault(a, nc)


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
        ordering.append(num_cov[x] + num_ncov[x])
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

    ind = np.arange(6)

    fig, ax = plt.subplots()

    ax1 = ax.bar(ind, cov)
    ax2 = ax.bar(ind, ncov, bottom=cov, color='green')

    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        if h1 != 0:
            plt.text(r1.get_x() + r1.get_width() / 2., h1 + 100, "%d" % h1, ha="center", va="top", color="black", fontsize=10)
        if h2 != 0:
            plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 + 140, "%d" % h2, ha="center", va="top", color="black", fontsize=10)
    ax.set_yscale('linear')
    if guards:
        ax.set(ylabel='Number of Guards', xlabel='ASN')
        plt.suptitle('Top ASNs Ranked by Number of Guards 2020-10-13')
    else:    
        ax.set(ylabel='Number of Relays', xlabel='ASN')
        plt.suptitle('AS Ranked by Number of Relays 2020-10-13')
    plt.setp(ax, xticks=ind, xticklabels=labels)
    plt.legend((ax1[0], ax2[0]), ('Covered', 'Not Covered'))
    plt.show()


def top_by_num_relays_guards(top_num_nc, asn4s, asn4s_nc, v4_covered, num_relays):
    # Top ASNs stacked bar for number of relays
    d = dict()
    dd = dict()
    all_sum = 0
    nc_sum = 0

    for a in top_num_nc:
        all = asn4s[a][0]
        nc = asn4s_nc[a][0]
        all_sum += all
        nc_sum += nc
        d.setdefault(a, (all-nc))
        dd.setdefault(a, nc)

    c_other = (v4_covered - (all_sum - nc_sum))
    nc_other = ((num_relays - v4_covered) - nc_sum)
    d.setdefault('Other', c_other)
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

    fig, ax = plt.subplots()

    ax1 = ax.bar(ind, cov)
    ax2 = ax.bar(ind, ncov, bottom=cov, color='green')

    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        if h1 != 0:
            plt.text(r1.get_x() + r1.get_width() / 2., h1, "%d" % h1, ha="center", va="top", color="black", fontsize=10)
        if h2 != 0 and (h1 + h2) < 100:
            plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 + 55, "%d" % h2, ha="center", va="top", color="black", fontsize=10)
        elif h2 != 0:
            plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2, "%d" % h2, ha="center", va="top", color="black", fontsize=10)

    ax.set(ylabel='Number of Guards', xlabel='ASN')
    ax.set_yscale('linear')
    plt.suptitle('Top ASNs Ranked by Number of Guards 2020-10-13')
    plt.setp(ax, xticks=ind, xticklabels=labels)
    plt.legend((ax1[0], ax2[0]), ('Covered', 'Not Covered'))
    plt.show()


def pie_plot(mydict):
    # calculate top 10 by number of relays and bandwidth
    n = dict()
    b = dict()
    for k, v in mydict.items():
        n.setdefault(k, v[0])
        b.setdefault(k, v[1])
    top_num = sorted(n, key=n.get, reverse=True)[:5]
    top_bw = sorted(b, key=b.get, reverse=True)[:5]
    # set up labels, num relays, and bandwidth lists; initialize 'Other'
    labels_num = []
    labels_num.append('Other')
    num = []
    num.append(0)
    labels_bw = []
    labels_bw.append('Other')
    bw = []
    bw.append(0)
    # loop through dict; if
    for k, v in mydict.items():
        if k in top_num:
            labels_num.append(k)
            num.append(v[0])
        else:
            num[0] += v[0]

        if k in top_bw:
            labels_bw.append(k)
            bw.append(v[1])
        else:
            bw[0] += v[1]

    temp = labels_num[3]
    labels_num[3] = labels_num[4]
    labels_num[4] = temp

    plt.figure(1, figsize=(20,10))
    cmap = plt.get_cmap('tab20')
    colors = [cmap(i) for i in np.linspace(0, 1, 8)]
    colors2 = colors[:4]
    colors2.extend(colors[6:])
    the_grid = GridSpec(1, 2)

    plt.subplot(the_grid[0, 0], aspect=1, title='Number of Relays')
    num_plot = plt.pie(num, labels=labels_num, autopct='%1.1f%%', colors=colors)

    plt.subplot(the_grid[0, 1], aspect=1, title='Bandwidth')
    bw_plot = plt.pie(bw, labels=labels_bw, autopct='%1.1f%%', colors=colors2)

    plt.suptitle('Relays Without ROA Coverage by ASN 2020-10-13', fontsize=16)
    plt.savefig("pie_plot.jpg")


def adl_cov(num_relays, v4_covered, top_num_nc, asn4s, asn4s_nc):
    """
    projection of additional coverage if AS with most uncovered relay would cover their IP space with ROA
    """
    # Top ASNs stacked bar for number of relays
    d = dict()
    dd = dict()
    all_sum = 0
    nc_sum = 0
    current = v4_covered / num_relays
    covered = []
    covered.append(current)

    for a in top_num_nc:
        all_relays = asn4s[a][0]
        nc = asn4s_nc[a][0]
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
        ordering.append(num_cov[x] + num_ncov[x])
    # zip(a,b) combine entry on a and b into a nested list
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

    ind = [0, 1, 2, 3, 4, 5]# ,6, 7, 8, 9, 10]


    fig, ax = plt.subplots(2, sharex=True)
    ax[0].plot(ind, covered, 'o-')
    ax[0].set_ylabel('% Relays Covered if AS Fully Adds ROA')
    ax[0].set_ylim(top=1)
    for x,y in zip(ind, covered):
        label = "{:.2f}".format(y *100) + '%'
        ax[0].annotate(label, (x,y), textcoords="offset points", xytext=(0,5), ha='center')

    ax1 = ax[1].bar(ind, cov)
    ax2 = ax[1].bar(ind, ncov, bottom=cov, color='green')

    for r1, r2 in zip(ax1, ax2):
        h1 = r1.get_height()
        h2 = r2.get_height()
        if h1 == 1:
            ax[1].text(r1.get_x() + r1.get_width() / 2., h1 + .45, "%d" % h1, ha="center", va="top", color="black", fontsize=10)
        elif h1 != 0:
            ax[1].text(r1.get_x() + r1.get_width() / 2., h1, "%d" % h1, ha="center", va="top", color="black", fontsize=10)
        if h2 != 0:
            ax[1].text(r2.get_x() + r2.get_width() / 2., h1 + h2 + ( (h1 + h2) * .5), "%d" % h2, ha="center", va="top", color="black", fontsize=10)

    ax[1].set_ylabel('Number of Relays')
    ax[1].set_xlabel('ASN')
    ax[1].set_yscale('log')
    plt.suptitle('Top ASNs with the Most Uncovered Relays 2021-03-13')
    plt.setp(ax, xticks=ind, xticklabels=labels)
    plt.legend((ax1[0], ax2[0]), ('Covered', 'Not Covered'))
    plt.savefig("adl_cov.png")


def adl_cov_guards(num_relays, v4_covered, top_num_nc, asn4s, asn4s_nc, n2):
    """
    graphs ROA coverage for guards if more AS were to cover their IP space 
    """
    all_nc = sorted(n2, key=n2.get, reverse=True)
    covered = []
    covered.append(v4_covered / num_relays)
    d = dict()
    # print(len(all_nc))
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
    plt.savefig("adl_cov_guards.jpg")


def adl_cov_bw(nw_bandwidth, v4_bw_covered, top_bw_nc, asn4s, asn4s_nc):
    """
    graphs bar plot of additional bandwidth covered by ROA, if top ROA AS were to fully cover their IP space 
    """
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
    # print(labels)

    ordering = []
    for x in range(len(bw_cov)):
        ordering.append(bw_cov[x] + bw_ncov[x])
    # print(ordering)
    z1 = sorted(zip(ordering, bw_cov), key=lambda t:t[0], reverse=True)
    uz1 = list(zip(*z1))
    z2 = sorted(zip(ordering, bw_ncov), key=lambda t:t[0], reverse=True)
    uz2 = list(zip(*z2))
    z3 = sorted(zip(ordering, labels), key=lambda t:t[0], reverse=True)
    uz3 = list(zip(*z3))
    # print(uz3[1])
    labels = uz3[1]

    ind = [0, 1, 2, 3, 4, 5]

    fig, ax = plt.subplots(2, sharex=True)
    print(ind)
    print(covered)
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
    plt.savefig("adl_cov_bw.jpg")


def invalid_roa(bad_asn, bad_pl, bad_asn_and_pl, v4_invalid):
    """
    graph the distribution of invalid reasons (mismatch ASN, max length violation, or both) across all invalid roa
    """
    labels = ['AS', 'ML', 'AS-ML']
    data = [bad_asn, bad_pl, bad_asn_and_pl]
    for i in range(3):
        labels[i] += ': ' + "{:.2%}".format(data[i]/v4_invalid)
    colors = ['blue', 'red', 'purple']
    fig1, ax1 = plt.subplots()
    ax1.pie(data, labels=labels, colors=colors)
    plt.savefig("invalid_roa.jpg")


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
    parser.add_argument("filename", help="consensus pickle with roas, in processed folder")
    parser.add_argument("guards", help="graph just guards (y/n)")
    # parser.add_argument("asns", help="pickle with asns: archive_pickles/year-mo-dy-00-asns.pickle")
    return parser.parse_args(args)


def main(args):

    r'''
    Put consensus file location and 'y' or 'n' indicating whether to only process guard relays as command line arguments.
    Analyze relays in 1 consensus file, including getting ROA coverage, IP prefix, ASN etc.
    Call graphing functions (all functions in this file excpet parse_arguments can produce a graph) at the end 
    of main function to graph various specs for this consensus file 

    Example Call: python graphs.py C:\Users\sunsi\Documents\GitHub\tor-rpki\processed\2021-06-01-06-processed.pickle n

    '''
    args = parse_arguments(args)
    
    # get consensus data + roa data + asn/prefix data
    with open(args.filename, 'rb') as f2:
        relays = pickle.load(f2)

    # if guards 
    g = False
    if args.guards == 'y':
        g = True
        relays = guards(relays)
    # relays are the var for loading pickled consensus file


    # initialize variables
    num_relays = len(relays) 
    # get total number of relays from the length of the relays list
    num_relays_w_ipv6 = 0
    nw_bandwidth = 0
    # total bandwith of the relays in the list
    ipv6_bandwidth = 0

    v4_covered = 0
    v4_invalid = 0
    v4_bw_covered = 0
    v4_bw_invalid = 0
    v4_mlpl = 0
    # number of v4 relay that has that prefix length = max length, won't be victum of more specific prefix hijack
    v4_mlpl_valid = 0


    v4_ml = dict()
    # dict containing max length of ip -> number of ip having this length
    v4_pl = dict()

    v6_covered = 0
    v6_bw_covered = 0
    v6_mlpl = 0

    # ipv6 maximum length
    v6_ml = dict()
    # ipv4 prefix length
    v6_pl = dict()

    asn4s = dict()
    # dictionary for all asn ipv4
    asn4s_nc = dict()
    # dictionary for asn ipv4 that is not covered by roa
    # asn -> [num relay, bandwidth]
    asn6s = dict()

    bad_asn = 0   
    bad_as_set = 0
    bad_pl = 0
    bad_asn_and_pl = 0
    invalids = dict()
    # dict containing invalid AS, ASN -> [0,0,0]
    # the list with 3 entry represent the 3 types of invalid states the relay in AS could have
    # first is ASN from web doesnt math ASN from ROA and prefix longer than maximum length
    # second is ASN doesnt match
    # third is prefix length > max length
    # otherwise the relay is valid

    # loop through all relays again
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
            print("relay asn：", relay.asn)
            # check if there is an roa and its validity
            if len(relay.asn) > 1:
                # relay.asn return a list supposedly with 1 entry which is the asn
                # make sure the format is valid, inherented this format from get_prefix_and_asn() in util.py
                print("invalid")
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
                if ml in v4_ml: v4_ml[ml] += 1
                else: v4_ml.setdefault(ml, 1)
                # prefix length distribution
                if pl in v4_pl: v4_pl[pl] += 1
                else: v4_pl.setdefault(pl, 1)  
        
        # asn ipv4
        asn = relay.asn
        # this asn var change each iteration, still in the for relay loop
        # iterate through ASN to update dictionary
        if asn is None:
            pass
        else:
            # check to see relay has ipv4 roa
            if relay.ipv4_roa is None:
                # if no ipv4 roa, add entry to notCovered dictionary
                # asn4s_nc is a dictionary with asn as keys and a 2 entry list as values, the list has num of relay in this AS and the total bandwidth
                if asn[0] not in asn4s_nc:
                    # setting the defaul format
                    asn4s_nc.setdefault(asn[0], [1, relay.bw])
                else:
                    # adding onto existing dictionary
                    asn4s_nc[asn[0]][0] += 1
                    asn4s_nc[asn[0]][1] += relay.bw
            # add to the total dictionary containing all ipv4 relays
            if asn[0] not in asn4s:
                asn4s.setdefault(asn[0], [1, relay.bw])
            else:
                asn4s[asn[0]][0] += 1
                asn4s[asn[0]][1] += relay.bw  

        # doing same calc for ipv6 as ipv4
        # ipv6
        if relay.ipv6 != '':
            num_relays_w_ipv6 += 1
            ipv6_bandwidth += relay.bw
            # ipv6 calculations
            if relay.ipv6_roa is not None:
                v6_bw_covered += relay.bw
                v6_covered += 1
                ml = relay.ipv6_roa[1]    # max length of ROA network
                pl = relay.ipv6_roa[2]    # prefix length of ROA network
                # max length == prefix length
                if ml == pl: v6_mlpl += 1
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
        
    length = 5
    #asn4s
    n = dict()
    # total number of relays in ipv4
    b = dict()
    # total bandwidth in ipv4
    for k, v in asn4s.items():
        n.setdefault(k, v[0])
        b.setdefault(k, v[1])
    top_num = sorted(n, key=n.get, reverse=True)[:length]
    # top_num: contain ASN -> number of relays; top 10 AS sorted by number of relay
    top_bw = sorted(b, key=b.get, reverse=True)[:length]
    # top_bw: contains ASN-> bandwidth; top 19 AS sorted by bandwidth

    #asn4s_nc
    n2 = dict()
    # number of relay not covered
    b2 = dict()
    # number of bandwidth not covered in ipv4
    for k, v in asn4s_nc.items():
        n2.setdefault(k, v[0])
        b2.setdefault(k, v[1])
    top_num_nc = sorted(n2, key=n2.get, reverse=True)[:length]
    # top_num_nc = top_num_nc[0:6]
    # sort by the value of n2 dictory from big to small
    #get the largest 10 entries in the dictionary
    top_bw_nc = sorted(b2, key=b2.get, reverse=True)[:length]
    # ASN->bandwidth
    # sort by the value of b2 dictory from big to small
    adl_cov(num_relays, v4_covered, top_num_nc, asn4s, asn4s_nc)
    # adl_cov(num_relays, (v4_covered+v4_invalid), top_num_nc, asn4s, asn4s_nc)
    # print_data(num_relays, nw_bandwidth, v4_covered, v4_invalid, v4_bw_covered, v4_bw_invalid, v4_mlpl, v4_mlpl_valid, num_relays_w_ipv6, v6_covered, v6_mlpl, g )

    # top_by_bw(top_bw_nc,asn4s,asn4s_nc,v4_bw_covered,nw_bandwidth)
    # invalid_roa(bad_asn,bad_pl,bad_asn_and_pl,v4_invalid)
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


# sample call:
# python graphs.py C:\Users\sunsi\Documents\GitHub\tor-rpki\processed\2021-06-01-06-processed.pickle n
