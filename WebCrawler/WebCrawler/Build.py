import numpy as np
import pandas as pd


def Pretreatment():

    url = "C:/creditcard.csv"
    titanic_train = pd.read_csv(url)

    #label_encoder = preprocessing.LabelEncoder()
    #encoded_Transaction = titanic_train["Class"]

    titanic_X = pd.DataFrame([
                            titanic_train["V1"],
                            titanic_train["V2"],
                            titanic_train["V3"],
                            titanic_train["V4"],
                            titanic_train["V5"],
                            titanic_train["V6"],
                            titanic_train["V7"],
                            titanic_train["V8"],
                            titanic_train["V9"],
                            titanic_train["V10"],
                            titanic_train["V11"],
                            titanic_train["V12"],
                            titanic_train["V13"],
                            titanic_train["V14"],
                            titanic_train["V15"],
                            titanic_train["V16"],
                            titanic_train["V17"],
                            titanic_train["V18"],
                            titanic_train["V19"],
                            titanic_train["V20"],
                            titanic_train["V21"],
                            titanic_train["V22"],
                            titanic_train["V23"],
                            titanic_train["V24"],
                            titanic_train["V25"],
                            titanic_train["V26"],
                            titanic_train["V27"],
                            titanic_train["V28"]
                          
    ]).T

    titanic_y = pd.DataFrame([
                                titanic_train["Class"]                  
    ]).T

    return titanic_X,titanic_y