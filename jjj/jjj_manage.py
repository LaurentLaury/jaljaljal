from math import sqrt
import cx_Oracle as oci
import numpy as np
import pandas as pd
import re
import os
from surprise import Reader, Dataset
from surprise.model_selection import cross_validate
from surprise import NormalPredictor, KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline, SVD
from surprise import BaselineOnly, SVDpp, NMF, SlopeOne, CoClustering
from surprise.accuracy import rmse
from surprise import accuracy
from surprise.model_selection import train_test_split



os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')

# connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
# cur = connection.cursor()
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user="hr", password="hr")

sql = "select name, place, category, star, address, category1, address1, address2, count, latitude, longitude, year, month, season from recommend"
cursor = conn.cursor()
cursor.execute(sql)
review = cursor.fetchall()
review = pd.DataFrame(review)
review.columns = ['이름', '장소', '분류', '별점', '주소', '대분류', '주소1', '주소2', '방문횟수', '위도', '경도', '년도', '월', '계절']


# 사용자 기반 선호도 예측 알고리즘
# review = pd.read_csv("review_v04.csv", encoding="utf-8-sig")
# u = pd.DataFrame(review.groupby([review["이름"]]).size(), columns=["여행횟수"])
# m = pd.merge(review, u, on="이름", how="left")
# c = m[m["방문횟수"]>=50]
# c = review[review["방문횟수"]>=50]
c=review
df = pd.DataFrame()
df["이름"] = c["이름"]
df["장소"] = c["장소"]+" "+c["주소"]
df["별점"] = c["별점"]

user_base = dict(df.groupby("이름").apply(lambda x : dict(zip(x["장소"], x["별점"]))))
item_base = dict(df.groupby("장소").apply(lambda x : dict(zip(x["이름"], x["별점"]))))


# calc_user_sim_positive
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


# recommend_by_user_base
def recommend_by_user_base(user_i):
    d = pd.DataFrame()
    d["장소"] = np.nan
    d["u_횟수"] = np.nan
    d["r_a"] = np.nan
    d["r_am"] = np.nan
    d["w_0"] = np.nan

    for person in user_base:
        if calc_user_sim_positive(user_i, person) != None:
            for place in user_base[person]:  # 그 사람들이 간 장소를 다 확인
                if place not in user_base[user_i]:
                    r_km = user_base[person][place]  # 장소에 대한 별점
                    w_ak, r_a, _ = calc_user_sim_positive(user_i, person)
                    r_am = (r_km - r_a) * w_ak
                    if place in list(d["장소"]):
                        i = int(d.loc[d["장소"] == place, "u_횟수"])
                        d.loc[d["장소"] == place, "u_횟수"] += 1
                        if f"w_{i}" in list(d.columns):
                            d.loc[d["장소"] == place, "r_a"] += r_a
                            d.loc[d["장소"] == place, "r_am"] += r_am
                            d.loc[d["장소"] == place, f"w_{i}"] = w_ak
                        else:
                            a = pd.DataFrame({"장소": [place], f"w_{i}": [w_ak]})
                            d = pd.merge(d, a, how="left")

                    else:
                        row = {"장소": place, "u_횟수": 1, "r_a": r_a, "r_am": r_am, "w_0": w_ak}
                        d = d.append(row, ignore_index=True)
    d["w_std"] = d.iloc[:, 4:].std(axis=1)
    d["p_am"] = d["r_a"] / d["u_횟수"] + d["r_am"] / (d.iloc[:, 4:-1].sum(axis=1))  # user_i의 장소에 대한 예상 별점

    # return d
    return d[d["u_횟수"] >= 2]


# 아이템 기반 선호도 예측 알고리즘
# calc_item_sim_positive
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


# recommend_by_item_base
def recommend_by_item_base(user_i) :
    d_u = recommend_by_user_base(user_i)
    d = pd.DataFrame()
    d["장소"] = np.nan
    d["횟수"] = np.nan
    d["r_am"] = np.nan
    d["w_0"] = np.nan
    for item in d_u["장소"] :
        for place in user_base[user_i] :       # user_i의 기존 모든 방문장소에 대해
            w_mk = calc_item_sim_positive(item, place)
            if (w_mk != None) :
                r_ak = item_base[place][user_i]
                r_am = r_ak * w_mk
                if item in list(d["장소"]) :
                    i=int(d.loc[d["장소"]==item,"횟수"])
                    d.loc[d["장소"]==item,"횟수"] += 1
                    if f"w_{i}" in list(d.columns) :
                        d.loc[d["장소"]==item,"r_am"] += r_am
                        d.loc[d["장소"]==item, f"w_{i}"] = w_mk
                    else :
                        a = pd.DataFrame({"장소":[item], f"w_{i}":[w_mk]})
                        d = pd.merge(d,a,how="left")
                else :
                    row = {"장소":item, "횟수":1, "r_am":r_am, "w_0":w_mk}
                    d = d.append(row, ignore_index=True)
    w = list(filter(lambda x : re.findall(r"w_\d", x), list(d.columns)))[-1]
    d["w_std"] = d.loc[:,"w_0":w].std(axis=1)
    d["p_am"] = d["r_am"]/(d.loc[:,"w_0":w].sum(axis=1))             # item에 대한 user_i의 예상 별점

    return d[d["횟수"]>=2]


# 하이브리드
def recommend_by_hybrid(user_i):
    u = recommend_by_user_base(user_i)
    r = recommend_by_item_base(user_i)
    rcm = pd.DataFrame()

    for place in r["장소"]:
        p_am_u = float(u.loc[u["장소"] == place, "p_am"])
        p_am_i = float(r.loc[r["장소"] == place, "p_am"])
        std_u = float(u.loc[u["장소"] == place, "w_std"])
        std_i = float(r.loc[r["장소"] == place, "w_std"])
        if (std_i == 0) & (std_u == 0):
            p = (p_am_u + p_am_i) / 2
            alpha = None
            row = {"장소": place, "p_u": p_am_u, "p_i": p_am_i, "alpha": alpha, "p": p}
            rcm = rcm.append(row, ignore_index=True)
        else:
            alpha = std_i / (std_u + std_i)
            p = p_am_u * alpha + p_am_i * (1 - alpha)
            row = {"장소": place, "p_u": p_am_u, "p_i": p_am_i, "alpha": alpha, "p": p}
            rcm = rcm.append(row, ignore_index=True)
    rcm.sort_values(["p"], ascending=False, inplace=True, ignore_index=True)
    rcm = rcm[["장소", "p_u", "p_i", "alpha", "p"]]

    # remove = ['서울특별시','경기도','인천광역시','대전광역시','부산광역시','대구광역시','울산광역시','광주광역시',
    #           '강원도','충청남도','충청북도','경상남도','경상북도','전라남도','전라북도','제주특별자치도']
    # for i in remove:
    #     rcm["장소"] = rcm["장소"].str.split(i).str[0]

    # return rcm[rcm["p"]>3]
    # return rcm.loc[rcm["p"] > 3, ["장소", "p"]]
    result = rcm.loc[rcm["p"] > 3, ["장소", "p"]]
    rows = [tuple(x) for x in result.values]
    sql = """insert into hello
             select :name, :place, :star from dual
             where not exists(select * from hello
             where name=:name and place=:place and star=:star)"""

    cursor = conn.cursor()
    for i in range(len(rows)):
        cursor.execute(sql, {"name": user_i,
                             "place": rows[i][0],
                             "star": rows[i][1]})
    conn.commit()



# 비회원 추천 테이블
# best_predictions = pd.read_csv('best_predictions.csv', encoding='utf-8')
def best_pred():
    review['새주소'] = review['장소'] + "*" + review['주소']
    review2 = review.drop(['장소', '주소', '위도', '경도', '분류', '대분류', '주소1', '주소2', '방문횟수', '년도', '월', '계절'], axis=1)
    review2 = review2[['이름', '새주소', '별점']]

    # 데이터 셋의 차원 줄이기
    # 저조한 평가를 기록한 장소 및 사용자 제외
    min_ratings = 50
    filter_review = review2['새주소'].value_counts() > min_ratings
    filter_review = filter_review[filter_review].index.tolist()

    min_user_ratings = 50
    filter_users = review2['이름'].value_counts() > min_user_ratings
    filter_users = filter_users[filter_users].index.tolist()

    review_new = review2[(review2['새주소'].isin(filter_review)) & (review2['이름'].isin(filter_users))]

    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(review_new[['이름', '새주소', '별점']], reader)

    benchmark = []
    # Iterate over all algorithms
    for algorithm in [SVD(), SVDpp(), SlopeOne(), NMF(), NormalPredictor(), KNNBaseline(), KNNBasic(), KNNWithMeans(),
                      KNNWithZScore, BaselineOnly(), CoClustering()]:
        # Perform cross validation
        algo = NMF()
        results = cross_validate(algo, data, measures=['RMSE'], cv=3, verbose=False)
        trainset, testset = train_test_split(data, test_size=0.25)
        predictions = algo.fit(trainset).test(testset)
        # accuracy.rmse(predictions)

        # Get results & append algorithm name
        tmp = pd.DataFrame.from_dict(results).mean(axis=0)
        tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
        benchmark.append(tmp)

    surprise_results = pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')

    # Train and Predict
    # CoClustering 알고리즘이 가장 좋은 rmse 결과를 보였다. 따라서 CoClustering 사용하여
    # 훈련 및 예측을 진행하고 교대최소제곱(ALS)를 사용할 것
    algo = NMF()
    cross_validate(algo, data, measures=['RMSE'], cv=3, verbose=False)

    # rmse 정확도 훈련셋과 검증셋을 샘플링하기위해 train_Test_split()을 사용
    # rmse 정확도 척도를 사용
    # fit() 메소드를 통해 훈련셋의 알고리즘을 훈련시키고, test() 메소드를 통해 검증셋으로부터
    # 생성된 예측을 반환
    trainset, testset = train_test_split(data, test_size=0.25)
    # algo = BaselineOnly(bsl_options=bsl_options)
    algo = NMF()
    predictions = algo.fit(trainset).test(testset)

    # dump.dump('./dump_file',predictions, algo)
    # predictions, algo = dump.load('./dump_file')

    trainset = algo.trainset

    # 예측을 정확히 살펴보기 위해, 모든 예측에 대한 데이터프레임 생성

    def get_Iu(uid):
        try:
            return len(trainset.ur[trainset.to_inner_uid(uid)])
        except ValueError:  # user was not part of the trainset
            return 0

    def get_Ui(iid):
        try:
            return len(trainset.ir[trainset.to_inner_iid(iid)])
        except ValueError:
            return 0

    df = pd.DataFrame(predictions, columns=['uid', 'iid', 'rui', 'est', 'details'])
    df['Iu'] = df.uid.apply(get_Iu)
    df['Ui'] = df.iid.apply(get_Ui)
    df['err'] = abs(df.est - df.rui)

    predictions = df.sort_values(by='err').drop_duplicates('iid')

    best_predictions = predictions[:100]
    worst_predictions = predictions[-10:]

    # tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]],index=['Algorithm']))
    best_predictions['iid'] = best_predictions.iid.str.split('*').str[0]

    sql = "insert into rec(rec_uid, rec_iid, rec_rui, rec_est) values(:rec_uid, :rec_iid, :rec_rui, :rec_est)"
    data = best_predictions[['uid', 'iid', 'rui', 'est']]
    data.columns = ['rec_uid', 'rec_iid', 'rec_rui', 'rec_est']
    # print(dict(data.iloc[i,]))

    for i in range(len(data)):
        cursor.execute(sql, dict(data.iloc[i,]))

    conn.commit()





