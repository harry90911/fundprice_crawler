
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score

from keras.layers import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from keras import optimizers
from keras.utils import to_categorical


# In[3]:


#dataset = pd.read_csv("/home/harry90911/fundprice.csv")
#data_dir = dataset.loc[dataset["FundId"]==5005,"Price"].to_frame().rename(columns={"Price":"close"}).to_csv()

input_seq_len = 10
classfication_len = 5

learning_rate = 0.001
epochs = 30
batch_size = 200


# In[23]:


def get_label(y_data):
	label_list = []
	for row in np.arange(y_data.shape[0]) :
		if y_data[row][-1] > y_data[row][0] :
			label_list.append(1)
		else :
			label_list.append(0)
	return label_list

#normalized in window
def normalize_data(x_data):
	normalized_x_data = []
	for row in np.arange(x_data.shape[0]):
		window_data = x_data[row]
		normalized_windows = []
		scale = np.max(window_data)
		for data in window_data:
			normalized_windows.append(data/scale)
		normalized_x_data.append(normalized_windows)
	normalized_x_data = np.array(normalized_x_data)
	return normalized_x_data

def data_preprocessing(data_dir):
    data = pd.read_csv(data_dir)
    data = np.array(data["close"])

    slice_data = []
    for index in range(len(data)-input_seq_len-classfication_len):
        slice_data.append(data[index:index+input_seq_len+classfication_len])
    slice_data = np.array(slice_data)
    row = int(0.9*slice_data.shape[0])
    train_data = slice_data[:row,:]
    np.random.shuffle(train_data)
    test_data = slice_data[row:,:]
    #x_data
    x_train = train_data[:,:-classfication_len]
    x_train = normalize_data(x_train)
    x_test = test_data[:,:-classfication_len]
    x_test = normalize_data(x_test)
    #y_data
    y_train = train_data[:,input_seq_len:]
    y_train = get_label(y_train)
    y_test = test_data[:,input_seq_len:]
    y_test = get_label(y_test)
    #reshape
    x_train = np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))
    x_test = np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))
    #one_hot
    y_train_one = to_categorical(y_train)

    return x_train , x_test , y_train ,y_train_one, y_test

def build_model():
	model = Sequential()
	model.add(LSTM(64,input_shape=(input_seq_len,1),return_sequences=True))
	model.add(Dropout(0.3))
	model.add(LSTM(128, return_sequences=False))
	model.add(Dropout(0.3))
	model.add(Dense(2,activation="softmax"))
	model.compile(loss="binary_crossentropy", optimizer=optimizers.Adam(lr=learning_rate,epsilon=1e-08), metrics=["accuracy"])
	print(model.summary())
	return model


# In[26]:


x_train,x_test,y_train,y_train_one,y_test = data_preprocessing(data_dir)
model = build_model()
model.fit(x_train,y_train_one,epochs=epochs,batch_size=batch_size,verbose=1)
model.save('classfication.h5')
print("training_accuracy : " , accuracy_score(y_true=y_train,y_pred=model.predict_classes(x_train)))

print("testing_accuracy : ",accuracy_score(y_true=y_test,y_pred=model.predict_classes(x_test)))

