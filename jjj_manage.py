import cx_Oracle as oci
# db
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user ="hr", password="hr")

class Recommend() :
    def __init__(self, name, category, addr, est):
        self.name = name
        self.category = category
        self.addr = addr
        self.est = est

    def __str__(self):
        return f"{self.name}, {self.category}, {self.addr}, {self.est}"

    def to_dict(self):
        return {"name":self.name, "category":self.category, "addr":self.addr, "est":self.est}


# 비회원 추천 목록 가져오는 쿼리
def get_rec():
    # sql = "select rec_uid, rec_iid, rec_rui, rec_est from rec"
    # 장소, 카테고리, 주소, 별점
    sql = "select a.rec_iid as name, case b.category1 when 0 then '음식점' when 1 then '숙박' when 2 then '관광지' when 3 then '카페' when 4 then '술집' end as category, b.address as addr, a.rec_est as est from rec a left outer join recommend b on a.rec_iid = b.place and a.rec_uid = b.name"
    cursor = conn.cursor()
    cursor.execute(sql)
    reco = []
    for data in cursor:
        reco.append(Recommend(*data))
    print(reco)
    return reco

