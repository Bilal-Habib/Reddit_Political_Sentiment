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
    replies = getSubredditReplies(scraped_comments)
    all_comments = scraped_comments + replies
    return all_comments


def getSubredditReplies(comments):
    reply_sort_type = "top"
    scraped_replies = []
    for comment in comments:
        comment.reply_sort = reply_sort_type
        if len(comment.replies) > 0:
            for reply in comment.replies:
                scraped_replies.append(reply)
    return scraped_replies


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


def flatten_list(elem):
    """ a better flat_list() function than pythons default implementation for this specific use case """
    if not elem:
        return []
    elif isinstance(elem, tuple):
        return [elem]
    elif isinstance(elem, list):
        combined = []
        for element in elem:
            flat = flatten_list(element)
            if flat:
                combined = combined + flat
        return combined
    else:
        print(type(elem))
        print(elem)


def get_comments(comments):
    """ Given a comment object (i.e CommentForest), outputs a list of all the comments in there excluding the
    MoreComment objects and replies """
    if comments is None:
        return []
    elif isinstance(comments, praw.models.reddit.more.MoreComments):
        return []
    elif isinstance(comments, praw.models.reddit.comment.Comment):
        author = None
        return [(comments.body, author)]
    elif isinstance(comments, praw.models.comment_forest.CommentForest):
        combined = []
        for comment in (comments.list()):
            combined = combined + get_comments(comment)
        return combined
    elif isinstance(comments, list):
        return []
    else:
        print(type(comments))
        print(comments)


def get_submission_from_subreddit(reddit, subreddit_name, num_posts=1, sort_order="top"):
    """ Returns a list of submission objects found on the specified subreddit """
    submissions = reddit.subreddit(subreddit_name)
    if sort_order == "top":
        return submissions.top(limit=num_posts)
    elif sort_order == "hot":
        return submissions.hot(limit=num_posts)
    else:
        return submissions.new(limit=num_posts)


def get_all_comments_from_subreddit(subreddit_name, num_posts, sort_order="top"):
    """ Given a subreddit name, will fetch all comments from there """
    # get a new instance of an api connection to reddit using the PRAW api
    comments_acc = set()
    for submission in get_submission_from_subreddit(reddit, subreddit_name, num_posts, sort_order):
        # get comments and also get nested replies if that option was selected on the frontend
        comments_acc.update(flatten_list(get_comments(submission.comments)))
    return list(comments_acc)


if __name__ == '__main__':
    import pickle

    uk_left = get_all_comments_from_subreddit('labouruk', 200)
    usa_left = get_all_comments_from_subreddit('democrats', 200)
    canada_left = get_all_comments_from_subreddit('ndp', 200)
    all_left = uk_left + usa_left + canada_left

    uk_right = get_all_comments_from_subreddit('tories', 200)
    usa_right = get_all_comments_from_subreddit('Republican', 200)
    canada_right = get_all_comments_from_subreddit('CanadianConservative', 200)
    all_right = uk_right + usa_right + canada_right

    print(len(all_left), len(all_right))

    leftfile = open("three_left.txt", "wb")
    pickle.dump(all_left, leftfile)
    leftfile.close()

    rightfile = open("three_right.txt", "wb")
    pickle.dump(all_right, rightfile)
    rightfile.close()

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