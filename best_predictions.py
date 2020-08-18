# 비회원 추천 테이블
import os
import cx_Oracle as oci
import pandas as pd
from surprise import Reader, Dataset
from surprise.model_selection import cross_validate
from surprise import NormalPredictor, KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline, SVD
from surprise import BaselineOnly, SVDpp, NMF, SlopeOne, CoClustering
from surprise.accuracy import rmse
from surprise import accuracy
from surprise.model_selection import train_test_split

os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user="hr", password="hr")

cursor = conn.cursor()
cursor.execute(
    'select name, place, category, star, address ,category1, address1, address2, count, latitude, longitude, year, month, season from recommend ')

review = []
for result in cursor:
    # print(result)
    review.append(result)
# print(len(review))
# 커넥션 종료
cursor.close()
conn.close()

review = pd.DataFrame(review)
review.columns = ['이름', '장소', '분류', '별점', '주소', '대분류', '주소1', '주소2', '방문횟수', '위도', '경도', '년도', '월', '계절']

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
    cursor.close()
    conn.close()
    return data
    # # print(dict(data.iloc[i,]))
    #
    # for i in range(len(data)):
    #     cursor.execute(sql, dict(data.iloc[i,]))
    #
    # conn.commit()
    # cursor.close()
    # conn.close()