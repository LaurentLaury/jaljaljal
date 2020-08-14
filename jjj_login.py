# # jjj_jl에 들어가는 로그인 함수
# # 고객 존재 여부 확인
# import os
import cx_Oracle
# os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
# oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
# conn = oci.connect(dsn=oracle_dsn, user="hr", password="hr")
# connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
# cur = connection.cursor()
# cur.execute(
#     'select name, place, category, star, address ,category1, address1, address2, count, latitude, longitude, year, month, season from recommend')
# # def checking_name(inserted_name):
#
#     if df["이름"].str.contains(inserted_name).any():
#         return 1
#     else:
#         return 0
import os
os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')

connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
cur = connection.cursor()
cur.execute("select membername from member")

member = []
for result in cur:
    member.append(result[0])
# 커넥션 종료
cur.close()
connection.close()

def checking_name(inserted_name):
    if inserted_name in member :
        return 1
    else :
        return 0