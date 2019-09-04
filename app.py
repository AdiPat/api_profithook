##
## app.py: Backend flask server
## Author: Aditya Patange
##

from flask import Flask,request,jsonify
from config import DB_CREDENTIALS
import sys
import os
import test.test__osx_support
sys.path.append(os.getcwd() + '/lib')
from lib import StockManager
from lib import base
from datetime import datetime


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False ## DONT SORT JSON
stockManager = StockManager.StockManager(DB_CREDENTIALS)

#
# Introduction 
#

@app.route("/profithook/api")
def api_hello():
    introData = [
        {
            'project-name':'ProfitHook API', 
            'apiVersion':'1.0', 
            'developer':'Aditya Patange', 
            'description':'REST API for real-time stock data',
            'howTo': [
                {
                    'name': 'Gets live stock Data from Id',
                    'request': 'GET',
                    'data': 'companyKey, companyName, companyId, companyId, url',
                    'format': '/profithook/api/stockId',
                    'description': 'Use companyId and not companyKey',
                    'example': '/profithook/api/TCS'
                },
                {
                    'name': 'Get results for a search Query',
                    'request': 'GET',
                    'data': 'List with search results',
                    'format': '/profithook/api/search/query',
                    'description': 'For whitespace, use + so Tata Power becomes Tata+Power',
                    'example': '/profithook/api/Tata+Power'
                },
                {
                    'name': 'Gets historic data for stock in specified time span',
                    'request': 'GET',
                    'format': '/profithook/api/historic/key=XXX&type=[daily,monthly,yearly]&from=[mm-dd-yy,mm-yy,yy]&to=[mm-dd-yy,mm-yy,yy]',
                    'description': 'Use companyKey for historic data and not companyId. Yearly data requires only a from date because it fetches historic data from the given year to current year.',
                    'example': [
                        '/profithook/api/historic/key=TCS&type=daily&from=01-02-2017&to=02-03-2018',
                        '/profithook/api/historic/key=TCS&type=monthly&from=02-2017&to=03-2018',
                        '/profithook/api/historic/key=TCS&type=yearly&from=2012'
                    ]
                }       
            ]
        }
    ]
    return jsonify(introData)


#
# Get stock data with stockId 
#

@app.route("/profithook/api/<stockId>")
def api_getStock(stockId):
    data = stockManager.getStockData(stockId)
    return jsonify(data)

#
# Route is of the form: /profithook/api/historic/key=TCS&type=daily&from=01-02-2017&to=02-03-2018
#

@app.route("/profithook/api/historic/<historicQuery>")
def api_historic(historicQuery):
    start = datetime.now() # performance testing
    ## Standardise parameters for scraper
    parameters = base.parseHistoricQuery(historicQuery)
    parameters = base.standardiseHistoricParameters(parameters)
    ## Get company information
    cInfo = stockManager.company(companyKey=parameters['key'])[0]
    print('api_historic()', cInfo, parameters)
    ## Pad company information into results
    result = dict([(key, cInfo[key]) for key in cInfo.keys()])
    ## Scrape historic data
    result['historicData'] = stockManager.historic(cInfo['companyName'], cInfo['companyKey'], cInfo['url'],parameters['type'], parameters['from'], parameters['to'])
    diff = datetime.now() - start
    print("TIME: ", diff.total_seconds())
    return jsonify(result)

#
# Search Query
#

@app.route("/profithook/api/search/<searchQuery>")
def api_search(searchQuery):
    tags = base.parseSearchQuery(searchQuery)
    results = stockManager.search(searchQuery)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)