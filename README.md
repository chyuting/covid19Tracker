# covid19Tracker
## Start
Install all required libraries.
```
pip install -r requirements.txt
```

Test if you correctly installed webdrive.
```
python chrome_driver_test.py
```

## Play with a command line tool.
Type in a state's name(i.e. Michigan) or a race name(i.e. Asian) or a age(i.e. 20), get the most updated covid19 info from CDC website.
```
python crawlCDC.py
```

## Create/update a database 'UScovid19.sqlite' via JHU API. 

```
python JHU_API.py
```

## Visualization
Run Flask app localhost. Plotly-oraca library is required to update static images.

```
python app.py
```

## Deployment
Create a remote heroku project with random name.
```
heroku create
```
Set heroku timezone to America.
```
 heroku config:add TZ="America/Argentina/Buenos_Aires"
```
Push app to github and heroku.
```
git push heroku master
```
Open heroku web.
```
heroku ps:scale web=1
heroku open
```
Take a look at heroku log file to debug.
```
heroku logs --tail
```
