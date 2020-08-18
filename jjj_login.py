# # jjj_manage에 들어가는 로그인 함수
# # 고객 존재 여부 확인

import cx_Oracle as oci
import os
import pandas as pd


os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user="hr", password="hr")

name_list=[]
sql = "select distinct name from recommend"
cursor = conn.cursor()
cursor.execute(sql)

for name in cursor :
    name_list.append(name[0])

cursor.close()
conn.close()

#고객 정보 확인
def checking_name(inserted_name):
    if inserted_name in name_list:
        return 1
    else:
        return 0




