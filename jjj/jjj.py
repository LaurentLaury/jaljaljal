from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import folium
import hybrid as hb
import rec
import jjj_manage as jm


app = Flask(__name__)


# @app.route("/user_base/<name>")
# def user_base(name):
#     result = jm.recommend_by_user_base(name)
#     result_1 = result.to_json(orient='records', force_ascii=False)
#     return render_template("jjj/user_base.html", data=result_1)


# @app.route("/item_base/<name>")
# def item_base(name):
#     result = jm.recommend_by_item_base(name)
#     result_1 = result.to_json(orient='records', force_ascii=False)
#     return render_template("jjj/item_base.html", data=result_1)


# @app.route("/hybrid/<name>")
# def hybrid(name):
#     result = hb.recommend_by_hybrid(name)
#     result_1 = result.to_json(orient='records', force_ascii=False)
#     return render_template("jjj/hybrid.html", data=result)
@app.route("/hybrid/<name>")
def hybrid(name):
    jm.recommend_by_hybrid(name)
    return render_template("jjj/hybrid.html")


@app.route("/best_pred")
def best_pred():
    rec.best_pred()
    return render_template("jjj/best_pred.html")


@app.route("/folium")
def folium():
    with open(r'TL_SCCO_CTPRVN.json', encoding='UTF-8') as f:
        geojson_data = json.load(f)
    return render_template("jjj/folium.html", data=geojson_data)


@app.route("/graph1")
def graph1():
    return render_template("jjj/graph1.html")


@app.route("/graph2")
def graph2():
    return render_template("jjj/graph2.html")


if __name__=='__main__':
    app.debug = True
    app.run()


