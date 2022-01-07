from bs4 import BeautifulSoup
import requests
import pickle

def get_ROV_data(files):
    #copy tbody tag from https://rov.rpki.net/ into txt file 
    ROVList = []
    for f in files:
        file = open(f)
        soup = BeautifulSoup(file, 'html.parser')


        for i in soup.findAll('tr'):
            ROVList.append(str(i.findAll('td')[1])[4:-5])
    
    with open('ASNwROV.pickle', 'wb') as pf:
        pickle.dump(set(ROVList), pf)
    
# get_ROV_data(['page.txt', 'page2.txt', 'page3.txt'])

