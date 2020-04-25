# covid19Tracker

## Play with a command line tool.

Test if you correctly installed webdrive
```
python chrome_driver_test.py
```

Type in a state's name(i.e. Michigan), get the most updated covid19 info from CDC website.
Make sure dependent libraries are installed.
```
python crawlCDC.py
```

## Create/update a database 'UScovid19.sqlite' via JHU API. 

```
python JHU_API.py
```

## Visualization
Run Flask app. Click on state for details. Plotly-oraca library is required.

```
python app.py
```

![alt text](https://github.com/chyuting/covid19Tracker/blob/master/static/acc_new.png "Nationwide")
![alt text](https://github.com/chyuting/covid19Tracker/blob/master/static/state.png "States distribution")
![alt text](https://github.com/chyuting/covid19Tracker/blob/master/static/age.png "Age distribution")
![alt text](https://github.com/chyuting/covid19Tracker/blob/master/static/race.png "Race distribution")
![alt text](https://github.com/chyuting/covid19Tracker/blob/master/static/demo_all.png "Demo 1")
![alt text](https://github.com/chyuting/covid19Tracker/blob/master/static/demo_michigan.png "Demo 1")



