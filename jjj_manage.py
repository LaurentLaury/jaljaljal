import cx_Oracle as oci
# db
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user ="hr", password="hr")

# 비회원 추천 목록 가져오는 쿼리
def get_rec():
    sql = "select rec_uid, sec_iid, rec_rui, rec_est from rec"
    cursor = conn.cursor()
    cursor.execute(sql)
    query = cursor.fetchall()
    return query

