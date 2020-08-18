# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:34:36 2020

@author: COM
"""
import pandas as pd
from math import sqrt
import numpy as np

# global user_base
# global item_base

# def group_base(df) :
#     # global user_base
#     # global item_base
#     user_base = dict(df.groupby("이름").apply(lambda x : dict(zip(x["장소"], x["별점"]))))
#     item_base = dict(df.groupby("장소").apply(lambda x : dict(zip(x["이름"], x["별점"]))))

# def __init__(self, user_base, item_base) :
#     self.user_base = user_base
#     self.item_base = item_base

def calc_user_sim_positive(user_i, user_j) :
    if user_i != user_j :
        li_i = []
        li_j = []
        for i in user_base[user_i] :
            if i in user_base[user_j] :
                li_i.append(user_base[user_i][i])
                li_j.append(user_base[user_j][i])
        if len(li_i) != 0 :                              # 공통 여행지가 존재 해야
            n_i = np.array(li_i)
            n_j = np.array(li_j)
            r_a = np.mean(n_i)
            r_u = np.mean(n_j)        
            r_i = n_i - r_a
            r_j = n_j - r_u
            if (r_i.all() != 0) & (r_j.all() != 0) :    # 모든 별점이 동일한 경우 제외
                w_ij = np.sum(r_i*r_j)/(sqrt(np.sum(r_i**2))*sqrt(np.sum(r_j**2)))
                if w_ij > 0 :
                    return w_ij, r_a, r_u   
            else : 
                pass
        else :
            pass

def calc_item_sim_positive(item_i, item_j) :
    li_i = []
    li_j = []
    try : 
        for i in item_base[item_i] :
            if i in item_base[item_j] :
                li_i.append(item_base[item_i][i])
                li_j.append(item_base[item_j][i])
        if len(li_i) != 0 :                              # 두 장소를 모두 간 사람이 존재해야
            n_i = np.array(li_i)
            n_j = np.array(li_j)
            r_i = n_i - np.mean(n_i)
            r_j = n_j - np.mean(n_j)
            if (r_i.all() != 0) & (r_j.all() != 0) :    # 모든 별점이 동일한 경우 제외
                w_ij = np.sum(r_i*r_j)/(sqrt(np.sum(r_i**2))*sqrt(np.sum(r_j**2)))
                if w_ij > 0 :
                    return w_ij   
            else : 
                pass
        else :
            pass
    except :
        pass
    
def recommend_user_base(user_i) :
    M=[]
    for person in user_base : 
        if calc_user_sim_positive(user_i, person) != None :
            for place in user_base[person] :                   # 그 사람들이 간 장소를 다 확인
                if place not in user_base[user_i] :
                    r_km = user_base[person][place]             # 장소에 대한 별점
                    w_ak, r_a,_ = calc_user_sim_positive(user_i, person)           
                    M.append([place, 1, r_km, r_a, w_ak])
    df = pd.DataFrame(M)
    df.columns=["장소", "횟수", "r_km","r_a","w_ak"]
    
    L = []
    place_set = set(df["장소"])
    for place in place_set : 
        if int(len(df[df["장소"]==place]))>=2 : 
            a = df.loc[df["장소"]==place,"r_a"]
            w = df.loc[df["장소"]==place,"w_ak"]
            r_am = df.loc[df["장소"]==place,"r_km"].apply(lambda x : x-a.mean())
            r = r_am * w
            p = a.mean() + r.sum()/w.sum()
            L.append([place, p])
    d = pd.DataFrame(L)
    d.columns=["장소","p_am"]
    d.sort_values(["p_am"], ascending=False, inplace=True)
    return d, df

def recommend_item_base(user_i) :
    d_u,_ = recommend_user_base(user_i)
    M=[]
    for item in d_u["장소"] :
        for place in user_base[user_i] :       # user_i의 기존 모든 방문장소에 대해
            w_mk = calc_item_sim_positive(item, place)
            if (w_mk != None) :                  
                r_ak = item_base[place][user_i]
                r_am = r_ak * w_mk
                L = [item, 1, r_am, w_mk]
                M.append(L)
    df = pd.DataFrame(M)
    df.columns=["장소","횟수","r_am","w_mk"]
    d = df.groupby(["장소"]).sum()
    d.reset_index(inplace=True)
    d["p_am"] = d["r_am"]/d["w_mk"]
    return d[d["횟수"]>=2], df

def recommend_hybrid(user_i) :
    u, u_s = recommend_user_base(user_i)
    r, r_s = recommend_item_base(user_i)
    M=[]
    for place in r["장소"] :
        p_am_u = float(u.loc[u["장소"]==place, "p_am"])
        p_am_i = float(r.loc[r["장소"]==place, "p_am"])
        std_u = u_s[u_s["장소"]==place]["w_ak"].std()
        std_i = r_s[r_s["장소"]==place]["w_mk"].std()
        if (std_i==0) & (std_u==0) :
            p = (p_am_u + p_am_i)/2
            alpha = None
            L = [place, p_am_u, p_am_i, alpha, p]
            M.append(L)
        else : 
            alpha = std_i / (std_u+std_i)
            p = p_am_u * alpha + p_am_i * (1-alpha)
            L = [place, p_am_u, p_am_i, alpha, p]
            M.append(L)        
    df = pd.DataFrame(M)
    df.columns=["장소", "p_u","p_i","alpha","p"]
    df.sort_values(["p"], ascending=False, inplace=True, ignore_index=True)
    df["이름"] = user_i
    df["주소"] = df["장소"].map(lambda x : x.split('*')[1])
    df["장소"] = df["장소"].map(lambda x : x.split('*')[0])
    df.reset_index(drop=True, inplace=True)
    df = df.loc[:,["이름","장소","p", "주소"]]
    df = df[["이름", "장소","p", "주소"]]
    df.columns=["name", "place", "rating", "region"]
    return df[df["rating"]>3]

def do(user_i, df) :
    global user_base
    global item_base
    user_base = dict(df.groupby("이름").apply(lambda x : dict(zip(x["장소"], x["별점"]))))
    item_base = dict(df.groupby("장소").apply(lambda x : dict(zip(x["이름"], x["별점"]))))
   
    return recommend_hybrid(user_i)