import praw
from prawcore import NotFound
import helper


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

# create Praw Reddit instance
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=SECRET_KEY,
    user_agent="my user agent",
    username=username,
    password=password
)


# function to fetch posts from subreddit
def getSubredditPosts(page_name, no_posts, post_sort_type):
    subreddit = reddit.subreddit(page_name)
    if post_sort_type == 'new':
        return subreddit.new(limit=no_posts)
    elif post_sort_type == 'hot':
        return subreddit.hot(limit=no_posts)
    elif post_sort_type == 'top':
        return subreddit.top(limit=no_posts)


# gets comments and replies from posts from specified subreddit
def getSubredditComments(page_name, no_posts, post_sort_type):
    comment_sort_type = 'top'
    no_posts = int(no_posts)
    scraped_comments = []
    # loop through posts
    for post in getSubredditPosts(page_name, no_posts, post_sort_type):
        # gets a flat list of comments, removing MoreComments instance
        post.comments.replace_more(limit=0)
        # set sort type
        post.comment_sort = comment_sort_type
        # add comments to list
        scraped_comments += post.comments
    replies = getSubredditReplies(scraped_comments)
    all_comments = scraped_comments + replies
    # returns comments and replies
    return all_comments


# gets replies from comments
def getSubredditReplies(comments):
    reply_sort_type = 'top'
    scraped_replies = []
    for comment in comments:
        # set sort type
        comment.reply_sort = reply_sort_type
        # check if comment has replies
        if len(comment.replies) > 0:
            for reply in comment.replies:
                scraped_replies.append(reply)
    return scraped_replies


# gets comments made by a user
def getUserComments(is_encrypted, reddit_username, no_comments, comment_sort_type):
    if is_encrypted == 'yes':
        # decrypt username if encrypted
        reddit_username = helper.decryptName(reddit_username)
    scraped_comments = []
    # get comments based on sort type
    if comment_sort_type == 'new':
        for comment in reddit.redditor(reddit_username).comments.new(limit=no_comments):
            scraped_comments.append(comment)
    elif comment_sort_type == 'hot':
        for comment in reddit.redditor(reddit_username).comments.hot(limit=no_comments):
            scraped_comments.append(comment)
    elif comment_sort_type == 'top':
        for comment in reddit.redditor(reddit_username).comments.top(limit=no_comments):
            scraped_comments.append(comment)
    return scraped_comments


# checks if subreddit exists
def subExists(sub):
    exists = True
    try:
        if len(sub) < 3 or len(sub) > 20:
            exists = False
        else:
            user = reddit.subreddits.search_by_name(sub, exact=True)
            if not user:
                exists = False
    except NotFound:
        exists = False
    return exists


# checks if user exists
def userExists(user):
    exists = True
    try:
        reddit.redditor(user).id
    except NotFound:
        exists = False
    return exists
