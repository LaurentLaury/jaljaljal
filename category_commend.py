import cx_Oracle as oci
oracle_dsn = oci.makedsn(host="192.168.2.27", port=1521, sid="xe")
conn = oci.connect(dsn=oracle_dsn, user="hr", password="hr")

def get_name(name):
    sql = "select distinct name from recommend where name=:name"
    cursor = conn.cursor()
    cursor.execute(sql, {"name": name})
    result = cursor.fetchall()
    cursor.close()
    return result


def get_address1():
    sql = "select distinct address1 from recommend order by address1"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_category1():
    # sql = """select distinct case category1
    #          when 0 then '음식점'
    #          when 1 then '숙박'
    #          when 2 then '관광지'
    #          when 3 then '카페'
    #          when 4 then '술집' else '없음'
    #          end as category1
    #          from recommend order by category1"""
    sql = "select distinct category1 from recommend order by category1"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result