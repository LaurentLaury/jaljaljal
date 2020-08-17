from flask import Flask, render_template, request, redirect
import cx_Oracle
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import folium
import recommend_hybrid as rh
import recommend_svd as rs
import get
import main as mm
import jjj_login as jl
import jjj_manage as jm


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




if __name__=='__main__':
    app.debug = True
    app.run()
