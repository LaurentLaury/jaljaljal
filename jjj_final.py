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



@app.route("/hybrid/<name>")
def hybrid(name):
    result = mm.main(name)
    return render_template("jjj/hybrid.html", data=result)

# 혜민 test
@app.route("/chart")
def chart():
    return render_template("jjj/chart_analysis.html")


if __name__=='__main__':
    app.debug = True
    app.run()
