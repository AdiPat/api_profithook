import base
##
## StockManager.py: Interface to use the web scraper
## Author: Aditya Patange
##

import scraper
import pymysql
#import sqlite3


class StockManager:
    ## Initializes catalog
    def __init__(self, conf):
        #print(conf)
        self.conn = pymysql.connect(host='localhost', user=conf['user'], password=conf['password'], db=conf['db'], charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        #self.updateCatalog(self, index="Z");        
                
    ## Updates the catalog db with latest data
    ## catalog(id,name,url)
    ##
    @staticmethod
    def updateCatalog(self, index=scraper.DEFAULT_CATALOG_INDEX):
        # Pull data using scraper
        catalog = scraper.fetchAll(scraper.getSearchResults(index))
        # Initialize cursor
        cur = self.conn.cursor()
        # fill db
        #cur.execute('ALTER TABLE catalog ADD sc_id varchar(10)')
        cur.conn.commit()
        sql = "INSERT INTO catalog (companyKey, companyId, companyName, url, sc_id) VALUES (%s, %s, %s, %s, %s)"
        for item in catalog:
            #print("\nINSERTING ({0}, {1}, {2}, {3})".format(item['companyKey'], item['companyId'], item['name'], item['link']))
            
            ## Check if old data is present
            cur.execute("SELECT * FROM catalog WHERE companyKey='{0}'".format(item['companyKey']))
            oldData = cur.fetchone()
            if(oldData):
            #if(False):
                ## Exists
                print("{0} data exists. Checking if data is up to date.".format(item['companyKey']))
                ## Check if up to date
                if(not (oldData['companyId'] == item['companyId'] and oldData['companyName'] == item['name'] and oldData['url'] == item['link']) and oldData['sc_id'] == item['sc_id']):
                    # UPDATE
                    print("{0} data is outdated. Updating. ".format(item['companyKey']))
                    cur.execute("UPDATE catalog SET companyId='{0}' , companyName='{1}' , url='{2}' WHERE companyKey = '{3}'".format(item['companyId'], item['name'], item['link'], item['companyKey'],item['sc_id']))
                    self.conn.commit()
            else:
                ## INSERT 
                cur.execute(sql, (item['companyKey'], item['companyId'], item['name'], item['link']), item['sc_id'])
                self.conn.commit()
        cur.close()

    def getCatalog(self):
        return ['hullo']
    
    
    ## Returns stock data 
    def getStockData(self, id):
        data = []
        cur = self.conn.cursor()
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
        cur.close()
        return data
    
    ## Returns search results for a tag
    def search(self, query):
        results = scraper.parseSearchPage(query)
        ### If moneycontrol doesn't yield results, query db
        tags = base.parseSearchQuery(query)
        if(len(tags) == 0):
            return results

        cur = self.conn.cursor()        
        ## Fetch all results based on tags
        i = 0
        alias = 'table'
        ## If there are more than 4 tags , fetch for first two and last
        ## Fetch only for 3 tags , greater than that is not practical
        sql = "SELECT * from %inner where companyName like '%{%c}%' or companyId like '%{%c}%'"
        final = ""
        if(len(tags) >= 3):
            last = sql.replace('%inner', 'catalog').replace('{%c}', tags[len(tags)-1]) # table0
            middle = sql.replace('{%c}', tags[1])
            first = sql.replace('{%c}', tags[0])
            final = base.nestSelectQuery(first,base.nestSelectQuery(middle, last, 'table0'), 'table1')
        if(len(tags) == 2):
            last = sql.replace('%inner', 'catalog').replace('{%c}', tags[1])
            first = sql.replace('{%c}', tags[0])
            final = base.nestSelectQuery(first,last,'table0')
        if(len(tags) == 1):
            final = sql.replace('%inner', 'catalog').replace('{%c}', tags[0])
        
        print("FINAL QUERY: search() | " + final)
        cur.execute(final)
        results = cur.fetchall()
        cur.close()
        return results
    
    ## Returns all results which match companyId
    def company(self, companyId="", companyKey = ""):
        results = []
        cur = self.conn.cursor()
        sql = "SELECT * FROM catalog WHERE company{%s}='{0}'"
        if(companyKey):
            sql = sql.replace('{%s}', 'Key').format(companyKey)
        elif(companyId and not(companyKey)):
            sql = sql.replace('{%s}', 'Id').format(companyId)
        else:
            return None
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        return results
    
    #
    ## Returns historic data for given duration
    # companyInfo must have companyName and companyKey
    # durationType = 'Daily' | 'Monthly | 'Yearly'
    # duration = [dd,mm,yy] | [mm, yy] | [yy]
    #
        
    def historic(self, companyName, companyKey, url, durationType, durationFrom, durationTo):
        results = scraper.getHistoricData({'companyName':companyName, 'companyKey':companyKey, 'url':url}, durationType, (durationFrom if durationType=="Yearly" else {'from':durationFrom, 'to':durationTo}))
        return results