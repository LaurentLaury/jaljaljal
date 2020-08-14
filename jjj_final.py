from flask import Flask, render_template, request, redirect
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


@app.route("/hybrid/<name>")
def hybrid(name):
    result = mm.main(name)
    result_1 = result.to_json(orient='records', force_ascii=False)
    return render_template("jjj/hybrid.html", data=result_1)




if __name__=='__main__':
    app.debug = True
    app.run()
