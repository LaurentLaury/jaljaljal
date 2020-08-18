import cx_Oracle as oci
# db
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user ="hr", password="hr")

class Recommend() :
    def __init__(self, idx, name, category, addr, est):
        self.idx = idx
        self.name = name
        self.category = category
        self.addr = addr
        self.est = est


    def __str__(self):
        return f"{self.idx}, {self.name}, {self.category}, {self.addr}, {self.est}"

    def to_dict(self):
        return {"idx":self.idx, "name":self.name, "category":self.category, "addr":self.addr, "est":self.est}

class Comment() :
    def __init__(self, name, star, review):
        self.name = name
        self.star = star
        self.review = review

    def __str__(self):
        return f"{self.name}, {self.star}, {self.review}"

    def to_dict(self):
        return {"name":self.name, "star":self.star, "review":self.review}


# 비회원 추천 목록 가져오는 쿼리
def get_rec():
    # sql = "select rec_uid, rec_iid, rec_rui, rec_est from rec"
    # 장소, 카테고리, 주소, 별점
    sql = "select a.idx as idx, a.rec_iid as name, case b.category1 when 0 then '음식점' when 1 then '숙박' when 2 then '관광지' when 3 then '카페' when 4 then '술집' end as category, b.address as addr, a.rec_est as est from rec a left outer join recommend b on a.rec_iid = b.place and a.rec_uid = b.name order by idx"
    cursor = conn.cursor()
    cursor.execute(sql)
    reco = []
    for data in cursor:
        reco.append(Recommend(*data))
    cursor.close()
    return reco

# 비회원 추천 목록 댓글 더보는 쿼리
def find_comment(place):
    sql = "select name, star, review from recommend where place =: place and review not in ('nan') order by star desc"
    cursor = conn.cursor()
    cursor.execute(sql, {"place":place})
    com = []
    for data in cursor:
        com.append(Comment(*data))
    cursor.close()
    return com

