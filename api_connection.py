import requests
from requests.auth import HTTPBasicAuth
import pandas as pd

# open config file
text_file = open("api_config", "r")

# read whole file to a string
data = text_file.read().split("\n")
CLIENT_ID = data[0]
SECRET_KEY = data[1]
username = data[2]
password = data[3]

# close file
text_file.close()

# note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
auth = HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

# here we pass our login method (password), username, and password
data = {'grant_type': 'password',
        'username': username,
        'password': password}

# setup our header info, which gives reddit a brief description of our app
headers = {'User-Agent': 'api/0.0.1'}

# send our request for an OAuth token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

# convert response to JSON and pull access_token value
TOKEN = res.json()['access_token']

# add authorization to our headers dictionary
headers['Authorization'] = f'bearer {TOKEN}'

# while the token is valid (~2 hours) we just add headers=headers to our requests
requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

# make a request for the trending posts in /r/Python
res = requests.get("https://oauth.reddit.com/r/python/top",
                   headers=headers)

df = pd.DataFrame()  # initialize dataframe

# loop through each post retrieved from GET request
for post in res.json()['data']['children']:
    # append relevant data to dataframe
    df = df.append({
        'subreddit': post['data']['subreddit'],
        'title': post['data']['title'],
        'selftext': post['data']['selftext'],
        'score': post['data']['score']
    }, ignore_index=True)

