from util import *
import time
import ipaddress
import argparse
import sys

def parse_arguments(args):
    """
    parses command line arguments into variable to be used in the main function 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("start_date", help="date in year-mo-da-hr format")
    parser.add_argument("end_date", help="date in year-mo-da-hr format")
    parser.add_argument("num_clients", help="number of clients")
    # parser.add_argument("asns", help="pickle with asns: archive_pickles/year-mo-dy-00-asns.pickle")
    return parser.parse_args(args)


def main(args):
    """
    main function of the guard simulator. Uses vanilla Tor guard selection
    algorithm to simulate the selection process over a time duration and output a 
    graph named L1Graph.png containing the load balance, client roa coverage etc for the simulated network. 

    :param start_date: (str) start date in year-mo-da-hr format
    :param end_date: (str) end date in year-mo-da-hr format
    :param num_clients: (int) the number of client objects for the simulation, larger number will reflect a more accurate performance but will take 
    longer time to process 
    """
    # timer
    tic = time.perf_counter()
    # process args
    args = parse_arguments(args)
    sd = args.start_date.split('-')
    ed = args.end_date.split('-')

    # change date argument into integer
    for i in range(4):
        sd[i] = int(sd[i])
        ed[i] = int(ed[i])
    # simulation variables
    start_date = datetime(sd[0], sd[1], sd[2], sd[3])
    end_date = datetime(ed[0], ed[1], ed[2], ed[3])
    num_clients = int(args.num_clients)

    # set up clients
    clients = list()
    for x in range(0, num_clients):
        client = Client()
        clients.append(client)

    # set up path
    p = os.getcwd()
    path = os.path.split(p)[0]
    path = path + '/rpkicoverage/processed/'
    # calculations

    num_hrs = ((end_date - start_date).days * 24)
 
    ideal_bw = 1 / num_clients
    # arrays for graphs

    num_guards = np.zeros((num_clients, num_hrs))       # churn array
    p_bw = np.zeros((num_clients, num_hrs))             # load balance array
    # get an num_clients by num_hrs matrix
    p_roa = []                                          # ROA coverage array
    p_roa_bw = []                                       # ROA coverage percent of bandwidth array
    roa_coverage = np.zeros((num_clients, num_hrs))     # ROA coverage by client
    # p_roa_mlpl = np.zeros((num_clients, num_hrs))     # ROA coverage and ML = PL array
    # index2 -> for hour
    i2 = 0
    # use datespan to iterate through every hour bt start and end date

    C_w_CG = []

    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
        
        if t.strftime('%H') == '00':
            print(t)
        # index1 -> for client
        i1 = 0
        # pull consensus file and update GUARDS --- if no consensus, don't update GUARDS
        load_consensus(path, t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), t.strftime('%H')) 
        # update each client
        for client in clients:
            client.on_consensus(t)
            # print('i1: ', i1)
            # print('i2: ', i2)
            # print(num_guards)
            num_guards[i1, i2] = len(client.guard_list)
            i1 += 1
        i1 = 0
        # calculate total bw for hour
        total_bw = calculate_total_bw(clients)
        # counters for ROA coverage
        p_bw_covered = 0
        p_covered = 0
        # p_mlpl = 0
        # second loop; stores each client's percent of the bw
        for client in clients:
            c_p_bw = (client.guard_list[-1].bw / CUR_GUARDS[client.guard_list[-1].fp]) / total_bw
            p_bw[i1, i2] = (c_p_bw - ideal_bw)
            # p_bw[i1, i2] = c_p_bw
            roa = client.guard_list[-1].ipv4_roa
            if roa is not None:
                p_covered += 1
                p_bw_covered += c_p_bw
                roa_coverage[i1, i2] = 1
            i1 += 1

        p_roa.append(p_covered/num_clients)
        # p_roa_mlpl.append(p_mlpl/num_clients)
        p_roa_bw.append(p_bw_covered)
        i2 += 1
    # timer
    toc = time.perf_counter()
    # print(toc - tic)

    ##### GRAPHING ######

    # graphing calculations
    max_p_bw = np.max(p_bw)
    min_p_bw = np.min(p_bw)
    max_guards = np.max(num_guards)
    h = np.arange(num_hrs)

    # creating plots
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)
    fig.suptitle(start_date.strftime('%m/%d/%Y') + ' to ' + end_date.strftime('%m/%d/%Y') + ', ' + str(num_clients) + ' clients')
    '''ax1 = axes[0,0]
    ax2 = axes[0,1]
    ax3 = axes[1,0]
    ax4 = axes[1,1]'''

    # churn IQR
    tsplot(h, num_guards, ax1, n=1, percentile_min=25, percentile_max=75, plot_median=False, plot_mean=False, color='g', line_color='navy', alpha=0.3)
    # churn 90% interval
    tsplot(h, num_guards, ax1, n=1, percentile_min=5, percentile_max=95, plot_median=False, plot_mean=True, color='g', line_color='navy', alpha=0.3)

    # load balance IQR
    tsplot(h, p_bw, ax2, n=1, percentile_min=25, percentile_max=75, plot_median=False, plot_mean=False, color='g', line_color='navy', alpha=0.3)
    # load balance 90% interval
    tsplot(h, p_bw, ax2, n=1, percentile_min=5, percentile_max=95, plot_median=False, plot_mean=True, color='g', line_color='navy', alpha=0.3)

    ax3.plot(h, p_roa)
    print(p_roa)
 
    # ax3.plot(h, p_ml_eq_pl)
    ax4.plot(h, p_roa_bw)

    # x axis ticks
    num_weeks = num_hrs // (24 * 7)
    hrs_week = 24 * 7
    xticks = []
    xtick_labels = []
    for x in range(0, num_weeks+1):
        xticks.append(hrs_week * x)
        label = start_date + timedelta(days=7) * x
        xtick_labels.append(label.strftime('%m/%d'))

    # labels, ticks
    ax1.set(ylabel='Churn', xlim=(0, num_hrs), ylim=(0, max_guards))
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(xtick_labels)
    ax2.set(ylabel='Load Balance', xlim=(0, num_hrs), ylim=(min_p_bw, max_p_bw))
    ax2.set_xticks(xticks)
    ax2.set_xticklabels(xtick_labels)
    ax3.set(ylabel='% Clients Covered', xlim=(0, num_hrs), ylim=(0, 1))
    ax4.set(ylabel='% BW Covered', xlim=(0, num_hrs), ylim=(0, 1))
    plt.xticks(rotation=90)
    # show plot
    plt.savefig("L1Graph.png")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
