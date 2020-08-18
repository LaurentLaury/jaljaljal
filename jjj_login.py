# # jjj_manage에 들어가는 로그인 함수
# # 고객 존재 여부 확인

import cx_Oracle as oci
import os
import pandas as pd


os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user="hr", password="hr")

sql = "select name from recommend"
cursor = conn.cursor()
cursor.execute(sql)
review = cursor.fetchall()
cursor.close()
review = pd.DataFrame(review)
review.columns = ['이름']

c=review
df = pd.DataFrame()
df["이름"] = c["이름"]

#고객 정보 확인
def checking_name(inserted_name):
    if df["이름"].str.contains(inserted_name).any():
        return 1
    else:
        return 0


conn.close()


