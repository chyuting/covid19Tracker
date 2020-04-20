from flask import Flask, render_template, request
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

@app.route('/')
def index():
    total_cases, total_deaths = cache['today']
    m = today.strftime('%B') # 4 -> April
    d = today.day
    y = today.year
    state_dict = cache['state']
    return render_template('index.html', month=m, year=y, day=d, 
    cases=total_cases, deaths=total_deaths, states = state_dict)

def plot(state_nm, data):
    x_vals = [i[2] for i in data] # date
    y_vals = [i[3] for i in data] # total cases
    bars_data = go.Scatter(
        x=x_vals,
        y=y_vals,
        line = dict(width=4, dash='dash')
    )
    print('generating pictures')
    fig = go.Figure(data=bars_data)
    fig.write_image(f'static/{state_nm}.png')


@app.route('/state/<state_nm>')
def state(state_nm):
    data = get_history_data_by_state(state_nm)
    if data:
        plot(state_nm, data)
        return render_template('state.html', nm= state_nm, data= data)
    else:
        html = f'''<p> Sorry, No data found for state {state_nm}. Please try again. </p>'''
        return html

if __name__ == '__main__':
    print('starting Flask app', app.name)
    app.run(debug=True)