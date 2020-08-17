# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 17:07:28 2020

@author: COM
"""
import pandas as pd
from surprise import SVD, accuracy #SVD model, 평가
from surprise import Reader, Dataset #SVD model의 dataset

# def make_model(df) :
#     global model



def do(user_i, df) :
    global item_base
    item_base = set(df["장소"])
    
    reader = Reader(rating_scale=(1,5))
    data = Dataset.load_from_df(df=df, reader=reader)
    train = data.build_full_trainset()
    test = train.build_testset()
    model = SVD(n_factors=100, n_epochs=20)
    model.fit(train)
    
    L=[]
    actual_rating=0
    for item_id in item_base:
        predictions = model.predict(user_i, item_id, actual_rating)
        if predictions[3] > 3 :
            L.append(predictions)

    result = pd.DataFrame(L)
    result.sort_values(["est"], ascending=False, inplace=True )
    result = result.loc[:,["uid", "iid", "est"]]
    result.columns=["이름", "장소", "p"]
    return result[:100]

# def do(user_i, df) :
#     global item_base
#     item_base = set(df["장소"])
#     return svd_recommend(user_i)