from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re
import string
import json

tagNames = {
  ## BSE 
  'BseCurrent': 'Bse_Prc_tick',
  'BseUploadTime': 'bse_upd_time',
  'BseChangeText': 'b_changetext', # Get span and content
  'BseVolume': 'bse_volume',
  'BsePrevClose': 'b_prevclose',
  'BseOpen': 'b_open',
  'BseBidPrice': 'b_bidprice_qty',
  'BseOfferPrice': 'b_offerprice_qty',
  ## NSE
  'NseCurrent': 'Nse_Prc_tick',
  'NseUploadTime': 'nse_upd_time',
  'NseChangeText': 'n_changetext', # Get span and content
  'NseVolume': 'nse_volume',
  'NsePrevClose': 'n_prevclose',
  'NseOpen': 'n_open',
  'NseBidPrice': 'n_bidprice_qty',
  'NseOfferPrice': 'n_offerprice_qty',
  ## Historic Search tags
  ## Daily
  'HistoricSearchBox': 'mycomp',
  'DailyForm': 'frm_dly',
  'fromDay': 'frm_dy',
  'fromMonth': 'frm_mth',
  'fromYear': 'frm_yr',
  'toDay': 'to_dy',
  'toMonth': 'to_mth',
  'toYear': 'to_yr',
  ## Monthly
  'MonthlyForm': 'frm_mthly',
  'month': 'mth_',
  ## Yearly
  'YearlyForm': 'frm_yrly',
  'yearly': 'frm_yrly_yr'
};

 
def getURL(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if isResponseValid(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
    
def isResponseValid(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)
 
def getSoup(url):
    raw_html = getURL(url)
    soup = BeautifulSoup(raw_html, 'html.parser', from_encoding="iso-8859-1")
    return soup


def parseSearchQuery(query):
    # Split into words
    tags = query.split('+')
    # Remove special characters
    pattern = re.compile('[\W_]+')
    i = 0
    for w in tags:
        tags[i] = pattern.sub('',w)
        i += 1
    return tags

#
# Parse historic query
#
def parseHistoricQuery(query):
    fields = query.split('&')
    result = {}
    for field in fields:
        prop = field.split('=')[0]
        val = field.split('=')[1].replace('+', ' ')
        result[prop] = val
    return result

def dateToArr(dateStr):
    return [x for x in dateStr.split('-')]
#
# Writes data in json to file
# 
def writeToFile(data, filename):
    datafile = open(filename + '.json', 'w')
    jsonStr = json.dumps(data, indent=4)
    datafile.write(jsonStr)
    datafile.close()

#
# Nests two select queries 
#

def nestSelectQuery(outer, inner, aliasName):
    modInner = "(" + inner + ") as " + aliasName + " "
    modOuter = outer.replace('%inner', modInner)
    return modOuter