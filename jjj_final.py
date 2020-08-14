from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import folium
import main as mm
import best_predictions as bp
import jjj_login as jl


app = Flask(__name__)

# 로그인 기능
@app.route("/home")
def home():
    return render_template("jjj/home.html")


@app.route("/post", methods=['POST'])
def post():
    value = request.form['input']
    result = jl.checking_name(value)
    if (result == 1):
        return render_template("jjj/login_success.html", name=value)
    else:
        return render_template("jjj/login_fail.html", name=value)


@app.route("/rec/<name>")
def rec(name):
    result = mm.main(name)
    result_1 = result.to_json(orient='records', force_ascii=False)
    result_2 = result_1.load_json()
    return render_template("jjj/rec.html", data=result_2)

# @app.route("/rec/<name>")
# def rec(name):
#     result = mm.main(name)
#     result_1 = f"{{ from: {result['장소']}, to: {result['장소']}, {result['p']} }}"
#
#     return render_template("jjj/rec.html", data=result_1)


@app.route("/rec/<name>/<area>")
def rec_area(name, area):
    result = mm.main(name, area)
    result_1 = result.to_json(orient='records', force_ascii=False)
    return render_template("jjj/rec_area.html", data=result_1)


@app.route("/rec/<name>/<area>/<ctg>")
def rec_ctg(name, area, ctg):
    result = mm.main(name, area, ctg)
    result_1 = result.to_json(orient='records', force_ascii=False)
    return render_template("jjj/rec_ctg.html", data=result_1)

@app.route("/best_pred")
def best_pred():
    result = bp.best_pred()
    result_1 = result.to_json(orient='records', force_ascii=False)
    return render_template("jjj/best_pred.html", data=result_1)



if __name__=='__main__':
    app.debug = True
    app.run()
