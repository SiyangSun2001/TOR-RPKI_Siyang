import numpy as np
import matplotlib.pyplot as plt
import pickle
# def barPlot():
#     # set width of bar
#     barWidth = 0.25
#     fig = plt.subplots(figsize =(12, 8))
    
#     # set height of bar
#     IT = [12, 30, 1, 8, 22]
#     ECE = [28, 6, 16, 5, 10]
#     CSE = [29, 3, 24, 25, 17]
    
#     # Set position of bar on X axis
#     br1 = np.arange(len(IT))
#     br2 = [x + barWidth for x in br1]
#     br3 = [x + barWidth for x in br2]
    
#     # Make the plot
#     plt.bar(br1, IT, color ='r', width = barWidth,
#             edgecolor ='grey', label ='IT')
#     plt.bar(br2, ECE, color ='g', width = barWidth,
#             edgecolor ='grey', label ='ECE')
#     plt.bar(br3, CSE, color ='b', width = barWidth,
#             edgecolor ='grey', label ='CSE')
    
#     # Adding Xticks
#     plt.xlabel('Branch', fontweight ='bold', fontsize = 15)
#     plt.ylabel('Students passed', fontweight ='bold', fontsize = 15)
#     plt.xticks([r + barWidth for r in range(len(IT))],
#             ['2015', '2016', '2017', '2018', '2019'])
    
#     plt.legend()
#     plt.savefig('barplot.png')

def scatter(LBfile, RRfile):
    """
    graphes the relationship between load balance of the percent of ROA ROV matching. 
    each dot in the scatter plot represent one parameter and its LB and ROA_ROV performance. The 
    graph is saved as scatter.png in the current directory. Input file are obtained from optimizeParam.py
    example call: scatter('PermLBResult.pickle', 'PermROA_ROVResult.pickle')

    :param LBfile: (string) filename of the load balance pickled file 
    :param RRfile: (string) filename of the ROA_ROV matching pickled file 
    """
    with open(LBfile, 'rb') as f:
        LB = pickle.load(f)
    #LB: a list of list containing parameter and LB of that parameter
    #e.g. [[0.6, 0.4, 1], 0.987646]
            #param         LB 

    with open(RRfile, 'rb') as f:
        roaROV = pickle.load(f)
    

    x = []
    y = []
    pTOLB = dict()
    pTOroarov = dict()
    for i in LB:
        pTOLB[tuple(i[0])] = i[1]
   
    for i in roaROV:
        pTOroarov[tuple(i[0])] = i[1]
    for i in LB:
        x.append(pTOroarov[tuple(i[0])])
        y.append(pTOLB[tuple(i[0])])
    plt.scatter(x, y)
    plt.xlabel('ROA ROV matching')
    plt.ylabel('Load Balance Expected Value')
    plt.title('Load Balance v.s. ROA ROV matches for Qualified Param (Normal Coverage)')
    plt.savefig('scatter.png')



def scatterWload(LBfile, RRfile, networkLoad):
    """
    same function as the scatter(), but draws a performance threshold for different network load. 
    Parameters above the benchmark means that at the specific network load, these parameters will not affect the load balance and 
    cause congestion comparing to vanilla TOR. 

    :param LBfile: (string) filename of the load balance pickled file 
    :param RRfile: (string) filename of the ROA_ROV matching pickled file 
    :param networkLoad: (float) how much of the total possible bandwith are used in the TOR network 

    """
    with open(LBfile, 'rb') as f:
        LB = pickle.load(f)
        
    with open(RRfile, 'rb') as f:
        roaROV = pickle.load(f)
    

    x = []
    y = []
    pTOLB = dict()
    pTOroarov = dict()
    for i in LB:
        i[1] = i[1]/networkLoad

    for i in LB:
        pTOLB[tuple(i[0])] = i[1]
   
    for i in roaROV:
        pTOroarov[tuple(i[0])] = i[1]
    for i in LB:
        x.append(pTOroarov[tuple(i[0])])
        y.append(pTOLB[tuple(i[0])])
    plt.scatter(x, y)
    plt.plot(x, [1]*len(y), color = 'black', label = 'Performance Threshold')
    plt.xlabel('ROA ROV matching')
    plt.ylabel('Load Balance Expected Value')
    plt.title('Load Balance v.s. ROA ROV matches at Network Load ' + str(networkLoad*100) + '%')
    plt.legend()
    plt.savefig('load'+ str(networkLoad) + 'sctter.png')
# scatterWload(0.9)
#scatter()