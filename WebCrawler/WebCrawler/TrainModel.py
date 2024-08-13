import numpy as np
import pandas as pd
from sklearn import ensemble, preprocessing, metrics
import joblib #jbolib模块
from sklearn.model_selection  import train_test_split
import os
import requests
import Build as Build
np.set_printoptions(threshold=np.inf)
# 載入資料




def TrainModel():


    titanic_X,titanic_y=Build.Pretreatment()

    train_X, test_X, train_y, test_y = train_test_split(titanic_X, titanic_y, test_size = 0)




    print("train start")
    forest = ensemble.RandomForestClassifier(n_estimators = 100) #n_estimators 決策樹
    #forest_fit = forest.fit(train_X, train_y.values.ravel())
    forest_fit = forest.fit(titanic_X, titanic_y.values.ravel())
     

    #保存Model(注:save文件夹要预先建立，否则会报错)
    joblib.dump(forest, os.getcwd()+'/forest.pkl')
 

    response = requests.get("http://127.0.0.1:800/UpdateModel")

    print(response)
    print("train end")



if __name__ == '__main__':
    TrainModel()