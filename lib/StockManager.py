import base
##
## StockManager.py: Interface to use the web scraper
## Author: Aditya Patange
##

import scraper
import sqlite3

STOCKDB = 'stocks.db'


class StockManager:
    ## Initializes catalog
    def __init__(self, conf):
        self.driver = scraper.init_webdriver('normal')
    
    ## Returns stock data 
    def getStockData(self, id):
        data = []
        conn = sqlite3.connect(STOCKDB)
        cur = conn.cursor()
        cur.execute("SELECT * FROM catalog WHERE companyId='{0}'".format(str(id)))
        stockInfo =  cur.fetchall()
        for row in stockInfo:
            url = ""
            if(type(row) == dict): #only one item was returned
                url = row['url']
            else:
                url = row[3] ## TODO: What is this? 
            print("Pulling data for {0}...".format(url))
            ## PULLS ALL DATA FROM MONEYCONTROL
            scrapedData = scraper.fetchStockData(url)
            data.append(scrapedData)
        conn.close()
        return data
    
    ## Returns search results for a tag

    def search(self, query):
        tags = base.parseSearchQuery(query)
        if(len(tags) == 0):
            return results
        conn = sqlite3.connect(STOCKDB)
        cur = conn.cursor()        
        ## Fetch all results based on tags
        alias = 'table'
        sql = "SELECT * from %inner where companyName like '%{%c}%' or companyId like '%{%c}%'"
        res = []
        for i in range(len(tags)):
            if i <= 2: # take only the first 3 tags
                q = sql.replace('%inner', 'catalog').replace('{%c}', tags[i])
                cur.execute(q)
                curRes = cur.fetchall()
                res.append(curRes)
        #print(res)
        conn.close()
        return res
    
    ## Returns all results which match companyId
    def company(self, companyId="", companyKey = ""):
        results = []
        conn = sqlite3.connect(STOCKDB)
        cur = conn.cursor()
        sql = "SELECT * FROM catalog WHERE company{%s}='{0}'"
        if(companyKey):
            sql = sql.replace('{%s}', 'Key').format(companyKey)
        elif(companyId and not(companyKey)):
            sql = sql.replace('{%s}', 'Id').format(companyId)
        else:
            return None
        cur.execute(sql)
        results = cur.fetchall()
        conn.close()
        return results
    
    #
    ## Returns historic data for given duration
    # companyInfo must have companyName and companyKey
    # durationType = 'Daily' | 'Monthly | 'Yearly'
    # duration = [dd,mm,yy] | [mm, yy] | [yy]
    #
        
    def historic(self, companyName, companyKey, url, durationType, durationFrom, durationTo):
        results = scraper.getHistoricData(self.driver, {'companyName':companyName, 'companyKey':companyKey, 'url':url}, durationType, (durationFrom if durationType=="Yearly" else {'from':durationFrom, 'to':durationTo}))
        return results