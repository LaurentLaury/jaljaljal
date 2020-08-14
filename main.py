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

get.get_data()

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
    return result

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

