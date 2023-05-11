from util import *
import time
import ipaddress
import argparse
import sys
from distributeUser import *
from ASNrov import *

def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("start_date", help="date in year-mo-da-hr format")
    parser.add_argument("end_date", help="date in year-mo-da-hr format")
    parser.add_argument("num_clients", help="number of clients")
    parser.add_argument("selection_algo", help="relay select method: vanilla, discount(e.g. 0.7), matching")
    parser.add_argument("csv_file", help="csv file for roa validation")
    parser.add_argument("multi_month_mean", help="True for multiple month analysis, False for consecutive hour analysis")
    parser.add_argument("multi_month_list", help="list of dates interval for each month")
    # parser.add_argument("asns", help="pickle with asns: archive_pickles/year-mo-dy-00-asns.pickle")
    return parser.parse_args(args)

def graph_LB_CDF(p_bw, make_pickle = True, make_graph = False, name = "loadBalanceCDF.png"):
    #graph snapshot of loadbalance in the first hour 
    """
    graph and pickle the load balance stats for a consensus file after running the simulation 
    :param p_bw: result from the guard_sim main function, input the same vairbale into this function to make graph and pickle file 
    :param make_pickle: (boolean) whether to make pickle of the load balance data 
    :param make_graph: (boolean) whether to make graph of Load Balance, save to current directory 
    :param name: (string) name of the graph is make_graph = True
    """
    loadBalanceSnap = []
    for row in p_bw:
        loadBalanceSnap.append(row[0])
    x = np.sort(loadBalanceSnap)
    y = np.arange(len(loadBalanceSnap))/float(len(loadBalanceSnap))
    if make_pickle:
        with open('matchingLB09Full.pickle', 'wb') as pf:
            pickle.dump(x, pf)
            pickle.dump(y, pf)
    if make_graph:
        plt.xlabel('Network Load Balance')
        plt.ylabel('CDF of Clients')
        plt.title('CDF of load balance')
        plt.plot(x,y,marker = 'o')
        plt.savefig(name)

def graph_ROACoverage_CDF(p_roa, make_pickle = True,make_graph = False, name = "ROACoverageCDF.png"):
    """
    graph and pickle the ROA CDF coverage stats for a consensus file after running the simulation 
    :param p_roa: result from the guard_sim main function, input the same vairbale into this function to make graph and pickle file 
    :param make_pickle: (boolean) whether to make pickle of the load balance data 
    :param make_graph: (boolean) whether to make graph of Load Balance, save to current directory 
    :param name: (string) name of the graph is make_graph = True
    """
    x = np.sort(p_roa)
    y = np.arange(len(p_roa))/float(len(p_roa))
    if make_pickle:
        with open('2023ROAshort.pickle', 'wb') as pf:
            pickle.dump(x, pf)
            pickle.dump(y, pf)
    if make_graph:
        plt.xlabel('% Clients Covered')
        plt.ylabel('CDF of Coverage')
        plt.title('% Clients Covered Matching new Param')
        plt.plot(x,y,marker = 'o')
        plt.savefig(name)
    
def graph_ROACoverage(h, p_roa, make_pickle = True,make_graph = True, name = "0.5ROACoverage2023.png"):
    """
    graph and pickle the ROA coverage stats for a consensus file after running the simulation 
    :param p_roa: result from the guard_sim main function, input the same vairbale into this function to make graph and pickle file 
    :param make_pickle: (boolean) whether to make pickle of the load balance data 
    :param make_graph: (boolean) whether to make graph of Load Balance, save to current directory 
    :param name: (string) name of the graph is make_graph = True
    """
    
    
    if make_graph:
        x = range(len(h))
        for d in p_roa:
            d = d *100
        plt.xlabel('Date')
        plt.ylabel('Client Coverage %')
        plt.title('Percent of Clients with ROA Covered Guard')
        plt.plot(x,p_roa,marker = 'o')
        plt.xticks(x, h, rotation ='vertical')
        plt.savefig(name)
    if make_pickle:
        with open('2023ROA0.5.pickle', 'wb') as pf:
            pickle.dump(h, pf)
            pickle.dump(p_roa, pf)

def graph_roa_rov_matching(h, p_roa_rov, p_total_rov,algo,  make_pickle = True, make_graph = False):
    """
    graph and pickle the ROA ROV matching coverage stats for a consensus file after running the simulation 
    :param p_roa_rov: result from the guard_sim main function, input the same vairbale into this function to make graph and pickle file 
    :param algo: specify the guard selection algo used
    :param make_pickle: (boolean) whether to make pickle of the load balance data 
    :param make_graph: (boolean) whether to make graph of Load Balance, save to current directory 
    :param name: (string) name of the graph is make_graph = True
    """
    if make_pickle:
        with open(algo + '2023ROAROVLowLB0.20.1.pickle', 'wb') as pf:
            pickle.dump(h, pf)
            pickle.dump(p_roa_rov, pf)
            pickle.dump(p_total_rov, pf)
            pickle.dump(algo, pf)
    if make_graph:
        print("length of h:", len(h))
        plt.xlabel('Date')
        plt.ylabel('Percent of Client that has ROA and ROV matching')
        x = range(len(h))
        plt.title(algo + ': Tor Percent of Client with ROA and ROV matching 1000 Clients')
        plt.plot(x,p_roa_rov,marker = 'o', label = "Matching Algorithm")
        plt.plot(x, p_total_rov, marker = '.', label = "Upper Bound")
        plt.xticks(x, h, rotation ='vertical')
        plt.legend()
        plt.savefig(algo + 'RoaRovAVG2023NewParam.png',bbox_inches='tight')

def main(args):
    """
    main function of the simulation that uses the util.py and graphing function above to carry out the simulation.
    add graphing functions at the end of the main function to graph and make pickle file 
    sample command for multiple months:
    python guard_sim.py 2022-10-13-00 2022-10-14-00 typicalTOR1000Clients2023.pickle 0.5 "20220813.csv,20220913.csv, 
    20221013.csv, 20221113.csv, 20221213.csv, 20230113.csv, 20230213.csv" True "2022-08-13-00, 2022-08-14-00, 2022-09-13-00,
    2022-09-14-00,2022-10-13-00,2022-10-14-00, 2022-11-13-00, 2022-11-14-00, 2022-12-13-00, 2022-12-14-00, 2023-01-13-00, 
    2023-01-14-00, 2023-02-13-00, 2023-02-14-00"
    """
    # timer
    tic = time.perf_counter()
    # process args
    args = parse_arguments(args)
    multiMonth = args.multi_month_mean
    
    if multiMonth == "True":
        dates_list = args.multi_month_list.split(",")
        csv_list = args.csv_file.split(",")
        for d in csv_list:
            print(d)
        numDates = len(dates_list)
        dates_list_formatted = []
        for i in range(0,numDates,2):
            dates_list_formatted.append([dates_list[i],dates_list[i+1]])
        print(dates_list_formatted)
        avg_rov = []
        avg_roa = []
        avg_total = []
        h = []
        for i in range(len(dates_list_formatted)):

            sd = dates_list_formatted[i][0].split('-')
            ed = dates_list_formatted[i][1].split('-')

            selection_algo = args.selection_algo
            csv = csv_list[i]
            # change date argument into integer
            for j in range(4):
                sd[j] = int(sd[j])
                ed[j] = int(ed[j])
            # simulation variables
            start_date = datetime(sd[0], sd[1], sd[2], sd[3])
            h.append(start_date)
            end_date = datetime(ed[0], ed[1], ed[2], ed[3])
            
            try:
                num_clients = int(args.num_clients)
                clients = assignASN(num_clients, countries, cweights, selection_algo, csv)[0]
            except ValueError:
                num_clients = args.num_clients
                if "pickle" in num_clients:
                    file = open(num_clients, 'rb')
                    clients = pickle.load(file)
                num_clients = len(clients)

                if selection_algo == "vanilla":
                    for c in clients:
                        c.selection_algo = "vanilla"
                elif selection_algo == "matching":
                    for c in clients:
                        c.selection_algo = 'matching'
                else:
                    for c in clients:
                        c.selection_algo = selection_algo
            # set up clients
            

            # set up path
            p = os.getcwd()
            path = os.path.split(p)[0]
            path = path + '/processed/'
            # calculations

            num_hrs = ((end_date - start_date).days * 24)
        
            ideal_bw = 1 / num_clients


            #record each client every hour on the specified data 
            # get an num_clients by num_hrs matrix
            num_guards = np.zeros((num_clients, num_hrs))       # churn array
                                    #rows,      col 
            p_bw = np.zeros((num_clients, num_hrs))             # load balance array
            roa_rov_coverage = np.zeros((num_clients, num_hrs))
            roa_coverage = np.zeros((num_clients, num_hrs))     # ROA coverage by client    

        #----------------------------------------------------------------------------------------------

            #record the hourly average of all clients on the specified data 
            p_roa = []                                          # ROA coverage array
            p_roa_bw = []                                       # ROA coverage percent of bandwidth array
            p_roa_rov = []                                      #ROA and ROV matched array 
            p_rov_matched = []                                #percent of rov that are matched
            p_total_rov = []

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
                    num_guards[i1, i2] = len(client.guard_list)
                    i1 += 1
                i1 = 0
                # calculate total bw for hour
                total_bw = calculate_total_bw(clients)
                # counters for ROA coverage
                p_bw_covered = 0
                p_covered = 0
                p_roa_rov_covered = 0
                totalROV = 0
                # second loop; stores each client's percent of the bw
        
                for client in clients:
                    c_p_bw = (client.guard_list[-1].bw / CUR_GUARDS[client.guard_list[-1].fp]) / total_bw
                    #         (clients current guard bw / num of clients in this guard) / total network bandwidth of this hour 
                    p_bw[i1, i2] = (c_p_bw - ideal_bw)
                    #record how much each client's bandwidth differs from ideal bandwidth 
                    #recording what percent of total network bandwidth the current client takes and takes difference from the ideal bandwidth, which is equally distributed among all clients 
                        # ideal_bw = 1 / num_clients
                    if client.guard_list[-1].asn != None:
                        guard_asn = client.guard_list[-1].asn[0]
                    else:
                        guard_asn = None
                    roa = client.guard_list[-1].ipv4_roa
                    
                    if check_rov(client.AS.ASN) or check_rov(guard_asn):
                        totalROV += 1
                        
                    
                    
                    
                    if check_rov(client.AS.ASN) and roa != None:
                        roa_rov_coverage[i1, i2] = 1
                        p_roa_rov_covered += 1 
                        
                    elif check_rov(guard_asn) and client.roaCovered:
                        roa_rov_coverage[i1, i2] = 1
                        p_roa_rov_covered += 1 
                    
                    

                    if roa != None:
                        p_covered += 1
                        p_bw_covered += c_p_bw
                        roa_coverage[i1, i2] = 1
                        
                    i1 += 1
        
                
                p_roa.append(p_covered/num_clients)
                p_roa_bw.append(p_bw_covered)
                p_roa_rov.append(p_roa_rov_covered/num_clients)
                p_rov_matched.append(p_roa_rov_covered/num_clients)
                # print(p_roa_rov_covered/totalROV)

                p_total_rov.append(totalROV/num_clients)
                #append data for the hourly average variable 

                i2 += 1
            print("p_roa_rov: ", (sum(p_roa_rov)/len(p_roa_rov)) *100)
            

            print("p_total_rov: ", (sum(p_total_rov)/len(p_total_rov))*100)
      
            avg_rov.append((sum(p_roa_rov)/len(p_roa_rov))*100)
            avg_roa.append((sum(p_roa)/len(p_roa))*100)
            avg_total.append((sum(p_total_rov)/len(p_total_rov))*100)
        # graph_roa_rov_matching(h,avg_rov,avg_total,selection_algo, make_pickle = True, make_graph = True)
        graph_ROACoverage(h, avg_roa)
    else:
        sd = args.start_date.split('-')
        ed = args.end_date.split('-')

        selection_algo = args.selection_algo
        csv = args.csv_file
        # change date argument into integer
        for i in range(4):
            sd[i] = int(sd[i])
            ed[i] = int(ed[i])
        # simulation variables
        start_date = datetime(sd[0], sd[1], sd[2], sd[3])
        end_date = datetime(ed[0], ed[1], ed[2], ed[3])
        
        try:
            num_clients = int(args.num_clients)
            clients = assignASN(num_clients, countries, cweights, selection_algo, csv)[0]
        except ValueError:
            num_clients = args.num_clients
            if "pickle" in num_clients:
                file = open(num_clients, 'rb')
                clients = pickle.load(file)
            num_clients = len(clients)

            if selection_algo == "vanilla":
                for c in clients:
                    c.selection_algo = "vanilla"
            elif selection_algo == "matching":
                for c in clients:
                    c.selection_algo = 'matching'
        # set up clients
        

        # set up path
        p = os.getcwd()
        path = os.path.split(p)[0]
        path = path + '/processed/'
        # calculations

        num_hrs = ((end_date - start_date).days * 24)
    
        ideal_bw = 1 / num_clients


        #record each client every hour on the specified data 
        # get an num_clients by num_hrs matrix
        num_guards = np.zeros((num_clients, num_hrs))       # churn array
                                #rows,      col 
        p_bw = np.zeros((num_clients, num_hrs))             # load balance array
        roa_rov_coverage = np.zeros((num_clients, num_hrs))
        roa_coverage = np.zeros((num_clients, num_hrs))     # ROA coverage by client    

    #----------------------------------------------------------------------------------------------

        #record the hourly average of all clients on the specified data 
        p_roa = []                                          # ROA coverage array
        p_roa_bw = []                                       # ROA coverage percent of bandwidth array
        p_roa_rov = []                                      #ROA and ROV matched array 
        p_rov_matched = []                                #percent of rov that are matched
        p_total_rov = []

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
                num_guards[i1, i2] = len(client.guard_list)
                i1 += 1
            i1 = 0
            # calculate total bw for hour
            total_bw = calculate_total_bw(clients)
            # counters for ROA coverage
            p_bw_covered = 0
            p_covered = 0
            p_roa_rov_covered = 0
            totalROV = 0
            # second loop; stores each client's percent of the bw
    
            for client in clients:
                c_p_bw = (client.guard_list[-1].bw / CUR_GUARDS[client.guard_list[-1].fp]) / total_bw
                #         (clients current guard bw / num of clients in this guard) / total network bandwidth of this hour 
                p_bw[i1, i2] = (c_p_bw - ideal_bw)
                #record how much each client's bandwidth differs from ideal bandwidth 
                #recording what percent of total network bandwidth the current client takes and takes difference from the ideal bandwidth, which is equally distributed among all clients 
                    # ideal_bw = 1 / num_clients
                if client.guard_list[-1].asn != None:
                    guard_asn = client.guard_list[-1].asn[0]
                else:
                    guard_asn = None
                roa = client.guard_list[-1].ipv4_roa
                
                if check_rov(client.AS.ASN) or check_rov(guard_asn):
                    totalROV += 1
                    
                
                
                
                if check_rov(client.AS.ASN) and roa != None:
                    roa_rov_coverage[i1, i2] = 1
                    p_roa_rov_covered += 1 
                    
                elif check_rov(guard_asn) and client.roaCovered:
                    roa_rov_coverage[i1, i2] = 1
                    p_roa_rov_covered += 1 
                
                

                if roa != None:
                    p_covered += 1
                    p_bw_covered += c_p_bw
                    roa_coverage[i1, i2] = 1
                    
                i1 += 1
    
            
            p_roa.append(p_covered/num_clients)
            p_roa_bw.append(p_bw_covered)
            p_roa_rov.append(p_roa_rov_covered/num_clients)
            p_rov_matched.append(p_roa_rov_covered/num_clients)
            # print(p_roa_rov_covered/totalROV)

            p_total_rov.append(totalROV/num_clients)
            #append data for the hourly average variable 

            i2 += 1


        #---------------------------------------------------------------------------------
        #uncomment to graph all 4 specs on same axis 

        # # timer
        # toc = time.perf_counter()
        # # print(toc - tic)

        # ##### GRAPHING ######

        # # graphing calculations
        # max_p_bw = np.max(p_bw)
        # min_p_bw = np.min(p_bw)
        # # find the max and min of the p_bw(load balance matrix)

        # max_guards = np.max(num_guards)
        h = np.arange(num_hrs) #return arrag with num_hrs size and each is increment of 1 starting from zero 

        # # creating plots
        # fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)
        # fig.suptitle(start_date.strftime('%m/%d/%Y') + ' to ' + end_date.strftime('%m/%d/%Y') + ', ' + str(num_clients) + ' clients')
        # '''ax1 = axes[0,0]
        # ax2 = axes[0,1]
        # ax3 = axes[1,0]
        # ax4 = axes[1,1]'''

        # # churn IQR
        # tsplot(h, num_guards, ax1, n=1, percentile_min=25, percentile_max=75, plot_median=False, plot_mean=False, color='g', line_color='navy', alpha=0.3)
        # # churn 90% interval
        # tsplot(h, num_guards, ax1, n=1, percentile_min=5, percentile_max=95, plot_median=False, plot_mean=True, color='g', line_color='navy', alpha=0.3)

        # # load balance IQR
        # tsplot(h, p_bw, ax2, n=1, percentile_min=25, percentile_max=75, plot_median=False, plot_mean=False, color='g', line_color='navy', alpha=0.3)
        # # load balance 90% interval
        # tsplot(h, p_bw, ax2, n=1, percentile_min=5, percentile_max=95, plot_median=False, plot_mean=True, color='g', line_color='navy', alpha=0.3)

        # ax3.plot(h, p_roa)

    
        # # ax3.plot(h, p_ml_eq_pl)
        # ax4.plot(h, p_roa_bw)

        # # x axis ticks
        # num_weeks = num_hrs // (24 * 7)
        # hrs_week = 24 * 7
        # xticks = []
        # xtick_labels = []
        # for x in range(0, num_weeks+1):
        #     xticks.append(hrs_week * x)
        #     label = start_date + timedelta(days=7) * x
        #     xtick_labels.append(label.strftime('%m/%d'))

        # # labels, ticks
        # ax1.set(ylabel='Churn', xlim=(0, num_hrs), ylim=(0, max_guards))
        # ax1.set_xticks(xticks)
        # ax1.set_xticklabels(xtick_labels)
        # ax2.set(ylabel='Load Balance', xlim=(0, num_hrs), ylim=(min_p_bw, max_p_bw))
        # ax2.set_xticks(xticks)
        # ax2.set_xticklabels(xtick_labels)
        # ax3.set(ylabel='% Clients Covered', xlim=(0, num_hrs), ylim=(0, 1))
        # ax4.set(ylabel='% BW Covered', xlim=(0, num_hrs), ylim=(0, 1))
        # plt.xticks(rotation=90)
        # # show plot
        # #plt.savefig('guard_sim.png')
        
        
        graph_roa_rov_matching(h, p_roa_rov,p_total_rov,selection_algo, make_pickle = False, make_graph = True)
        # graph_ROACoverage_CDF(p_roa, make_pickle = False,make_graph = True, name = "param=1ROACoverageCDF.png")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
