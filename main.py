

import requests, json, time
from random import randint
from fake_useragent import UserAgent
from pymongo import MongoClient

# 拿到基金 ID 
def get_fund_index(page):
	url = "https://www.fundrich.com.tw/default/v1/funds"
	payload = {"PageSize":"99","PageIndex":page,"Sort":"UpDown","OrderDesc":"true","TwStock":"false","Retire":"false","Keyword":""}
	headers = {"Accept": "application/json, text/plain, */*",
			  "Accept-Encoding": "gzip, deflate, br",
			  "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,ja;q=0.5",
			  "Connection": "keep-alive",
			  "Content-Length": "106",
			  #"Content-Type": "application/json;charset=UTF-8",
			  #"Host": "www.fundrich.com.tw",
			  #"Origin": "https://www.fundrich.com.tw",
			  #"Referer": "https://www.fundrich.com.tw/fundOverview.html",
			  "User-Agent": "{}".format(UserAgent().random)}
	res = requests.post(url, data=payload, headers=headers)
	item_list = []
	items = json.loads(res.text)["Items"]
	for item in items:
		item_dict = {"Name":item["Name"], "FundId":item["FundId"]}
		
		# 將基金 ID 匯入至 mongodb
		client = MongoClient("mongodb://localhost:27017/")
		db = client.fund
		fundid = db.fundid
		fundid.update(item_dict, item_dict, upsert=True)
		
		item_list.append(item_dict)

	return item_list

# 拿到價格
def get_price(item):
	url = "https://apis.fundrich.com.tw/default/v1/funds/navPrices/{}?duration=est".format(item["FundId"])
	headers = {"User-Agent": "{}".format(UserAgent().random)}
	res = requests.get(url, headers=headers)
	prices = json.loads(res.text)

	client = MongoClient("mongodb://localhost:27017/")
	db = client.fund
	fundprice = db.fundprice

	price_list = []
	for price in prices:
		price_dict = {"Date": price["TransDate"], "Price": price["Price"], "Name":item["Name"], "FundId":item["FundId"]}
		price_list.append(price_dict)
	
	# 將基金價格資料匯入至 mongo db
	fundprice.insert_many(price_list)

	time.sleep(randint(2,3))

if __name__ == "__main__":
	for page in range(1,33):
		item_list = get_fund_index(page)
		for item in item_list:
			print(item)
			
			try:
				get_price(item)
			except Exception as e:
				print(e)

