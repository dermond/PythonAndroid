
import numpy as np
import pandas as pd
from sklearn import ensemble, preprocessing, metrics
import joblib #jbolib模块
from sklearn.model_selection  import train_test_split
import os
import Build as Build

np.set_printoptions(threshold=np.inf)
# 載入資料


def Predicted(forest):


    titanic_X,titanic_y=Build.Pretreatment()

  
    t1=0
    t2=0
    t3=0
    t4=0
    t5=0
    t6=0
    t7=0


    # 績效
    test_y_predicted = forest.predict(titanic_X)

    fpr, tpr, thresholds = metrics.roc_curve(titanic_y, test_y_predicted)
    r2 = metrics.r2_score(titanic_y,test_y_predicted)
    auc = metrics.auc(fpr, tpr)

    result = "";
    result += "AUC:"+str(auc)+"<br>";
    print("AUC:"+str(auc))
    result += "R2:"+str(r2)+"<br>";
    print("R2:"+str(r2))



    #for index, row in titanic_X.iterrows():
 
    #    #print(titanic_y["Class"][t1])
    
    #    if (str(test_y_predicted[t1]) == "0"):
    #        t2+=1
         
    #    if (str(test_y_predicted[t1]) == "1"):
    #        t3+=1
 
    #    if (str(test_y_predicted[t1]) == "1" and str(titanic_train["Class"][t1]) == "0"):
    #        t4+=1
        
    #    if (str(test_y_predicted[t1]) == "1" and str(titanic_train["Class"][t1]) == "1"):
    #        t7+=1
         
    #    if (str(test_y_predicted[t1]) == "0" and str(titanic_train["Class"][t1]) == "0"):
    #        t6+=1
    
    #    if (str(test_y_predicted[t1]) == "0" and str(titanic_train["Class"][t1]) == "1"):
    #        t5+=1
     
    #    t1=t1+1

    #t8=0
    #t9=0
    #for index, row in titanic_train.iterrows():
    #    if (str(titanic_train["Class"][t8]) == "1"):
    #        t9+=1
         
    #    t8+=1
     
    #result = "";

    #result += "共"+str(t2)+"預測會不成交" +"<br>";
    #print("共"+str(t2)+"預測會不成交")
    #result += "共"+str(t3)+"預測會成交" +"<br>";
    #print("共"+str(t3)+"預測會成交")
 
    #result += "預測成交率:"+str(t3*100/t1)+"%" +"<br>";
    #print ("預測成交率:"+str(t3*100/t1)+"%")
 
    #result += "本來成交 預測為成交數量:"+str(t7) +"<br>";
    #print ("本來成交 預測為成交數量:"+str(t7))
    #result += "本來成交 預測為不成交數量:"+str(t5) +"<br>";
    #print ("本來成交 預測為不成交數量:"+str(t5))
    #result += "本來不成交 預測為成交數量:"+str(t4)+"<br>";
    #print ("本來不成交 預測為成交數量:"+str(t4))
    #result += "本來不成交 預測為不成交數量:"+str(t6) +"<br>";
    #print ("本來不成交 預測為不成交數量:"+str(t6))
 
    #result += "原本資料共"+str(t8)+"預測會不成交" +"<br>";
    #print("原本資料共"+str(t8)+"預測會不成交")
    #result += "原本資料共"+str(t9)+"預測會成交" +"<br>";
    #print("原本資料共"+str(t9)+"預測會成交")
    #result += "原本資料的成交率"+str(t9*100/t8)+"%" +"<br>";
    #print ("原本資料的成交率"+str(t9*100/t8)+"%")
    #result += "預測成交率和實際數值去比較:"+str(t7*100/t9)+"%準確率" +"<br>";
    #print ("預測成交率和實際數值去比較:"+str(t7*100/t9)+"%準確率")

    return result

#if __name__ == '__main__':

#    forest = joblib.load(os.getcwd()+'/forest.pkl')
#    Predicted();

