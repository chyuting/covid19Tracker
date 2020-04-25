######################
# Flask app
# Author: Yuting Chen
# Uniquename: chyuting
######################

from flask import Flask, render_template, request
from flask_caching import Cache
import plotly
import plotly.graph_objs as go
import os
import random
import requests
import datetime
import sqlite3
import crawlCDC
import JHU_API

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "null", # Flask-Caching related configs
}
app = Flask(__name__)
app.config.from_mapping(config)
today = crawlCDC.today
cache = crawlCDC.open_cache()
if cache == {}:
    crawlCDC.update()
    cache = crawlCDC.open_cache()

DB_NAME = JHU_API.DB_NAME # built database is required
region_list = JHU_API.read_regions()

def get_history_data_by_state(state_nm):
    if state_nm in region_list:
        q = f'''
        SELECT * FROM Counts 
        JOIN Regions
        WHERE RegionId = Regions.Id
        AND RegionName = '{state_nm}'
        ORDER BY Date DESC
        '''
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        results = cur.execute(q).fetchall()
        conn.close()
        return results

def _todate(str):
    '''change str to a date obj'''
    y,m,d = str.split('-')
    return datetime.date(year=int(y), month=int(m), day=int(d))

def plot_stacked_bar(cache):
    ''' Plot stacked bar figure'''
    tend = cache['date']
    x_vals = [_todate(key) for key in tend.keys()] # dates
    y1_vals = [tend[key][0]-tend[key][1] for key in tend.keys()]
    y2_vals = [tend[key][1] for key in tend.keys()]
    stacked_fig = go.Figure(
        data=[
            go.Bar(name='New cases', x=x_vals, y=y2_vals),
            go.Bar(name='Accumulated cases', x=x_vals, y=y1_vals)
        ]
    )
    stacked_fig.update_layout(barmode='stack',  xaxis={'categoryorder': 'category ascending'})
    stacked_fig.write_image('static/acc_new.png')

def plot_pie_charts(cache):
    ''' Plot 3 distribution pie charts'''
    # distribution by states
    state = cache['state']
    labels, values =[], []
    for key,value in state.items():
        if key != None and value != 'None':
            labels.append(key)
            values.append(value)
    pie_fig = go.Figure(
        data=[go.Pie(labels=labels, values=values)]
    )
    pie_fig.update_traces(textposition='inside')
    pie_fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
    pie_fig.write_image('static/state_pie.png')

    # distribution by age
    age = cache['age']
    labels = [key for key in age.keys() if key != 'Total']
    values = [age[key] for key in labels]
    pie_fig = go.Figure(
        data=[go.Pie(labels=labels, values=values)]
    )
    pie_fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
    pie_fig.write_image('static/age.png')

    # distribution by race
    race = cache['race']
    labels = list(race.keys())
    values = list(race.values())
    pie_fig = go.Figure(
        data=[go.Pie(labels=labels, values=values)]
    )
    pie_fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
    pie_fig.write_image('static/race.png')

def plot(state_nm, data):
    x_vals = [i[2] for i in data] # date
    y1_vals = [i[3] for i in data] # total cases
    y2_vals = [i[5] for i in data] # total deaths
    fig = go.Figure(
        data=[
            go.Scatter(name='Accumulated cases', x=x_vals, y=y1_vals, line = dict(width=4, dash='dash')),
            go.Scatter(name='Deaths', x=x_vals, y=y2_vals, line=dict(width=4, dash='dash'))
        ]
    )
    print('generating pictures')
    fig.update_layout(xaxis={'categoryorder': 'category ascending'})
    fig.write_image(f'static/{state_nm}1.png')

def get_bars_by_rating(sortby, chosen_date, orderby, limit):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    q = f'''
        SELECT RegionName, {sortby} FROM Counts
        JOIN Regions
        ON Regions.Id = Counts.RegionId
        WHERE Date = '{chosen_date}'
        ORDER BY {sortby} {orderby}
        LIMIT {limit}
        '''
    results = cur.execute(q).fetchall()
    conn.close()
    return results

def percent_rate(results):
    '''0.01 -> 1%'''
    r = []
    idx = -1
    print(len(results[0]))
    if len(results[0])>9:
        idx = 9
    for res in results:
        l = list(res)
        l[idx] = "{:.2%}".format(l[idx])
        r.append(tuple(l))
    return r

@app.route('/')
def index():
    total_cases, total_deaths = cache['today']
    m = today.strftime('%B') # 4 -> April
    d = today.day
    y = today.year
    state_dict = cache['state']
    return render_template('index.html', month=m, year=y, day=d,
    cases=total_cases, deaths=total_deaths, states = state_dict)

@app.route('/results', methods=['POST'])
def results():
    sortby = request.form['sort']
    chosen_date = request.form['chosen_date']
    orderby = request.form['dir']
    limit = request.form['howmany']
    results = get_bars_by_rating(sortby=sortby, chosen_date=chosen_date, orderby=orderby, limit=limit)
    if sortby == "FatalityRate":
        results = percent_rate(results)
    return render_template('results.html', results = results)

@app.route('/state/<state_nm>')
def state(state_nm):
    data = get_history_data_by_state(state_nm)
    if data:
        plot(state_nm, data)
        data = percent_rate(data)
        return render_template('state.html', nm= state_nm, data= data)
    else:
        html = f'''<p> Sorry, No data found for state {state_nm}. Please try again. </p>'''
        return html

if __name__ == '__main__':
    plot_stacked_bar(cache)
    plot_pie_charts(cache)
    print('starting Flask app', app.name)
    app.run()