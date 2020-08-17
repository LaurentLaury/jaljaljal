# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:26:08 2020

@author: COM
"""

#%%

# import sys
# sys.path.append("C:\\pylib")

import get
import recommend_hybrid
import recommend_svd

review = get.get_data()

def recommend(user_i,df) :
    try :
        result = recommend_hybrid.do(user_i, df)
        if len(result) < 100 :
            result2 = recommend_svd.do(user_i, df)
            for place in result2["iid"] :
                if place not in result["장소"] :
                    row = {"장소":place, "p":float(result2.loc[result2["iid"]==place, "est"])}
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
    else :
        df = get.get_df(add, ctg)
        result = recommend_svd.do(user_i, df)    
    result["주소"] = result["장소"].map(lambda x : x.split('*')[1])
    result["장소"] = result["장소"].map(lambda x : x.split('*')[0])
    result.reset_index(drop=True, inplace=True)
    result.columns=["name", "place", "p", "address"]
    return result

def get_recommend_info(result) :
    M=[]
    L=[]
    address_count=[]
    ctg_count=[]
    place=result["장소"]
    address=result["주소"]
    for i in range(100) :
        add = review.loc[(review["장소"]==place[i])&(review["주소"]==address[i]),"주소1"].max()
        ctg = review.loc[(review["장소"]==place[i])&(review["주소"]==address[i]),"대분류"].mean()
        M.append(add)
        L.append(ctg)
    for address in set(M) :
        address_count.append([address, M.count(address)])
    for ctg in set(L) :
        if ctg == 0 :
            ctg_count.append(["음식점", L.count(ctg)])
        elif ctg==1:
            ctg_count.append(["숙박", L.count(ctg)])
        elif ctg==2:
            ctg_count.append(["관광지", L.count(ctg)])
        elif ctg==3:
            ctg_count.append(["카페", L.count(ctg)])
        elif ctg==4:
            ctg_count.append(["술집", L.count(ctg)])
        else :
            pass
    return address_count, ctg_count
# #%%
# import time
# start = time.time()
# r1 = main("빅픽쳐한뫼")
# print(time.time()-start)
#
# #%%
# import time
# start = time.time()
# r2 = main("빅픽쳐한뫼","부산")
# print(time.time()-start)
#
# #%%
# import time
# start = time.time()
# r3 = main("빅픽쳐한뫼","부산",0)
# print(time.time()-start)

