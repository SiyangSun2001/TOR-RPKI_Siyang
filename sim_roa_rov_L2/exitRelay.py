from util import *
import sys
import argparse
import statistics


def get_exit_distribution(start_date, end_date):
    """
    analyze the exit relay distribution in a duration of time using the processed pickles 
    each consensus file is processed using the analyze_consensus function, then the arithmetic mean is taken 
    of the exit&guard, just exit and nonExit percentage. 

    :param start_date: (datetime object) start of the period to be analyzed 
    :param end_date: (datetime object) end of the period to be analyzed 

    :return: prints out the averaged stats for each type of exit relay 
    """
    print("running")
    p = os.getcwd()
    path = os.path.split(p)[0]
    path = path + '/rpkicoverage/processed/'

    resultls = []
    for t in datespan(start_date, end_date, delta=timedelta(hours=1)):

        resultls.append(analyze_consensus(path, t.strftime('%Y'), t.strftime('%m'), t.strftime('%d'), t.strftime('%H')))
    exit_guardls = []
    exitls = []
    nonExitGuardls = []
    for consensus in resultls:
        exit_guardls.append(consensus[0])
        exitls.append(consensus[1])
        nonExitGuardls.append(consensus[2])
    print('exit and guard', '   just exit',  '  neither')
    print(statistics.mean(exit_guardls), statistics.mean(exitls),  statistics.mean(nonExitGuardls))

def analyze_consensus(p, year, month, date, hour):
    """
    tally up the number of relay tagged with exit, exit&guard, non-exit in processed consensus file 

    :param p: (string) path to the processed consensus directory 
    :param year: (string) year of consensus file 
    :param month: (string) month of consensus file 
    :param date: (string) date of consensus file 
    :param hour: (string) hour of consensus file

    :return: (list) return a list containing percent of exit&guard, percent of just exit and percent of nonExit.
    """
    filename = p + year + '-' + month + '-' + date + '-' + hour + '-processed.pickle'
    try:
        file = open(filename, 'rb')
    except FileNotFoundError:
        print('Consensus for ' + year + '-' + month + '-' + date + '-' + hour + ' doesn\'t exist.')
        return
    rs = pickle.load(file)
    exit_guard = 0
    exit = 0
    
    nonExit= 0
    for relay in rs:
        if relay.is_exit and relay.is_guard:
            exit_guard += 1
        elif relay.is_exit:
            exit += 1
        else:
            nonExit += 1
    return [exit_guard/len(rs), exit/len(rs),nonExit/len(rs)]

def main(args):
    """
    main function that drives the exit relay analyze, so user could provide command line arguments for the duration of the analyze
    """
    startdate = '2020-09-01-00'
    enddate = '2020-09-01-02'
    sd = startdate.split('-')
    ed = enddate.split('-')
    start_date = datetime(int(sd[0]), int(sd[1]), int(sd[2]), int(sd[3]))
    end_date = datetime(int(ed[0]), int(ed[1]), int(ed[2]), int(ed[3]))
    print('running')
    get_exit_distribution(start_date, end_date)



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
