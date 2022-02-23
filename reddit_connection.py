import praw
import numpy as np
import ml_model

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
    if post_sort_type == 'new':
        return subreddit.new(limit=no_posts)
    elif post_sort_type == 'hot':
        return subreddit.hot(limit=no_posts)
    elif post_sort_type == 'top':
        return subreddit.top(limit=no_posts)


# gets comments from posts from specified subreddit
def getSubredditComments(page_name, no_posts, post_sort_type):
    comment_sort_type = 'top'
    no_posts = int(no_posts)
    scraped_comments = []
    for post in getSubredditPosts(page_name, no_posts, post_sort_type):
        post.comments.replace_more(limit=0)
        post.comment_sort = comment_sort_type
        scraped_comments += post.comments
    replies = getSubredditReplies(scraped_comments)
    all_comments = scraped_comments + replies
    return all_comments


def getSubredditReplies(comments):
    reply_sort_type = 'top'
    scraped_replies = []
    for comment in comments:
        comment.reply_sort = reply_sort_type
        if len(comment.replies) > 0:
            for reply in comment.replies:
                scraped_replies.append(reply)
    return scraped_replies


# gets comments made by a user
def getUserComments(is_encrypted, reddit_username, no_comments, comment_sort_type):
    if is_encrypted == 'yes':
        reddit_username = ml_model.decryptName(reddit_username)
    scraped_comments = []
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


if __name__ == '__main__':
    pass
    # comments = getUserComments('Leelum', 5, 'top')
    # for comment in comments:
    #     print(comment.body)
    # comments = getSubredditComments('labouruk', 1, 'top')
    # for comment in comments:
    #     if comment.author:
    #         print(comment.author.name)
    # import pickle
    #
    # uk_left = get_all_comments_from_subreddit('labouruk', 200)
    # usa_left = get_all_comments_from_subreddit('democrats', 200)
    # canada_left = get_all_comments_from_subreddit('ndp', 200)
    # all_left = uk_left + usa_left + canada_left
    #
    # uk_right = get_all_comments_from_subreddit('tories', 200)
    # usa_right = get_all_comments_from_subreddit('Republican', 200)
    # canada_right = get_all_comments_from_subreddit('CanadianConservative', 200)
    # all_right = uk_right + usa_right + canada_right
    #
    # print(len(all_left), len(all_right))
    #
    # leftfile = open("three_left.txt", "wb")
    # pickle.dump(all_left, leftfile)
    # leftfile.close()
    #
    # rightfile = open("three_right.txt", "wb")
    # pickle.dump(all_right, rightfile)
    # rightfile.close()

    # left_wing = []
    # right_wing = []
    #
    # with open('three_left.txt') as f:
    #     left_wing = [line.rstrip('\n') for line in f]
    #
    # with open('three_right.txt') as f:
    #     right_wing = [line.rstrip('\n') for line in f]
    #
    # print(len(left_wing), len(right_wing))
