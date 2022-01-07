from util import *
import time
import ipaddress
import argparse
import sys
import pickle
# start_date = datetime(2020,9,1,00)
# end_date = datetime(2020,9,2,00)
# print(type(start_date))
# for t in datespan(start_date, end_date, delta=timedelta(hours=1)):
#     print(type(t))
with open('/home/siyang/research/tor-rpki/sim_roa_rov_L2/PermROA_ROVResult.pickle', 'rb')as f1:
    ls = pickle.load(f1)
    print(ls)