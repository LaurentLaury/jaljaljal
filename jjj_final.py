from flask import Flask, render_template, request

import jjj_login as jl
import jjj_manage as jm
import main as mm

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


@app.route("/chart/<name>")
def chart(name):
    result = mm.get_recommend_info(name)
    address_count, ctg_count = mm.get_chart_data(result)
    length = len(address_count)
    return render_template("jjj/graph1.html", data=address_count, len = length)

@app.route("/hybrid/<name>")
def hybrid(name):
    os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
    connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
    cur = connection.cursor()
    cur.execute("select distinct name from jjj_rec ")
    member = []
    for result in cur:
        member.append(result[0])
    cur.close()
    connection.close()

    if name not in member:
        mm.main(name)

    reco = mm.get_recommend_info(name)

    return render_template("jjj/hybrid.html", data=reco)

# 혜민 test
@app.route("/chart")
def chart():
    return render_template("jjj/chart_analysis.html")


@app.route("/normal_comment/<name>", methods=['GET'])
def user_result(name):
    value = name
    result = jl.checking_name(value)
    jjj_reco = jm.get_jjj_rec()
    return render_template("jjj/nomal_comment.html" , name=value, data=jjj_reco)


@app.route("/svd/<name>")
def svd(name):
    os.putenv('NLS_LANG', 'KOREAN_KOREA.KO16MSWIN949')
    connection = cx_Oracle.connect('hr/hr@192.168.2.27:1521/xe')
    cur = connection.cursor()
    cur.execute("select distinct name from jjj_rec ")
    member = []
    for result in cur:
        member.append(result[0])
    cur.close()
    connection.close()

    if name not in member:
        mm.main(name)

    reco = mm.get_recommend_info(name)

    return render_template("jjj/hybrid.html", data=reco)

if __name__=='__main__':
    app.debug = True
    app.run()
