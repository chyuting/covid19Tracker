############################################
# Based on public data by Johns Hopkins CSSE
# Author: Yuting Chen
# Uniquename: chyuting
############################################

import secrets
import requests
key = secrets.jhuapi_key


# # total, show the summary
# url = "https://covid-19-statistics.p.rapidapi.com/reports/total"

# querystring = {"date":"2020-04-07"}

# headers = {
#     'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
#     'x-rapidapi-key': key
#     }

# response = requests.request("GET", url, headers=headers, params=querystring)
# print(response.text)

# # regions, show countries iso
# url = "https://covid-19-statistics.p.rapidapi.com/regions"
# headers = {
#     'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
#     'x-rapidapi-key':  key
#     }

# response = requests.request("GET", url, headers=headers)

# print(response.text)

# # provinces information by iso
# # 'province', 'lat', 'long'
# url = "https://covid-19-statistics.p.rapidapi.com/provinces"

# querystring = {"iso":"USA"}

# headers = {
#     'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
#     'x-rapidapi-key': key
#     }

# response = requests.request("GET", url, headers=headers, params=querystring)

# print(response.text)

# reports by province
url = "https://covid-19-statistics.p.rapidapi.com/reports"

querystring = {"region_province":"Michigan","iso":"USA","region_name":"US","date":"2020-04-14","q":"US Michigan"}

headers = {
    'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
    'x-rapidapi-key': key
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)