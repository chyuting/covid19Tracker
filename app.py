######################
# Flask app
# Author: Yuting Chen
# Uniquename: chyuting
######################

from flask import Flask, render_template, request
from gevent.pywsgi import WSGIServer
import plotly
import plotly.graph_objs as go
import os
import random
import requests
import datetime
import sqlite3
import crawlCDC
import JHU_API

app = Flask(__name__)
today = crawlCDC.today
cache = crawlCDC.open_cache()
if cache == {}:
    crawlCDC.update()
    cache = crawlCDC.open_cache()

DB_NAME = JHU_API.DB_NAME # built database is required
region_list = JHU_API.read_regions()

def get_history_data_by_state(state_nm):
    '''Read a state's detail data from database'''
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
    '''a date str -> a date obj'''
    y,m,d = str.split('-')
    return datetime.date(year=int(y), month=int(m), day=int(d))

def _sqldate(str):
    ''' 2020-4-24 -> 2020-04-24 '''
    y,m,d = str.split('-')
    if len(m)<2:
        m = '0'+m
    return '-'.join([y,m,d])

def plot_stacked_bar(cache):
    ''' Plot stacked bar figure'''
    tend = cache['date']
    x_vals = [_todate(key) for key in tend.keys()] # label (date obj)
    y1_vals = [tend[key][0]-tend[key][1] for key in tend.keys()]
    y2_vals = [tend[key][1] for key in tend.keys()]
    y3_vals = []

    dates = [_sqldate(key) for key in tend.keys()] # dates to search in db
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    q = '''
        SELECT Recovered FROM Counts
        WHERE RegionId = 137
        AND Date = ?
    '''
    for d in dates:
        result = cur.execute(q, [d]).fetchone()
        if result:
            y3_vals.append(-int(result[0])) # negative value
        else:
            y3_vals.append(0)
    conn.close()

    stacked_fig = go.Figure(
        data=[
            go.Bar(name='New cases', x=x_vals, y=y2_vals),
            go.Bar(name='Accumulated cases', x=x_vals, y=y1_vals),
            go.Bar(name='Accumulated recovered', x=x_vals, y=y3_vals)
        ]
    )
    stacked_fig.update_layout(barmode='relative',  xaxis={'categoryorder': 'category ascending'},
    legend=dict(x=-.1, y=1.2),
    title={
        'text': "Covid19 in the U.S.",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
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
    pie_fig.update_layout(legend_title='<b> States </b>',
        legend=dict(x=-.1, y=1.2),
        uniformtext_minsize=10, uniformtext_mode='hide',
        title={
        'text': "Distribution by state",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    pie_fig.write_image('static/states.png')

    # distribution by age
    age = cache['age']
    labels = [key for key in age.keys() if key != 'Total']
    values = [age[key] for key in labels]
    pie_fig = go.Figure(
        data=[go.Pie(labels=labels, values=values)]
    )
    pie_fig.update_traces(textposition='inside')
    pie_fig.update_layout(legend_title='<b> Age </b>',
        legend=dict(x=-.1, y=1.2),
        uniformtext_minsize=10, uniformtext_mode='hide', 
        title={
        'text': "Distribution by age",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    pie_fig.write_image('static/age.png')

    # distribution by race
    race = cache['race']
    labels = [k.split('or')[0] for k in race.keys()]
    values = list(race.values())
    pie_fig = go.Figure(
        data=[go.Pie(labels=labels, values=values)]
    )
    pie_fig.update_traces(textposition='inside')
    pie_fig.update_layout(legend_title='<b> Race </b>',
        legend=dict(x=-.1, y=1.2),
        uniformtext_minsize=10, uniformtext_mode='hide', 
        title={
        'text': "Distribution by race",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    pie_fig.write_image('static/race.png')

def plot(state_nm, data):
    '''plot total cases and deaths of a state'''
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
    fig.update_layout(xaxis={'categoryorder': 'category ascending'},
        title={
        'text': f"Trend in {state_nm}",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig.write_image(f'static/{state_nm}1.png')

def get_bars_by_rating(sortby, chosen_date, orderby, limit):
    '''Read data with filters from database'''
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
    if not os.path.exists('static/acc_new.png'): # deploy
        plot_stacked_bar(cache)
    if not os.path.exists('static/states.png'):
        plot_pie_charts(cache)
    print('starting Flask app', app.name)
    # Debug/Develpment
    # app.run(debug=True)

    # Production
    http_server = WSGIServer(('', 5000),app)
    http_server.serve_forever()