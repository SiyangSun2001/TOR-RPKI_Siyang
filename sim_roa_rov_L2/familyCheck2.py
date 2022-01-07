from utilExit import *
import pickle
import json
import requests


def requestDescriptor():
    #request descriptor in json format from tor metricx and pickle the data
    url = 'https://onionoo.torproject.org/details'
    x = requests.get(url).json()

    with open("jsonRelay.pickle", "wb") as f:
        pickle.dump(list(x["relays"]),f)

def createDict():
    #create 2 dict to check for family given ip address 
    ipTOfp = dict() #maps ip with port -> fingerprint in descriptor file 
    fpTOserver = dict() #maps fingerprint to server object 
    with open("jsonRelay.pickle", "rb") as f:
        relayLS = pickle.load(f)
        
        for r in relayLS:
            ip = r["or_addresses"][0] #getting the ip address 
            nickname = r["nickname"] #getting nick name of relay
            curServer = Server(ip, nickname) #create server object that stores each relay within the descriptor file
            curServer.family = r["effective_family"] #assign family list to descriptor object 
            curServer.fp = r["fingerprint"] #assign fingerprint to relay 
            fpTOserver[r["fingerprint"]] = curServer #populate fingerprint -> server dictionary 
            if ip in ipTOfp.keys(): #check for repeat, same ip map to multiple server 
                print("repeat: ", ip)
            else:
                ipTOfp[ip] = r["fingerprint"]
        
    #pickle dump the 2 dictionary for future relay family relation check-up 
    with open("fpTOserver.pickle", "wb") as f:
        pickle.dump(fpTOserver,f)
    with open("ipTOfp.pickle", "wb") as f1:
        pickle.dump(ipTOfp, f1)

    


# createDict()
        

