import pickle 
from tabulate import tabulate
from itertools import permutations
import itertools

def intersection(lst1, lst2):
    '''
    return the intersection of two lists
    :param lst1: (list) first input list
    :param lst2: (list) second input list 

    :return: (list) intersect of lst1 and lst2

    '''
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

#give the permutation of parameters, the pool is the possible value to choose from 
#repeat is the number if param to permutate. 
def get_param_Permutation(pool):
    """
    given the possible values and number of item in each choice, return all possible permutations

    :param pool: *iterable, list, set or string etc 

    :return: (list) a list of the all possible permutations  
    """
    result = []
    for j in itertools.product(pool, repeat=3) :
        result.append(j)

    return result

#return the difference between 2 list 
def Diff(li1, li2):
        """
    return the difference of two lists
    :param lst1: (list) first input list
    :param lst2: (list) second input list 

    :return: (list) difference of lst1 and lst2

    """
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))



def analyzeParam(LBfilename, roa_rovFilename, ProaFilename):
    """
    This function filters the performance of different parameter based on load balance
    ROA_ROV matching percentage, and percent of client with ROA coverage. All 3 performance 
    are measured separately then filtered using a cutoff point. Then, the programs find the
    parameter that passed all 3 of the performance cutoff. Finally, a table is printed with 
    parameters that passed all 3 bench marks. The input file into this function is obtained from the 
    optimizeParam.py file. 

    :param LBfilename: (string) filename to the pickled file containing load balance performance of all parameters 
    :param roa_rovFilename: (string) filename to the pickled file containing ROA ROV matching performance of all parameters 
    :param ProaFilename: (string) filename to the pickled file containing percent of client covered by ROA  performance of all parameters 
    

    """
    #filter params through LB, roarov cutoff and roa coverage better than vanilla 

    #list to keep qualified paramter that passes the cutoff 
    qualifiedParamLB = []
    qualifiedParamRR = []
    qualifiedProa = []

    #dict that maps (param) -> performance, e.g. (0.1,0.1, 1) -> 0.98 
    LBDict = dict()
    RRDict = dict()
    ProaDict = dict()

    #threshold where we include this param into the qualified list 
    LBcutoff = 0.6
    RRcutoff = 0.06
    pROAcutoff = 0.5423
    #open each file and iterate to get the qualified param 
    with open(LBfilename, 'rb') as f:
        resultLB = pickle.load(f)

    for i in resultLB:
        if i[1] > LBcutoff:
            qualifiedParamLB.append(tuple(i[0]))
            LBDict[tuple(i[0])] = i[1]

    with open(roa_rovFilename, 'rb') as f:
        resultRR = pickle.load(f)


    for i in resultRR:
        if i[1] > RRcutoff:
            qualifiedParamRR.append(tuple(i[0]))
            RRDict[tuple(i[0])] = i[1]
        
    with open(ProaFilename, 'rb') as f:
        resultProa = pickle.load(f)
    
    for i in resultProa:
        if i[1] > pROAcutoff:
            qualifiedProa.append(tuple(i[0]))
            ProaDict[tuple(i[0])] = i[1]
    
    #get a list of param where it passes threshold for all 3 performance 
    RRLB_intersect = intersection(qualifiedParamRR, qualifiedParamLB)
    all_intersect = intersection(RRLB_intersect, qualifiedProa)

    #store the value for the param with highest combined value 
    maxval = 0
    maxParam = None

    tablels = []#list in list with entry [param, roarov, LB, Percent ROA]
    overall_qualified_param = []#list of overall qualified param 
    for i in all_intersect:
        tablels.append([i,RRDict[i] ,LBDict[i], ProaDict[i]])
        overall_qualified_param.append(i)
        #if the current param's performance > max, assign it as max 
        if RRDict[i] + LBDict[i] + ProaDict[i] > maxval:
            maxval  = RRDict[i] + LBDict[i] + ProaDict[i]
            maxParam = i
    #dump the overall qualified param into pickle 
    with open('overall_qualified_param.pickle', 'wb') as f:
        pickle.dump(overall_qualified_param, f)

    #output the table 
    print('max:', maxParam ,maxval)

    head = ["rov, roa, neither","ROA ROV Matching", 'Load Balance', 'Percent ROA Coverage']
    print(tabulate(tablels, headers=head, tablefmt="grid"))

#open pickle file and get all param with neitherDiscount = 1
def get_fair_param(file):
    """
    To avoid putting clients without ROA or ROV coverage in a worse position than in vanilla, we 
    want the neitherDiscount to be 1, so that clients with no coverage has the same chance of selecting 
    a ROA guard comparing to vanilla TOR. We want to achieve this because ROA guards could still provide 
    added security to the client even if the client has no ROA or ROV coverage in itself. 
    
    :param file: (string) file name of pickled parameters

    :return: (list) filter out all parameter with neitherDiscount != 1, return a list of 
    parameter with neitherDiscount == 1. 

    """
    with open(file, 'rb') as f:
        params = pickle.load(f)
    fairParam = []
    for p in params:
        if p[0][2] == 1:
            fairParam.append(p)
    return fairParam

#get max value in a list of param 
def get_max_param(file):
    """
    find the parameter with the largest combined value in all 3 area of performance 

    :param file: (string) filename of the pickled file with parameter and performance specs 

    :return: prints out the max param with the performance value and parameter 
    """
    with open(file, 'rb') as f:
        params = pickle.load(f)
        print(params)
    max_param_val = 0
    max_param = None
    max_param_spec = []
    for p in params:
        if p[1] + p[2] + p[3] > max_param_val:
            max_param_val = p[1] + p[2] + p[3]
            max_param = p[0]
            max_param_spec = [p[1], p[2], p[3]]
    print('-----------------------------------------------------')
    print('Optimal Params:')
    print('rov  roa  neither')
    print(max_param)
    print('roa_rov', '     LB', '               percent roa')
    print(max_param_spec)

# get_max_param('fairParam.pickle')
# analyzeParam('/home/siyang/research/tor-rpki/sim_roa_rov_L2/PermLBResult.pickle', '/home/siyang/research/tor-rpki/sim_roa_rov_L2/PermROA_ROVResult.pickle', '/home/siyang/research/tor-rpki/sim_roa_rov_L2/Perm_pROA_Result.pickle')
# get_max_param('/home/siyang/research/tor-rpki/sim_roa_rov_L2/qualifiedParam10runs.pickle')

