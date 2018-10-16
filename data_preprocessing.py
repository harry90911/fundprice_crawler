
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
#from pymongo import MongoClient
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt


# # 從資料庫拉資料

# In[2]:


# client = MongoClient("mongodb://localhost:27017/")
# db = client.fund
# fundprice = db.fundprice

# cursor = fundprice.find()
# fundprice = pd.DataFrame([d for d in cursor])


# In[3]:


fundprice = pd.read_csv("/home/harry90911/fundprice.csv")


# In[6]:


for i in fundprice["FundId"].unique().tolist():
    print(i)
    fundprice.loc[fundprice["FundId"]==i,:].to_csv("/home/harry90911/fund_price_by_id/{}.csv".format(i))


# # 算滾動平均
# 
# 以 20181007 的 1M_Return 代表 20180907~20181007 的平均 Return  
# 其他以此類推

# In[4]:


#fundprice = fundprice.drop("_id",axis=1)
fundprice["Return"] = (fundprice["Price"]-fundprice["Price"].shift(1))/fundprice["Price"].shift(1)
fundprice["1M_Return"] = fundprice["Return"].rolling(30).mean()
fundprice["3M_Return"] = fundprice["Return"].rolling(90).mean()
fundprice["6M_Return"] = fundprice["Return"].rolling(180).mean()


# # 觀察滾動平均
# 
# 以 20171007 之後的資料為基準，如果該報酬率大於 75 百分位數，則記為 1 。

# In[5]:


# fundprice_check = fundprice.loc[fundprice["Date"].astype("int")>=20171007, ["FundId", "Name", "Return", "1M_Return", "3M_Return", "6M_Return"]].describe()
# 1 year 75百分位數
# Return    1M_Return  3M_Return  6M_Return
# 0.002825  0.000539   0.000472   0.000526

# fundprice_check = fundprice.loc[fundprice["Date"].astype("int")>=20180407, ["FundId", "Name", "Return", "1M_Return", "3M_Return", "6M_Return"]].describe()
# 0.5 year 75百分位數
# Return    1M_Return  3M_Return  6M_Return
# 0.002777  0.000358   0.000175   0.000279

fundprice_check = fundprice.loc[fundprice["Date"].astype("int")>=20171007, ["FundId", "Name", "Return", "1M_Return", "3M_Return", "6M_Return"]]
fundprice_check.loc[fundprice_check["Return"]>=0.002825,"Return_check"] = 1
fundprice_check.loc[fundprice_check["1M_Return"]>=0.000539,"1M_Return_check"] = 1
fundprice_check.loc[fundprice_check["3M_Return"]>=0.000472,"3M_Return_check"] = 1
fundprice_check.loc[fundprice_check["6M_Return"]>=0.000526,"6M_Return_check"] = 1
fundprice_check.fillna(0,inplace=True)


# # 觀察大於 75 百分位數的個數，取前十名

# In[6]:


count_check = fundprice_check.loc[:,["Name","1M_Return_check","3M_Return_check","6M_Return_check"]].groupby(["Name"],as_index=False).sum()

tmp1 = count_check.sort_values("1M_Return_check", ascending=False).loc[:,"Name"].reset_index(drop=True)
tmp2 = count_check.sort_values("3M_Return_check", ascending=False).loc[:,"Name"].reset_index(drop=True).rename(columns={"Name":"Rank_3M"})
tmp3 = count_check.sort_values("6M_Return_check", ascending=False).loc[:,"Name"].reset_index(drop=True).rename(columns={"Name":"Rank_6M"})
tmp1.name = "Rank_1M"
tmp2.name = "Rank_3M"
tmp3.name = "Rank_6M"

pd.DataFrame({"Rank_1M":tmp1,"Rank_3M":tmp2, "Rank_6M":tmp3})


# In[7]:


list(set(tmp1.tolist()[0:10]+tmp2.tolist()[0:10]+tmp3.tolist()[0:10]))

