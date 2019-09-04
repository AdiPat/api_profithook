# Profithook
## REST API for Stock Market Data

Profithook is a non for profit, fun project I built as part of my Web Development Course during Engineering.

It is a REST API that delivers stock market data in real-time. The API uses a web scraper that searches for your favorite stocks, scrapes stock prices and historic data from the web.


## Getting Started

To run the Flask Server on your local system, install Python 3 and the required dependencies. To ensure you're running the correct versions, use a virtual environment. Clone the project and run this command in the root directory.

**Install modules**
```
pip install -r requirements.txt
```

**Start the Flask server**
```
python3 app.py
```

## API Routes

Below are the API routes for using the service.

### 1. Instructions to use the API
```
/profithook/api/
```

### 2. Search a Stock
```
/profithook/api/search/<query>
```

### 3. Get Stock Information
Use the stockID provided in the search results to query the stock's information directly.
```
/profithook/api/<stockID>
```

### 4. Get Historic Data for a Stock

```
/profithook/api/historic/key=XXX&type=[daily,monthly,yearly]&from=[mm-dd-yy,mm-yy,yy]&to=[mm-dd-yy,mm-yy,yy]'
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.