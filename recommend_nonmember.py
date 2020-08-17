import pandas as pd
# -*- coding: utf-8 -*-
import cx_Oracle
#패키지 추가
import pandas as pd
from surprise import Reader, Dataset
from surprise.model_selection import cross_validate
from surprise import NormalPredictor, KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline, SVD
from surprise import BaselineOnly, SVDpp, NMF, SlopeOne, CoClustering
from surprise.accuracy import rmse
from surprise import accuracy
from surprise.model_selection import train_test_split
import os
os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')

connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
cur = connection.cursor()
cur.execute("select name, place, category, star, address,category1, address1, address2, count, latitude, longitude, year, month, season from recommend  ")

review = cur.fetchall()
review = pd.DataFrame(review)

# 커넥션 종료
cur.close()
connection.close()

# df 컬럼 이름 변경
review.columns = ['이름', '장소', '분류', '별점', '주소', '대분류', '주소1', '주소2', '방문횟수', '위도', '경도', '년도', '월', '계절']
review['새주소'] = review['장소'] + "*" + review['주소']
review2 = review.drop(['장소', '주소', '위도', '경도', '분류', '대분류', '주소1', '주소2', '방문횟수', '년도', '월', '계절'], axis=1)

review2 = review2[['이름', '새주소', '별점']]

# 데이터 셋의 차원 줄이기
min_ratings = 50
filter_review = review2['새주소'].value_counts() > min_ratings
filter_review = filter_review[filter_review].index.tolist()

min_user_ratings = 50
filter_users = review2['이름'].value_counts() > min_user_ratings
filter_users = filter_users[filter_users].index.tolist()

review_new = review2[(review2['새주소'].isin(filter_review)) & (review2['이름'].isin(filter_users))]

reader = Reader(rating_scale=(0,5))
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
    accuracy.rmse(predictions)

    # Get results & append algorithm name
    tmp = pd.DataFrame.from_dict(results).mean(axis=0)
    tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
    benchmark.append(tmp)

pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')

surprise_results = pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')

# train and predict
algo = NMF()
cross_validate(algo,data,measures=['RMSE'], cv=3, verbose=False)

# rmse 정확도 훈련셋과 검증셋을 샘플링하기위해 train_Test_split()을 사용
# rmse 정확도 척도를 사용
# fit() 메소드를 통해 훈련셋의 알고리즘을 훈련시키고, test() 메소드를 통해 검증셋으로부터
# 생성된 예측을 반환
trainset, testset = train_test_split(data, test_size=0.25)
algo = NMF()
predictions = algo.fit(trainset).test(testset)
accuracy.rmse(predictions)
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
# review_new.loc[review_new['새주소'] == '롯데월드 서울특별시 송파구 잠실동 올림픽로 240']['별점'].describe()

# import matplotlib.pyplot as plt
# %matplotlib inline
# review_new.loc[review['장소'] == '전쟁기념관']['별점'].hist()
# plt.xlabel('rating')
# plt.ylabel('Number of ratings')
# plt.title('Number of ratings place has received')
# plt.show()

#데이터 저장하기 (df -> db)
# -*- coding: utf-8 -*-
import cx_Oracle
import os
os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')


connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
cur = connection.cursor()
sql = "insert into rec(rec_uid, rec_iid, rec_rui, rec_est) values(:rec_uid, :rec_iid, :rec_rui, :rec_est)"
data = best_predictions[['uid', 'iid', 'rui', 'est']]
data.columns = ['rec_uid', 'rec_iid', 'rec_rui', 'rec_est']
# print(dict(data.iloc[i,]))

for i in range(len(data)):
    cur.execute(sql, dict(data.iloc[i,]))
connection.commit()

# 커넥션 종료
cur.close()
connection.close()