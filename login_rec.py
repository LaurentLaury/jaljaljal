# 회원 추천 목록 가져오는 쿼리
class user_Recommend() :
    def __init__(self, name, place, rating, region, category,insert_date):
        self.name = name
        self.place = place
        self.rating = rating
        self.region = region
        self.category = category
        self.insert_date = insert_date


    def __str__(self):
        return f"{self.name}, {self.place}, {self.rating}, {self.region}, {self.category},{self.insert_date}"

    def to_dict(self):
        return {"name":self.name, "place":self.place, "rating":self.rating, "region":self.region, "category":self.category, "insert_date":self.insert_date}

def get_jjj_rec():
    sql = "select a.name as name, a.place as place , case b.category1 when 0 then '음식점' when 1 then '숙박' when 2 then '관광지' when 3 then '카페' when 4 then '술집' end as category,a.rating as rate, a.region as region from jjj_rec a left outer join recommend b on a.place = b.place and a.name = b.name and b.address=a.region"
    cursor = conn.cursor()
    cursor.execute(sql)
    jjj_reco = []
    for data in cursor:
        jjj_reco.append(Recommend(*data))
    return jjj_reco