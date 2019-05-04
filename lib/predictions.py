#
# Author: Anezka Virani
#

import pandas as pd
import numpy as np
from sklearn import model_selection, preprocessing
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from matplotlib import style
import requests 
import json 
from pandas.io.json import json_normalize

#prediction for next 30 days 
def get_daily_data(key,fromdate,todate):
	api_url = "api url"
	response = requests.get(api_url)
	json_data = json.loads(response.text)
	df=json_normalize(json_data['historicData'])
	return df 

def clean_daily_data(df):
	df['close']=df['close'].astype(float)
	df['open']=df['open'].astype(float)
	df['high']=df['high'].astype(float)
	df['low']=df['low'].astype(float)
	df['volume']=df['volume'].astype(float)
	return df 

#returns 30 values 
def prepare_model_30days(df):
	#Make two new columns which will be used for making predictions.
	df["HL_Perc"] = (df["high"]-df["low"]) / df["low"] * 100
	df["CO_Perc"] = (df["close"] - df["open"]) / df["open"] * 100
	#Make array of dates
	#Last 30 dates will be used for forecasting.
	dates = np.array(df["date"])
	dates_check = dates[-30:]
	dates = dates[:-30]
	df = df[["HL_Perc", "CO_Perc", "close", "volume"]]
	#Define the label column
	df["PriceNextMonth"] = df["close"].shift(-30)
	#Make fetaure and label arrays
	X = np.array(df.drop(["PriceNextMonth"], axis=1))
	X = preprocessing.scale(X)
	X_Check = X[-30:]
	X = X[:-30]
	df.dropna(inplace = True)
	y = np.array(df["PriceNextMonth"])
	#Divide the data set into training data and testing data
	X_train, X_test, y_train, y_test = model_selection.train_test_split(X,y,test_size = 0.2)
	#Define the prediction model
	model = RandomForestRegressor()
	#Fit the model using training data
	model.fit(X_train, y_train)
	#Fit the model again using the whole data set
	model.fit(X,y)
	#Make predictions
	predictions = model.predict(X_Check)
	return predictions

#prediction for next 6 months 
def get_monthly_data(key,frommonth,tomonth):
	api_url = ("http://adamantium.pagekite.me/profithook/api/historic/key="+key+"&type=monthly&from="+frommonth+"&to="+tomonth) 
	response = requests.get(api_url)
	json_data = json.loads(response.text)
	df=json_normalize(json_data['historicData'])
	return df 

def clean_monthly_data(df):
	df['close']=df['close'].astype(float)
	df['open']=df['open'].astype(float)
	df['high']=df['high'].astype(float)
	df['low']=df['low'].astype(float)
	return df 

#returns 6 values
def prepare_model_6months(df):
	df["HL_Perc"] = (df["high"]-df["low"]) / df["low"] * 100
	df["CO_Perc"] = (df["close"] - df["open"]) / df["open"] * 100
	#Make array of dates
	#Last 6 months will be used for forecasting.
	dates = np.array(df["date"])
	dates_check = dates[-6:]
	dates = dates[:-6]
	df = df[["HL_Perc", "CO_Perc", "close"]]
	#Define the label column
	df["PriceNext6Months"] = df["close"].shift(-6)
	#Make fetaure and label arrays
	X = np.array(df.drop(["PriceNext6Months"], axis=1))
	X = preprocessing.scale(X)
	X_Check = X[-6:]
	X = X[:-6]
	df.dropna(inplace = True)
	y = np.array(df["PriceNext6Months"])
	#Divide the data set into training data and testing data
	X_train, X_test, y_train, y_test = model_selection.train_test_split(X,y,test_size = 0.2)
	#Define the prediction model
	model = RandomForestRegressor()
	#Fit the model using training data
	model.fit(X_train, y_train)
	#Fit the model again using the whole data set
	model.fit(X,y)
	#Make predictions
	predictions = model.predict(X_Check)
	return predictions 

#prediction for next 2 years 
def get_yearly_data(key,fromyear):
	api_url = ("http://adamantium.pagekite.me/profithook/api/historic/key="+key+"&type=yearly&from="+fromyear) 
	response = requests.get(api_url)
	json_data = json.loads(response.text)
	df=json_normalize(json_data['historicData'])
	return df

def clean_yearly_data(df):
	df['close']=df['close'].astype(float)
	df['open']=df['open'].astype(float)
	df['high']=df['high'].astype(float)
	df['low']=df['low'].astype(float)
	return df 

#returns 2 values 
def prepare_yearly_model(df):
	df["HL_Perc"] = (df["high"]-df["low"]) / df["low"] * 100
	df["CO_Perc"] = (df["close"] - df["open"]) / df["open"] * 100
	#Make array of dates
	#Last 2 years will be used for forecasting.
	dates = np.array(df["date"])
	dates_check = dates[-2:]
	dates = dates[:-2]
	df = df[["HL_Perc", "CO_Perc", "close"]]
	#Define the label column
	df["PriceNext2Years"] = df["close"].shift(-2)
	#Make fetaure and label arrays
	X = np.array(df.drop(["PriceNext2Years"], axis=1))
	X = preprocessing.scale(X)
	X_Check = X[-2:]
	X = X[:-2]
	df.dropna(inplace = True)
	y = np.array(df["PriceNext2Years"])
	#Divide the data set into training data and testing data
	X_train, X_test, y_train, y_test = model_selection.train_test_split(X,y,test_size = 0.2)
	#Define the prediction model
	model = RandomForestRegressor()
	#Fit the model using training data
	model.fit(X_train, y_train)
	#Fit the model again using the whole data set
	model.fit(X,y)
	#Make predictions
	predictions = model.predict(X_Check)

def predict(data):
    df = pd.DataFrame.from_dict(data)
    df = clean_daily_data(df)
    res = prepare_model_30days(df)
    return list(res)

#df=get_daily_data("TCS","2017-08-12","2018-9-23")
#print(df)
#df=clean_daily_data(df)
#predictions=prepare_daily_model(df)
#print(predictions)