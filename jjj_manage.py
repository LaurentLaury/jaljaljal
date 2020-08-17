import cx_Oracle as oci
# db
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user ="hr", password="hr")

# 비회원 추천 목록 가져오는 쿼리
def get_rec():
    # sql = "select rec_uid, rec_iid, rec_rui, rec_est from rec"
    # 장소, 카테고리, 주소, 별점
    sql = "select a.rec_iid, case b.category1 when 0 then '음식점' when 1 then '숙박' when 2 then '관광지' when 3 then '카페' when 4 then '술집' end as category, b.address, a.rec_est from rec a left outer join recommend b on a.rec_iid = b.place and a.rec_uid = b.name"
    cursor = conn.cursor()
    cursor.execute(sql)
    query = cursor.fetchall()
    return query

