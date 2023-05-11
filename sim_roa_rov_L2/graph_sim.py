import pickle
import matplotlib.pyplot as plt


def graph_roaCovered_cdf(pfile1, pfile2, pfile3, pfile4, graphName):
        """
        function used to graph ROA coverage of multiple simulation onto 1 graph using pickle file made when running each simulation. 
        generater pickle file in guard_sim.py graph_ROACoverage_CDF(). 
        
        :param pfile1: (string) name to pickle file for 1 simulation, same for the other 3 
        :param graphName: (string) name of the resulting graph  

        """

        file = open('shortPickle/'+pfile1, 'rb')
        xd50 = pickle.load(file)
        yd50 = pickle.load(file)
        file.close()

        file = open('shortPickle/'+pfile2, 'rb')
        xd60 = pickle.load(file)
        yd60 = pickle.load(file)
        file.close()

        file = open('shortPickle/'+pfile3, 'rb')
        xd70 = pickle.load(file)
        yd70 = pickle.load(file)
        file.close()

        file = open('shortPickle/'+pfile4, 'rb')
        xVan = pickle.load(file)
        yVan = pickle.load(file)
        file.close()

        plt.xlabel('% Clients Covered')
        plt.ylabel('CDF of Coverage')
        plt.title('CDF of % Clients Covered by ROA 1000 Clients 2020-09-01 to 2020-09-05')
        
        plt.plot(xd50,yd50,marker = '.', color = 'blue', label = '50% Discount')
        plt.plot(xd60,yd60,marker = '.', color = 'yellow', label = '60% Discount')
        plt.plot(xd70,yd70,marker = '.', color = 'red', label = '70% Discount')
        plt.plot(xVan,yVan,marker = '.', color = 'green', label = "Vanilla Guard Selection")
        
        plt.legend()
        plt.savefig(graphName+'.png')


def graph_LB_cdf(graphName):
        """
        function used to graph load balance of multiple simulation onto 1 graph using pickle file made when running each simulation. 
        generater pickle file in guard_sim.py graph_LB_CDF(). 
        
        :param pfile1: (string) name to pickle file for 1 simulation, same for the other 3 
        :param graphName: (string) name of the resulting graph  

        """

        file = open('/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/2023ROA0.5.pickle', 'rb')
        xd50 = pickle.load(file)
        yd50 = pickle.load(file)
        file.close()

        file = open('/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/2023ROA0.7.pickle', 'rb')
        xd60 = pickle.load(file)
        yd60 = pickle.load(file)
        file.close()

        file = open('/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/2023ROA0.9.pickle', 'rb')
        xd70 = pickle.load(file)
        yd70 = pickle.load(file)
        file.close()

        file = open('/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/2023ROAVanilla.pickle', 'rb')
        xVan = pickle.load(file)
        yVan = pickle.load(file)
        file.close()
        
        x = range(len(xVan))

        plt.xlabel('Date')
        plt.ylabel('% Tor Clients')
        plt.title('Percentage of Clients with ROA Covered Guard')

        plt.plot(x,yd50,marker = '.', color = 'blue', label = '50% Discount')
        plt.plot(x,yd60,marker = '.', color = 'yellow', label = '70% Discount')
        plt.plot(x,yd70,marker = '.', color = 'red', label = '90% Discount')
        plt.plot(x,yVan,marker = '.', color = 'green', label = " Vanilla Guard Selection")
        plt.xticks(x, xVan, rotation ='vertical')
        plt.legend()
        plt.savefig(graphName+'.png', bbox_inches='tight')


def graph_roa_rov_matching(pickleLS):
        """
        function used to graph ROA ROV matching of multiple simulation onto 1 graph using pickle file made when running each simulation. 
        generater pickle file in guard_sim.py graph_roa_rov_matching(). 
        
        :param pfile1: (string) name to pickle file for 1 simulation, same for the other 3 
        :param graphName: (string) name of the resulting graph  

        """
        plt.xlabel('Time by the hour')
        plt.ylabel('Percent of Client that has ROA and ROV matching')
        plt.title('Tor Percent of Client with ROA and ROV matching 1000 Clients')
        file = open(pickleLS[1], 'rb')
        h = pickle.load(file)
        p_roa_rov = pickle.load(file)
        p_total_rov = pickle.load(file)
        plt.plot(h, p_total_rov, marker = '.', label = "Upper Bound")
        file.close()
        label = [" 94% LB", " 75% LB", ""]
        count = 0
        for p in pickleLS:
                file = open(p, 'rb')
                h = pickle.load(file)
                p_roa_rov = pickle.load(file)
                p_total_rov = pickle.load(file)
                algo = pickle.load(file)
                plt.plot(h,p_roa_rov,marker = 'o', label = algo + label[count] + " Algorithm")
                count += 1
        plt.legend(bbox_to_anchor=(0, 1.02, 1.02, 0.3), loc="upper center", ncol=2)
        plt.tight_layout()
        plt.savefig('ROAROVVanillaVmatching.png')       


# graph_roa_rov_matching(["/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/matching2023ROAROVHighLBParam0.40.8.pickle", "/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/matching2023ROAROVLowLB0.20.1.pickle", "/home/ys3kz/TorPythonSimulator/TOR-RPKI_Siyang/sim_roa_rov_L2/vanilla2023ROAROV.pickle"])
# graph_roaCovered_cdf('0.5%ROAshort.pickle', '0.6%ROAshort.pickle', '0.7%ROAshort.pickle', 'VanillaROAshort.pickle', 'latexDiscountROA')

graph_LB_cdf("ROA Coverage of Clients.png")