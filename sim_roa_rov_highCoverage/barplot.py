import numpy as np
import matplotlib.pyplot as plt
import pickle
def barPlot():
    # set width of bar
    barWidth = 0.25
    fig = plt.subplots(figsize =(12, 8))
    
    # set height of bar
    IT = [12, 30, 1, 8, 22]
    ECE = [28, 6, 16, 5, 10]
    CSE = [29, 3, 24, 25, 17]
    
    # Set position of bar on X axis
    br1 = np.arange(len(IT))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]
    
    # Make the plot
    plt.bar(br1, IT, color ='r', width = barWidth,
            edgecolor ='grey', label ='IT')
    plt.bar(br2, ECE, color ='g', width = barWidth,
            edgecolor ='grey', label ='ECE')
    plt.bar(br3, CSE, color ='b', width = barWidth,
            edgecolor ='grey', label ='CSE')
    
    # Adding Xticks
    plt.xlabel('Branch', fontweight ='bold', fontsize = 15)
    plt.ylabel('Students passed', fontweight ='bold', fontsize = 15)
    plt.xticks([r + barWidth for r in range(len(IT))],
            ['2015', '2016', '2017', '2018', '2019'])
    
    plt.legend()
    plt.savefig('barplot.png')

def scatter():

    with open('QualiLBResult.pickle', 'rb') as f:
        LB = pickle.load(f)
        
    with open('QualiROA_ROVResult.pickle', 'rb') as f:
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
    plt.title('Load Balance v.s. ROA ROV matches for Qualified Param (High Coverage)')
    plt.savefig('sctter.png')
scatter()