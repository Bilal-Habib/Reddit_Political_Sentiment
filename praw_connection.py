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
    user_agent="my user agent",
    username=username,
    password=password
)

subreddit = reddit.subreddit("learnpython")
no_posts = 1
post_sort_type = "top"
comment_sort_type = "top"
reply_sort_type = "top"
scraped_comments = []
scraped_replies = []

# scrape comments based on post and comment sort type
if post_sort_type == "new":
    for post in subreddit.new(limit=no_posts):
        post.comment_sort = comment_sort_type
        scraped_comments = list(post.comments)
elif post_sort_type == "hot":
    for post in subreddit.post_sort_type(limit=no_posts):
        post.comment_sort = comment_sort_type
        scraped_comments = list(post.comments)
elif post_sort_type == "top":
    for post in subreddit.top(limit=no_posts):
        post.comment_sort = comment_sort_type
        scraped_comments = list(post.comments)

# scrape replies/nested comments based on reply sort type
for comment in scraped_comments:
    comment.reply_sort = reply_sort_type
    if len(comment.replies) > 0:
        for reply in comment.replies:
            scraped_replies = reply.body

print(scraped_comments)