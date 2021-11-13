import praw

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

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=SECRET_KEY,
    user_agent='api:v0.0.1 (by u/TheSixthGates)',
    username=username,
    password=password,
)

for post in reddit.subreddit("learnpython").top(limit=10):
    print(post.title)
