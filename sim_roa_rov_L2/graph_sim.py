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


def graph_LB_cdf(pfile1, pfile2, pfile3, pfile4, graphName):
        """
        function used to graph load balance of multiple simulation onto 1 graph using pickle file made when running each simulation. 
        generater pickle file in guard_sim.py graph_LB_CDF(). 
        
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

        # file = open('shortPickle/'+pfile3, 'rb')
        # xd70 = pickle.load(file)
        # yd70 = pickle.load(file)
        # file.close()

        # file = open('shortPickle/'+pfile4, 'rb')
        # xVan = pickle.load(file)
        # yVan = pickle.load(file)
        # file.close()
        
        plt.xlabel('Network Load Balance')
        plt.ylabel('CDF of Clients')
        plt.title('CDF of Load Balance 1000 Clients 2020-09-01 to 2020-09-05')

        plt.plot(xd50,yd50,marker = '.', color = 'blue', label = 'vanilla')
        plt.plot(xd60,yd60,marker = '.', color = 'yellow', label = 'roa rov matching')
        # plt.plot(xd70,yd70,marker = '.', color = 'red', label = '70% Discount Selection')
        # plt.plot(xVan,yVan,marker = '.', color = 'green', label = " Vanilla Guard Selection")

        plt.legend()
        plt.savefig(graphName+'.png')


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
        file = open(pickleLS[0], 'rb')
        h = pickle.load(file)
        p_roa_rov = pickle.load(file)
        p_total_rov = pickle.load(file)
        plt.plot(h, p_total_rov, marker = '.', label = "Upper Bound")
        file.close()
        for p in pickleLS:
                file = open(p, 'rb')
                h = pickle.load(file)
                p_roa_rov = pickle.load(file)
                p_total_rov = pickle.load(file)
                algo = pickle.load(file)
                plt.plot(h,p_roa_rov,marker = 'o', label = algo + " Algorithm")
        plt.legend()
        plt.savefig('RefractorParamRoaRovVanilla.png')       



# graph_roaCovered_cdf('0.5%ROAshort.pickle', '0.6%ROAshort.pickle', '0.7%ROAshort.pickle', 'VanillaROAshort.pickle', 'latexDiscountROA')