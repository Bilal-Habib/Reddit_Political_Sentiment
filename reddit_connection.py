import praw
import numpy as np

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


def getSubredditPosts(page_name, no_posts, post_sort_type):
    subreddit = reddit.subreddit(page_name)
    if post_sort_type == "new":
        return subreddit.new(limit=no_posts)
    elif post_sort_type == "hot":
        return subreddit.hot(limit=no_posts)
    elif post_sort_type == "top":
        return subreddit.top(limit=no_posts)


# scrape comments based on post and comment sort type
# def getComments(page_name, no_posts, post_sort_type):
#     comment_sort_type = "top"
#     no_posts = int(no_posts)
#     scraped_comments = np.empty([1, 0])
#     for post in getPosts(page_name, no_posts, post_sort_type):
#         post.comments.replace_more(limit=0)
#         post.comment_sort = comment_sort_type
#         scraped_comments = np.append(scraped_comments, post.comments)
#     return scraped_comments


# scrape replies/nested comments based on reply sort type
# def getReplies(comments):
#     reply_sort_type = "top"
#     scraped_replies = np.empty([1, 0])
#     for comment in comments.tolist():
#         comment.reply_sort = reply_sort_type
#         if len(comment.replies) > 0:
#             for reply in comment.replies:
#                 scraped_replies = np.append(scraped_replies, reply)
#     return scraped_replies


def getSubredditComments(page_name, no_posts, post_sort_type):
    comment_sort_type = "top"
    no_posts = int(no_posts)
    scraped_comments = []
    for post in getSubredditPosts(page_name, no_posts, post_sort_type):
        post.comments.replace_more(limit=0)
        post.comment_sort = comment_sort_type
        scraped_comments += post.comments
    return scraped_comments


# def getSubredditReplies(comments):
#     reply_sort_type = "top"
#     scraped_replies = []
#     for comment in comments:
#         comment.reply_sort = reply_sort_type
#         if len(comment.replies) > 0:
#             for reply in comment.replies:
#                 scraped_replies.append(reply)
#     return scraped_replies


def getUserComments(reddit_username, no_comments, comment_sort_type):
    scraped_comments = []
    if comment_sort_type == "new":
        for comment in reddit.redditor(reddit_username).comments.new(limit=no_comments):
            scraped_comments.append(comment)
    elif comment_sort_type == "hot":
        for comment in reddit.redditor(reddit_username).comments.hot(limit=no_comments):
            scraped_comments.append(comment)
    elif comment_sort_type == "top":
        for comment in reddit.redditor(reddit_username).comments.top(limit=no_comments):
            scraped_comments.append(comment)
    return scraped_comments
