# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:10:16 2020

@author: COM
"""

import pandas as pd
import cx_Oracle
import os

def get_data() :
    global review
    os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
    
    connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
    cur = connection.cursor()
    cur.execute('select name, place, category, star, address ,category1, address1, address2, count, latitude, longitude, year, month, season from recommend ')
    
    
    review = []
    for result in cur:
        # print(result)
        review.append(result)
    # print(len(review))
    # 커넥션 종료
    cur.close()
    connection.close()
    
    review = pd.DataFrame(review)
    review.columns = ['이름', '장소', '분류', '별점', '주소', '대분류', '주소1', '주소2', '방문횟수', '위도', '경도', '년도', '월', '계절']    


def get_df(add=None, ctg=5):
    if add == None :
        df = pd.DataFrame()
        df["이름"] = review["이름"]
        df["장소"] = review["장소"]+"*"+review["주소"]
        df["별점"] = review["별점"]
    else :
        df = pd.DataFrame()
        df["이름"] = review.loc[(review["주소1"]==add), "이름"]
        df["장소"] = review.loc[(review["주소1"]==add), "장소"]+"*"+review.loc[(review["주소1"]==add), "주소"]
        df["별점"] = review.loc[(review["주소1"]==add), "별점"]
        df["대분류"] = review.loc[review["주소1"]==add, "대분류"]
        if ctg in [0,1,2,3,4] :
            df = df[df["대분류"]==ctg]
        df.drop(columns=["대분류"], inplace=True)
        df.reset_index(drop=True, inplace=True) 
    return df