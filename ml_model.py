import reddit_connection as rc
import re as regex
import toolz


def generateTrainingData(no_left_posts, no_right_posts):
    left_wing_comments = []
    right_wing_comments = []

    # gather left-wing data
    # uk left-wing party
    comments = rc.getSubredditComments('LabourUK', no_left_posts, 'top')
    for comment in comments:
        left_wing_comments.append(comment.body)
    # usa left-wing party
    # comments = rc.getSubredditComments('democrats', 100, 'top')
    # for comment in comments:
    #     left_wing_comments.append(comment)

    # gather right-wing data
    # uk right-wing party
    comments = rc.getSubredditComments('tories', no_right_posts, 'top')
    for comment in comments:
        right_wing_comments.append(comment.body)
    # usa right-wing party
    # comments = rc.getSubredditComments('Republican', 100, 'top')
    # for comment in comments:
    #     right_wing_comments.append(comment)

    return [left_wing_comments, right_wing_comments]


# preprocess data
# stop words from NLTK
stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
              'you', "you're", "you've", "you'll", "you'd", 'your', 'yours',
              'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
              'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
              'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
              'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
              'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
              'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
              'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
              'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
              'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
              'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
              'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
              'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
              "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
              'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
              'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma',
              'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
              'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
              'wouldn', "wouldn't"]

# words that change meaning of sentiment: "you've", "you'll", "you'd", "that'll", "should've",
# couldn', "couldn't", didn', "didn't", 'doesn', "doesn't",
#               'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma',
#               'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
#               'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
#               'wouldn', "wouldn't"

# function that filters one comment
# def filterComment(comment):
#     # filter comment by removing links
#     removed_link = regex.sub(r'http\S+', '', comment)
#     # filter comment by removing special characters
#     removed_special = regex.sub('\W+', ' ', removed_link)
#     # remove noisy words from comment to increase accuracy
#     comment_without_noise = [word for word in removed_special if word.lower() not in stop_words]
#     filtered_comment = ' '.join(comment_without_noise)
#     return filtered_comment


# function from website
def filterComment(comment):
    # Take care of non-ascii characters
    comment = (comment.encode('ascii', 'replace')).decode("utf-8")

    # Convert text to Lower case
    comment = comment.lower()

    # filter comment by removing links
    removed_link = regex.sub(r'http\S+', '', comment)

    # Remove multiple spacing
    space = regex.sub(r"\s+", " ", removed_link, flags=regex.I)

    # Remove special characters
    clean_text = regex.sub(r'[!"#$%&()*+,-./:;?@[\]^_`{|}~]', ' ', space)
    space1 = regex.sub(r"\s+", " ", clean_text, flags=regex.I)

    comment_without_noise = [word for word in space1.split() if word not in stop_words]
    filtered_comment = ' '.join(comment_without_noise)
    return filtered_comment


# function that applies filter to every comment
def filterAllComments(all_comments):
    filtered_comments = []
    for comment in all_comments:
        # filter each comment
        filtered_comment = filterComment(comment)
        # add it to filtered list
        filtered_comments.append(filtered_comment)
    return filtered_comments


# function that labels the left and right comments
def labelComments(left_wing_comments, right_wing_comments):
    labelled_left = []
    labelled_right = []

    # format: [X, y] = [comment, label]

    # label left wing comments with 0
    for comment in left_wing_comments:
        labelled_left.append([comment, 0])

    # label right wing comment with 1
    for comment in right_wing_comments:
        labelled_right.append([comment, 1])

    return [labelled_left, labelled_right]


# function that combines the left and right comments
def getCommentsLabels(labelled_left, labelled_right):
    # combined_comments = labelled_left + labelled_right
    comments = []
    labels = []

    # use interleave function to combine comments & labels in alternating fashion
    combined_comments = toolz.interleave([labelled_left, labelled_right])

    for comment in combined_comments:
        comments.append(comment[0])
        labels.append(comment[1])

    return [comments, labels]


# create ml model
def createModel(left_wing, right_wing):
    # filter comments
    filtered_left = filterAllComments(left_wing)
    filtered_right = filterAllComments(right_wing)

    # label comments
    labelled_comments = labelComments(filtered_left, filtered_right)
    labelled_left = labelled_comments[0]
    labelled_right = labelled_comments[1]

    # set comments and labels
    comments_labels = getCommentsLabels(labelled_left, labelled_right)
    X = comments_labels[0]
    y = comments_labels[1]

    # split both into training/testing (start with 70/30)
    n_samples = len(comments)
    percentage_samples = int(0.7 * n_samples)
    X_train, X_test = X[:percentage_samples], X[percentage_samples:]
    y_train, y_test = y[:percentage_samples], y[percentage_samples:]

    # create ml model



# get accuracy by testing it on testing data


# X = comments text "I like boris"
# y = comments label "0"

if __name__ == '__main__':
    comments = generateTrainingData(1, 1)
    # raw comments
    left_wing = comments[0]
    right_wing = comments[1]
    # print("raw: ", left_wing, right_wing)

    # filtered comments
    filtered_left = filterAllComments(left_wing)
    filtered_right = filterAllComments(right_wing)
    # print("filtered: ", filtered_left, filtered_right)

    # labelled comments
    labelled_comments = labelComments(filtered_left, filtered_right)
    labelled_left = labelled_comments[0]
    labelled_right = labelled_comments[1]
    # print("labelled: ", labelled_left, labelled_right)

    # combine comments
    comments_labels = getCommentsLabels(labelled_left, labelled_right)
    comments = comments_labels[0]
    labels = comments_labels[1]
    print("comments: ", comments)
    # print("labels: ", labels)
    # print(labels.count(0), labels.count(1))
