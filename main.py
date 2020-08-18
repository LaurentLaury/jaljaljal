# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:26:08 2020

@author: COM
"""

#%%

# import sys
# sys.path.append("C:\\pylib")
import cx_Oracle
import os
import get
import recommend_hybrid
import recommend_svd

review = get.get_data()

def recommend(user_i,df) :
    try :
        result = recommend_hybrid.do(user_i, df)
        if len(result) < 100 :
            result2 = recommend_svd.do(user_i, df)
            for place in result2["place"] :
                if place not in result["place"] :
                    row = {"place":place, "rating":float(result2.loc[result2["place"]==place, "rating"])}
                    result = result.append(row, ignore_index=True)
                if len(result)== 100 :
                    break
    except :
        result = recommend_svd.do(user_i, df)
    return result[:100]

def main(user_i, add=None, ctg=5) : 
    if add == None :
        df = get.get_df()
        result = recommend(user_i, df)

        os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
        connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
        cur = connection.cursor()
        sql = "insert into jjj_rec(name, place, rating, region) values(:name, :place, :rating, :region)"

        for i in range(len(result)):
            cur.execute(sql, dict(result.iloc[i, :]))
        connection.commit()
        # 커넥션 종료
        cur.close()
        connection.close()

    else :
        df = get.get_df(add, ctg)
        result = recommend_svd.do(user_i, df)
        result["category"]=ctg
        result["address1"]=add
        os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
        connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
        cur = connection.cursor()
        sql = "insert into jjj_rec_add(name, place, rating, region, category, address1) " \
              "values(:name, :place, :rating, :region, :category, :address1)"

        for i in range(len(result)):
            cur.execute(sql, dict(result.iloc[i, :]))
        connection.commit()
        # 커넥션 종료
        cur.close()
        connection.close()

    return result


def get_chart_data(reco) :
    M = []
    L = []
    address_count = []
    ctg_count = []
    for data in reco:
        M.append(data[5])
        L.append(data[2])
    for address in set(M):
        address_count.append([address, M.count(address)])
    for ctg in set(L):
        ctg_count.append([ctg, L.count(ctg)])
    return address_count, ctg_count

def get_recommend_info(name) :
    os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
    conn = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
    sql = """select name, place, category, region, round(rating,2) as rating, address1
           from (select distinct a.name as name, a.place as place, a.region as region, a.rating as rating
           , case b.category1 when 0 then '음식점'
                            when 1 then '숙박'
                            when 2 then '관광지'
                            when 3 then '카페'
                            when 4 then '술집' end as category
            , b.address1 as address1
            from jjj_rec a
            left outer join recommend b
            on a.place= b.place
            and a.region = b.address 
            order by a.rating desc)
            where name=:name"""
    cursor = conn.cursor()
    cursor.execute(sql, {"name": name})
    reco = []
    for data in cursor:
        reco.append(data)
    return reco
