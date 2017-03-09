import requests
from bs4 import BeautifulSoup
import pickle
import sys
import re

BASE_URL = 'https://www.dotabuff.com/heroes'
WIN_RATE_URL = 'https://www.dotabuff.com/heroes/winning?date=patch_7.02'

#Dotabuff blocks the standard python/urllib user-agent
REQUEST_HEADER = {'user-agent': 'friendly stats robot'}

sys.setrecursionlimit(50000)


class StatTracker():
    def __init__(self):
        self.win_rate_soup = None
        self.win_rates = None


st = StatTracker()


def saveSoup():  
    with open('win_rate_soup.pickle', 'wb') as f:
        pickle.dump(st.win_rate_soup, f)

    
    
def loadSoup():
    try:
        f = open('win_rate_soup.pickle', 'rb')
        print('loading local')
        return pickle.load(f)
        
    except FileNotFoundError:
        print('loading from web')
        return requestWinRateSoup()
        

def requestWinRateSoup():
    r = requests.get(WIN_RATE_URL, headers = REQUEST_HEADER)
    status = r.status_code
    if status != requests.codes.ok:
        r.raise_for_status
       
    soup = BeautifulSoup(r.text, 'html.parser')
    
    return soup
    
def getWinRatePageStats(tr_block):
    #print(str(tr_block.prettify()))
    tr_str = str(tr_block)
    
    name = findName(tr_str)
    win_rate, pick_rate, kda = extractWinPageStats(tr_str)

    
    print(name)
    print('Win Rate: {}'.format(win_rate))
    print('Pick Rate: {}'.format(pick_rate))
    print('KDA: {}'.format(kda))
    print()
    
    
    
def findName(tr_str):

    name_start_idx = int( 
        re.search('"cell-icon" data-value="', tr_str).end()
    )
    
    name_length = int(
        re.search('"', tr_str[name_start_idx:]).start()
    )
    
    return tr_str[name_start_idx : name_start_idx + name_length]
    

def extractWinPageStats(tr_str):
    win_rate, tr_str = getNextTrData(tr_str)
    pick_rate, tr_str = getNextTrData(tr_str)
    kda = getNextTrData(tr_str)[0]

    return (win_rate, pick_rate, kda)
    
#returns a tuple (data_str, tr_str starting after data)
def getNextTrData(tr_str):
    start_idx = int(
        re.search('td data-value="', tr_str).end()
    )
        
    length = int(
        re.search('"', tr_str[start_idx:]).start()
    )
    
    data_str = tr_str[start_idx : start_idx + length]
    
    return (data_str, tr_str[start_idx+length :])


if __name__ == '__main__':
    st.win_rate_soup = loadSoup()
    
    print(st.win_rate_soup.tbody.contents[0])

    for i in range(len(st.win_rate_soup.tbody.contents)):
        getWinRatePageStats(st.win_rate_soup.tbody.contents[i])
    
    saveSoup()