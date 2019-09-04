import sqlite3;
import sys
import os
## Otherwise modules inside lib don't get detected
sys.path.append(os.getcwd() + '/lib')
from lib import scraper
def create_db(conn):
    query = """CREATE TABLE catalog (
        companyKey varchar(16), 
        companyId varchar(64), 
        companyName varchar(128), 
        url varchar(2048)
        )
        """
    c = conn.cursor()
    c.execute(query)
    conn.commit()

def setup_db(conn):
    catalog = scraper.fetchAll(scraper.getSearchResults(scraper.DEFAULT_CATALOG_INDEX))
    # Initialize cursor
    cur = conn.cursor()
    #print(catalog)
    sql = """INSERT INTO catalog (companyKey, companyId, companyName, url) VALUES ("{0}", "{1}", "{2}", "{3}")"""
    for item in catalog:
        q = sql.format(item['companyKey'], item['companyId'], item['name'], item['link']) ## Add sc_id later
        cur.execute(q)
        conn.commit()
    conn.commit()

# def check_items(conn):
#     sql = "SELECT * from catalog LIMIT 5"
#     cur = conn.cursor()
#     cur.execute(sql)
#     res = cur.fetchall()
#     print(res)

conn = sqlite3.connect("stocks.db")

create_db(conn)
setup_db(conn)
conn.close()