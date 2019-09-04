##
## scraper.py: Web Page parsing and scraping functionality
## Author: Aditya Patange
##

import os
import sys
import time
import base
from base import tagNames
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

DEFAULT_CATALOG_INDEX = "ABCDEFGHIJKLMNOPQRSTUVWXYZ9"

#
# Extracts the companyId from link
#

def stripLink(link):
    link = link.replace('https://www.moneycontrol.com/india/stockpricequote/', '')
    link = link.replace('http://www.moneycontrol.com/india/stockpricequote/', '')
    # FAILS FOR http://www.moneycontrol.com/india/stockpricequote/bsesensex/bsesensex/BSE03 because /bsesensex is deleted twice!
    # link = link.replace(link[0:link.find('/')+1],'')
    link = link[link.find('/')+1:len(link)]
    return link

def getCompanyKey(link):
    link = stripLink(link)
    key = link[link.find('/')+1:len(link)]
    return key

def getCompanyId(link):
    ## Strip off useless data
    link = stripLink(link)
    data = link[0: link.find('/')]
    return data


#
# Fetches {company Id, company Name, moneycontrol link} from a url
#

def get_sc_id(link):
    linkSrc = base.getSoup(link)
    #print(data['link'])
    #print(linkSrc.find('sc_id'))
    scTag = linkSrc.find(id="sc_id")
    if scTag:
        scTag = str(scTag)
        scTag = scTag[scTag.find('value')+7:scTag.find('/')-1]
        return scTag
    return 'NA'
    
    
def fetchCompanyInfo(link):
    html = base.getSoup(link)
    companyData = []
    data = {}
    for tr in html.find_all('tr'):
        for a in tr.find_all('a'):
            if(len(a.contents)):
                data = {
                    'name': a.contents[0],
                    'link': a.get('href')
                }
                data['companyId'] = getCompanyId(data['link'])
                data['companyKey'] = getCompanyKey(data['link'])
                companyData.append(data)
    return companyData

#
# fetches {company Id, company Name, moneycontrol link}
# from all links in the list.
#

def fetchAll(pages):
    result = []
    i = 1
    for link in pages:
        print(str(i) + " | FETCHING.. ", link)
        data = fetchCompanyInfo(link)
        #print(str(i) + " | EXTENDING..")
        result.extend(data)
        i += 1
    return result

#
# Generate search result links for all stocks starting with alphabets # # in index: (A-Z, others is represented by 9) 
# By default it fetches result links for all (A to Z and others)
# 

def getSearchResults(index=DEFAULT_CATALOG_INDEX):
    pages = []
    for c in index:
        baseURL = 'https://www.moneycontrol.com/india/stockpricequote/'
        if (c == '9'):
            baseURL += 'others'
        else:
            baseURL += c
        pages.append(baseURL)
    return pages


#
# Parses moneycontrol page and pulls out all required data
# TODO: Cleanup this method
# 

def convFloat(val):
    val = val.replace("(", "")
    val = val.replace(")", "")
    val = val.strip()
    ans = 0
    try:
        ans = float(val)
    except ValueError:
        ans = 420.69
    return ans

def parseMainPage(html, exchange):
    result = {}
    prefix = '';
    if(exchange == 'NSE'):
        prefix = "Nse"
    if(exchange == 'BSE'):
        prefix = 'Bse'
    ## Fetch current price
    currentElem = html.find(id=tagNames[prefix + 'Current'])
    if(currentElem):
        result['currentPrice'] = currentElem.find('strong').contents[0]
    ## Fetch upload time
    uploadElem = html.find(id=tagNames[prefix + 'UploadTime'])
    if(uploadElem):
        result['uploadTime'] = uploadElem.contents[0]
    ## Fetch change
    changeElem = html.find(id=tagNames[prefix+'ChangeText'])
    if(changeElem):
        ## Get percentage
        changeData = str(changeElem)
        start = changeData.find('(')
        end = changeData.find(')')
        changeData = changeData[start+1:end].replace('%', '')
        result['changePercentage'] = convFloat(changeData.strip())
        result['changePoints'] = convFloat(changeElem.find('span').find('strong').contents[0])
        #print(result['changePercentage'], result['changePoints'])
    ## Volume
    volumeElem = html.find(id=tagNames[prefix+'Volume'])
    if(volumeElem):
        result['volume'] = volumeElem.find('strong').contents[0].replace(',', '')
    ## Prev Close
    prevCloseElem = html.find(id = tagNames[prefix+'PrevClose'])
    if(prevCloseElem):
        result['prevClose'] = convFloat(prevCloseElem.find('strong').contents[0])
    ## Open
    openElem = html.find(id = tagNames[prefix+'Open'])
    if(openElem):
        result['openPrice'] = convFloat(openElem.find('strong').contents[0])
    ## Bid Price
    bidElem = html.find(id = tagNames[prefix+'BidPrice'])
    if(bidElem):
        bidData = bidElem.find('strong').contents[0]
        result['bidPrice'] = convFloat(bidData.strip()[0:bidData.find(' ')])
        result['bidQuantity'] = int(bidData[bidData.find('(')+1:bidData.find(')')].replace(',', ''))
    ## Offer Price
    offerElem = html.find(id = tagNames[prefix+'OfferPrice'])
    if(offerElem):
        offerData = offerElem.find('strong').contents[0]
        result['offerPrice'] = convFloat(offerData.strip()[0:offerData.find(' ')])
        result['offerQuantity'] = int(offerData[offerData.find('(')+1:offerData.find(')')].replace(',', ''))
    return result

# 
# Fetches stock data from the moneycontrol page
# Takes url as parameter
#

def fetchStockData(url):
    html = base.getSoup(url)
    result = {
        'companyKey': getCompanyKey(url),
        'companyId': getCompanyId(url),
        'link': url,
        'BSE': {},
        'NSE': {}
    }
    result['BSE'] = parseMainPage(html, 'BSE')
    result['NSE'] = parseMainPage(html, 'NSE')
    return result

##
## Parses search results
## We assume the search String is purely alphanumeric
## TODO: Add validation for this later
## 
def parseSearchPage(searchStr):
    results = []
    searchStr = searchStr.replace('+',' ').lower()
    print(searchStr)
    url = "http://www.moneycontrol.com/stocks/cptmarket/compsearchnew.php?search_data=&cid=&mbsearch_str=&topsearch_type=1&search_str={0}".format(searchStr)
    html = base.getSoup(url)
    print(type(html))
    for tr in html.findAll('table', {'class': 'srch_tbl'}):
        for a in tr.findAll('a'):
            templink = a.get('href')
            tempname = ''
            for c in a.contents:
                cstr = str(c)
                cstr = cstr.replace('</strong>', '').replace('<strong>', '').strip()
                tempname += ' ' + cstr
            item = {'name': tempname.strip(), 'companyId': getCompanyId(templink), 'companyKey': getCompanyKey(templink), 'link': a.get('href')}
            results.append(item)
    return results


#### Historic data
def init_webdriver(pageLoadStrategy):
    caps = DesiredCapabilities().FIREFOX
    #caps["pageLoadStrategy"] = "none"
    driverPath = os.getcwd()+'/bin/geckodriver'
    opts = Options()
    opts.set_headless()
    assert opts.headless
    driver = Firefox(desired_capabilities=caps, options=opts, executable_path=driverPath)
    return driver

#
# getHistoric() Returns page with historic data for the stock within # # provided time span
# daily, {from: [dd,mm,yy], to: [dd,mm,yy]} 
#
#
#


#
# Scrapes table from the result page after historic result search
#

def scrapeHistoricResultPage(page_source):
    results = []
    keys = {
        '0': 'date',
        '1': 'open',
        '2': 'high',
        '3': 'low',
        '4': 'close',
        '5': 'volume',
        '6': 'spread_high-low',
        '7': 'spread_open-close'
    }
    html = BeautifulSoup(page_source, 'html.parser')
    for table in html.findAll('table', {'class':'tblchart'}):
        for tr in table.findAll('tr'):
            item = {}
            i = 0
            for td in tr.findAll('td'):
                if(i > 7):
                    break
                if(len(td.contents)):
                    item[keys[str(i)]] = td.contents[0]
                    i += 1
            #print(item)
            results.append(item)    
    return list(filter(None,results))

#
# Scrapes all historic search results page wise
#
    
def scrapeHistoricResults(driver):
    results = scrapeHistoricResultPage(driver.page_source)
#    wait = WebDriverWait(driver, 20)
#    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'pgn')))
#    nextBtn = driver.find_element_by_class_name('pgn').find_element_by_class_name('nextprev')
    curPage = 1
    while(True):
        ## Click
        time.sleep(2)
        #nextBtn.click()
        #driver.execute_script("""document.querySelector("a[class='nextprev']").click();""")
        try:
            driver.find_element_by_link_text(str(curPage+1)).click()
        except NoSuchElementException:
            print("No next page!")
            break
            
        results.extend(scrapeHistoricResultPage(driver.page_source))
        curPage += 1
    return list(filter(None,results))    
    

def matchHistoricSearch(companyInfo, driver):
    ## Iterate through suglist links and look for matching key 
#    entry = companyInfo['companyName'].split(' ')[0]
#    searchBox = driver.find_element_by_id(tagNames['HistoricSearchBox'])
#    searchBox.send_keys(entry)
#    time.sleep(0.100) # Wait for all the characters to be sent to generate results
#    sugList = driver.find_element_by_id("suggest")
#    links = sugList.find_elements_by_tag_name("a")
#    for a in links:
#        ## check if company id matches id in the button
#        scriptText = a.get_attribute('onclick')
#        sugKey = scriptText[scriptText.find(',')+2: len(scriptText)-3]
#        sugName = scriptText[scriptText.find('(')+2: scriptText.find(',')-1]
#        if(sugKey == companyInfo['companyKey'] or sugName == companyInfo['companyName']):
#            time.sleep(0.500)
#            ## FOUND, click
#            a.click()
#            break 
    ## ALTERNATIVE. The page uses set_val(companyName, companyKey) for the form
    sc_id = get_sc_id(companyInfo['url'])
    if sc_id == "NA":
        return False
    driver.execute_script("set_val('{0}','{1}');".format(companyInfo['companyName'], sc_id))
    return True
            
def setHistoricFormInput(driver, name, value, formName):
    if(formName == tagNames['YearlyForm']):
        driver.execute_script("""document.getElementsByName('{0}')[0].querySelector("select[name='{1}']").value = '{2}';""".format(formName, name, value))
    else:
        driver.execute_script("""document.getElementsByName('{0}')[0].querySelector("div.PT4 select[name='{1}']").value = '{2}';""".format(formName, name, value))
    time.sleep(0.500)
                    
def _getHistoricData(driver, companyInfo, durationType, duration):
    url = 'https://www.moneycontrol.com/stocks/histstock.php'
    data = []
    status = True
    driver.get(url)
    time.sleep(5)
    inp_val = matchHistoricSearch(companyInfo, driver)
    if(durationType == 'Daily' and type(duration) == dict):
        ## Set input fields
       # driver.execute_script("var formElem = document.getElementsByName('{0}')[0];".format(tagNames['DailyForm']));
        ## Set from fields
        setHistoricFormInput(driver, tagNames['fromDay'], duration['from'][0], tagNames['DailyForm'])
        setHistoricFormInput(driver, tagNames['fromMonth'], duration['from'][1], tagNames['DailyForm'])
        setHistoricFormInput(driver, tagNames['fromYear'], duration['from'][2], tagNames['DailyForm'])
        ## Set to dates
        setHistoricFormInput(driver, tagNames['toDay'], duration['to'][0], tagNames['DailyForm'])
        setHistoricFormInput(driver, tagNames['toMonth'], duration['to'][1], tagNames['DailyForm'])
        setHistoricFormInput(driver, tagNames['toYear'], duration['to'][2], tagNames['DailyForm'])
        time.sleep(5)
    elif(durationType == 'Monthly' and type(duration) == dict):
        ## From
        setHistoricFormInput(driver, tagNames['month']+tagNames['fromMonth'], duration['from'][0], tagNames['MonthlyForm'])
        setHistoricFormInput(driver, tagNames['month']+tagNames['fromYear'], duration['from'][1], tagNames['MonthlyForm'])
        ## To 
        setHistoricFormInput(driver, tagNames['month']+tagNames['toMonth'], duration['to'][0], tagNames['MonthlyForm'])
        setHistoricFormInput(driver, tagNames['month']+tagNames['toYear'], duration['to'][1], tagNames['MonthlyForm'])
        time.sleep(5)
    elif(durationType == 'Yearly' and type(duration) == str):
        setHistoricFormInput(driver, tagNames['yearly'], duration, tagNames['YearlyForm'])
        time.sleep(5)
    else:
        print("getHistoric(): INVALID INPUT!")
        status = False
    ## Click submit button
    if(status and inp_val):
        imgBtn = driver.find_element_by_name(tagNames[durationType+'Form']).find_element_by_tag_name('input')
        imgBtn.click()
        time.sleep(5) ## Let page load properly
        data = scrapeHistoricResults(driver)
    return data


def getHistoricData(companyInfo, durationType, duration):
    driver = init_webdriver('normal')
    data = []
    print(companyInfo, durationType, duration)
    try:
        data = _getHistoricData(driver, companyInfo, durationType, duration)
    finally:
        driver.quit()
    return data
