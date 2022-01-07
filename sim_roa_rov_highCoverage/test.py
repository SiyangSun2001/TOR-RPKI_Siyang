import pickle
import matplotlib.pyplot as plt


def graph_roaCovered_cdf(pfile1, pfile2, pfile3, pfile4, graphName):
   

        file = open(pfile1, 'rb')
        xd50 = pickle.load(file)
        yd50 = pickle.load(file)
        file.close()

        file = open(pfile2, 'rb')
        xd60 = pickle.load(file)
        yd60 = pickle.load(file)
        file.close()

        file = open(pfile3, 'rb')
        xd70 = pickle.load(file)
        yd70 = pickle.load(file)
        file.close()

        file = open(pfile4, 'rb')
        xVan = pickle.load(file)
        yVan = pickle.load(file)
        file.close()

        plt.xlabel('% Clients Covered')
        plt.ylabel('CDF of Coverage in 1 Month')
        plt.title('CDF of % Clients Covered by ROA 1000 Clients 2020-09-01 to 2020-09-05')
        
        plt.plot(xd50,yd50,marker = '.', color = 'blue', label = '50% Discount Selection')
        plt.plot(xd60,yd60,marker = '.', color = 'yellow', label = '60% Discount Selection')
        plt.plot(xd70,yd70,marker = '.', color = 'red', label = '70% Discount Selection')
        plt.plot(xVan,yVan,marker = '.', color = 'green', label = " Vanilla Guard Selection")

        plt.legend()
        plt.savefig(graphName+'.png')


def graph_LB_cdf(pfile1, pfile2, pfile3, pfile4, graphName):
        

        file = open(pfile1, 'rb')
        xd50 = pickle.load(file)
        yd50 = pickle.load(file)
        file.close()

        file = open(pfile2, 'rb')
        xd60 = pickle.load(file)
        yd60 = pickle.load(file)
        file.close()

        file = open(pfile3, 'rb')
        xd70 = pickle.load(file)
        yd70 = pickle.load(file)
        file.close()

        file = open(pfile4, 'rb')
        xVan = pickle.load(file)
        yVan = pickle.load(file)
        file.close()
        
        plt.xlabel('Network Load Balance')
        plt.ylabel('CDF of Clients')
        plt.title('CDF of Load Balance 1000 Clients 2020-09-01 to 2020-09-05')

        plt.plot(xd50,yd50,marker = '.', color = 'blue', label = '50% Discount Selection')
        plt.plot(xd60,yd60,marker = '.', color = 'yellow', label = '60% Discount Selection')
        plt.plot(xd70,yd70,marker = '.', color = 'red', label = '70% Discount Selection')
        plt.plot(xVan,yVan,marker = '.', color = 'green', label = " Vanilla Guard Selection")

        plt.legend()
        plt.savefig(graphName+'.png')

graph_roaCovered_cdf('0.5%ROAshort.pickle', '0.6%ROAshort.pickle', '0.7%ROAshort.pickle', 'vanilla%ROAshort.pickle', '%ROACoveredshort')