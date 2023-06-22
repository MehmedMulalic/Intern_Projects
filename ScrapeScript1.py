from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import pandas as pd

# There are 45 states of which 12 have no information
# (2 informationless states only have telephone numbers)
states = [
"alaska",
"connecticut",
"hawaii",
"louisiana",
"montana",
"utah"
]
states_with_maps = [
"alabama",
"arizona",
"california",
"colorado",
"florida",
"georgia",
"idaho",
"illinois",
"indiana",
"maryland",
"michigan",
"minnesota",
"missouri",
"north-carolina",
"new-mexico",
"nevada",
"new-york",
"ohio",
"oregon",
"pennsylvania",
"rhode-island",
"south-carolina",
"tennessee",
"texas",
"virginia",
"washington"
]
baseLink = 'https://www.storhouseselfstorage.com/storage-units/'

def getSoup(stateName):
    page = requests.get(urljoin(baseLink, stateName))
    return BeautifulSoup(page.text, 'html.parser')

def getInfo(findable):
    tempSeries = pd.Series(dtype='object')
    for a in findable:
        tempSeries = pd.concat([tempSeries, pd.Series(a.text.strip())])
    return tempSeries

for i in states:
    soup = getSoup(i)
    df = pd.DataFrame()

    #Unit Sizes
    findTag = soup.find_all('div', {"class": "unit-size"})
    df = pd.concat([df, getInfo(findTag)])
    
    #Information
    findTag = soup.find_all('div', {"class": "amenities"})
    df = pd.concat([df, getInfo(findTag)], axis=1)

    #Prices
    findTag = soup.find_all('span', {"class": "price bold"})
    df = pd.concat([df, getInfo(findTag)], axis=1)
    findTag = soup.find_all('span', {"class": "price price-strike"}) #dashed prices
    df = pd.concat([df, getInfo(findTag)], axis=1)
    
    df.to_csv(i+'.csv', index=False)

for i in states_with_maps:
    soup = getSoup(i)
    link_num = 1

    for link in soup.find_all('a'):
        df = pd.DataFrame()
        
        if i in link.get('href'):
            #skip if same urls
            if urljoin(baseLink, link.get('href')) == baseLink+i+'/': continue
            soup = getSoup(link.get('href'))

            #Unit Sizes
            findTag = soup.find_all('div', {"class": "unit-size"})
            df = pd.concat([df, getInfo(findTag)])
    
            #Information
            findTag = soup.find_all('div', {"class": "amenities"})
            df = pd.concat([df, getInfo(findTag)], axis=1)

            #Prices
            findTag = soup.find_all('span', {"class": "price bold"})
            df = pd.concat([df, getInfo(findTag)], axis=1)
            df = df.reset_index(drop=True)

            findTag = soup.find_all('span', {"class": "price price-strike"}) #dashed prices
            new_df = pd.DataFrame(getInfo(findTag)).reset_index(drop=True)
            df = pd.concat([df, new_df], axis=1)
    
            df.to_csv(i+str(link_num)+'.csv', index=False)
            link_num += 1