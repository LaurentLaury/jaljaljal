import os
import cx_Oracle
from flask import Flask, render_template, request
import jjj_login as jl
import jjj_manage as jm
import main as mm
import category_commend as cc
app = Flask(__name__)

# 로그인 기능
@app.route("/")
def home():
    return render_template("jjj/home.html")


@app.route("/post", methods=['POST'])
def post():
    value = request.form['input']
    result = jl.checking_name(value)
    reco = jm.get_rec()
    if (result == 1):
        return render_template("jjj/login_success.html", name=value)
    else:
        return render_template("jjj/login_fail.html", name=value, data = reco)

@app.route("/unmember/comment/<place>", methods=['GET'])
def find_comment(place):
    com = jm.find_comment(place)
    return render_template("jjj/unmember_comment.html", data= com)


@app.route("/chart/<name>", methods=['GET'])
def chart(name):
    result = mm.get_recommend_info(name)
    address_count, ctg_count = mm.get_chart_data(result)
    add_length = len(address_count)
    ctg_length = len(ctg_count)
    return render_template("jjj/graph1.html", add_data=address_count, add_len = add_length, ctg_data = ctg_count, ctg_len=ctg_length, name=name)

@app.route("/hybrid/<name>", methods=['GET'])
def hybrid(name):
    os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
    connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
    cur = connection.cursor()
    cur.execute("select distinct name from jjj_rec ")
    member = []
    for result in cur:
        member.append(result[0])

    if name not in member:
        mm.main(name)
    reco = mm.get_recommend_info(name)
    cur.close()
    return render_template("jjj/hybrid.html", data=reco, name=name)


# @app.route("/normal_comment/<name>", )
# def user_result(name):
#     value = name
#     result = jl.checking_name(value)
#     jjj_reco = jm.get_jjj_rec()
#     return render_template("jjj/nomal_comment.html" , name=value, data=jjj_reco)




@app.route("/location_recommend/<name>", methods=["GET"])
def location_commend(name):
    value = name
    name = cc.get_name(value)
    address1_list = cc.get_address1()
    return render_template("jjj/location_recommend.html", name=value, data={"name": name, "address1_list": address1_list})

@app.route("/location_recommend", methods=["GET"])
def rec_addr_ctg():
    name = request.form["name"]
    add = request.form["address1"]

    os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
    connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
    cur = connection.cursor()
    cur.execute("select distinct name from jjj_rec_add where address1=:address1", {"address1":add})
    member = []
    for result in cur:
        member.append(result[0])
    cur.close()
    connection.close()

    if name not in member:
        mm.main(name, add)

    result = mm.get_recommend_info(name, add)

    return render_template("jjj/category_commend2.html", data=result)


# @app.route("/category_commend", methods=["POST"])
# def rec_addr_ctg():
#     name = request.form["name"]
#     add = request.form["address1"]
#     ctg = int(request.form["category1"])
#     print(ctg)
#
#     os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
#     connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
#     cur = connection.cursor()
#     cur.execute("select distinct name from jjj_rec_add where category=:category and address1=:address1", {"category":ctg, "address1":add})
#     member = []
#     for result in cur:
#         member.append(result[0])
#     cur.close()
#     connection.close()
#
#     if name not in member:
#         mm.main(name, add, ctg)
#
#     result = mm.get_recommend_info(name, add, ctg)
#
#     return render_template("jjj/category_commend2.html", data=result)



if __name__=='__main__':
    app.debug = True
    app.run()
