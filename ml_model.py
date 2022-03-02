import keras.losses
from tensorflow import keras
import reddit_connection as rc
import re as regex
import toolz
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Embedding, GlobalAveragePooling1D, LSTM, Dropout
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from collections import Counter
from random import shuffle
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.naive_bayes import GaussianNB
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import confusion_matrix
import pickle
import rsa
import app
import ast


def encryptName(username):
    cipher_text = str(rsa.encrypt(username.encode(), app.public_key))
    return cipher_text


def decryptName(username):
    decoded = ast.literal_eval(username)
    plain_text = rsa.decrypt(decoded, app.private_key).decode()
    return plain_text


def generateTrainingData(no_left_posts, no_right_posts):
    left_wing_comments = []
    right_wing_comments = []

    # gather left-wing data
    # uk left-wing party
    comments = rc.getSubredditComments('LabourUK', no_left_posts, 'top')
    for comment in comments:
        left_wing_comments.append(comment.body)
    # usa left-wing party
    # comments = rc.getSubredditComments('democrats', no_left_posts, 'top')
    # for comment in comments:
    #     left_wing_comments.append(comment.body)

    # gather right-wing data
    # uk right-wing party
    comments = rc.getSubredditComments('tories', no_right_posts, 'top')
    for comment in comments:
        right_wing_comments.append(comment.body)
    # usa right-wing party
    # comments = rc.getSubredditComments('Republican', no_right_posts, 'top')
    # for comment in comments:
    #     right_wing_comments.append(comment.body)

    return [left_wing_comments, right_wing_comments]


# preprocess data
# stop words from NLTK
stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
              "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
              'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
              'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
              'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
              'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
              'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
              'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
              'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
              'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
              'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
              'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
              'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've",
              'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
              "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
              'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
              'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren',
              "weren't", 'won', "won't", 'wouldn', "wouldn't"]


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


# filter text
def filterComment(comment):
    # Take care of non-ascii characters
    comment = (comment.encode('ascii', 'replace')).decode("utf-8")

    # Convert text to Lower case
    comment = comment.lower()

    # filter comment by removing links
    # url = regex.compile(r"https?//\S+|www\.\S+")
    # removed_url = url.sub(r"", comment)
    removed_url = regex.sub(r"https?//\S+|www\.\S+", '', comment)

    # Remove multiple spacing
    space = regex.sub(r"\s+", " ", removed_url, flags=regex.I)

    # Remove special characters
    clean_text = regex.sub(r'[!"#$%&()*+,-./:;?@[\]^_`{|}~]', ' ', space)
    space1 = regex.sub(r"\s+", " ", clean_text, flags=regex.I)

    comment_without_noise = [word for word in space1.split() if word not in stop_words]
    filtered_comment = ' '.join(comment_without_noise)
    return filtered_comment


# def filterComment(data):
#     # Removing URLs with a regular expression
#     url_pattern = regex.compile(r'https?://\S+|www\.\S+')
#     data = url_pattern.sub(r'', data)
#
#     # Remove Emails
#     data = regex.sub('\S*@\S*\s?', '', data)
#
#     # Remove new line characters
#     data = regex.sub('\s+', ' ', data)
#
#     # Remove distracting single quotes
#     data = regex.sub("\'", "", data)
#
#     return data


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


# function that retrieves the comments and labels separately
def getCommentsLabels(labelled_left, labelled_right):
    comments = []
    labels = []

    # use interleave function to combine comments & labels in alternating fashion
    # avoids bias in learning stage
    # combined_comments = toolz.interleave([labelled_left, labelled_right])

    combined_comments = labelled_left + labelled_right
    shuffle(combined_comments)

    # separate comments and labels
    for comment in combined_comments:
        comments.append(comment[0])
        labels.append(comment[1])

    return [comments, labels]


# counts number of times words appear
def wordCounter(comments):
    count = Counter()
    for comment in comments:
        for word in comment.split():
            count[word] += 1
    return count


def finalPreprocessing(left_wing, right_wing):
    # filter comments
    filtered_left, filtered_right = filterAllComments(left_wing), filterAllComments(right_wing)

    # label comments
    labelled_comments = labelComments(filtered_left, filtered_right)
    labelled_left, labelled_right = labelled_comments[0], labelled_comments[1]

    # set comments and labels
    comments_labels = getCommentsLabels(labelled_left, labelled_right)
    comments, labels = comments_labels[0], comments_labels[1]

    # split both into training/testing (start with 70/30)
    n_comments = len(comments)
    train_size = int(0.80 * n_comments)
    training_comments, testing_comments = comments[:train_size], comments[train_size:]
    training_labels, testing_labels = labels[:train_size], labels[train_size:]
    print('INITIAL TRAIN SIZE: ', train_size)

    # ----------------------------------------------
    # he said forget about testing part, split training data into 80:20 again
    # n_comments = len(training_comments)
    # train_size = int(0.80 * n_comments)
    # print('SECOND TRAIN SIZE: ', train_size)
    # training_comments2, val_comments = training_comments[:train_size], training_comments[train_size:]
    # training_labels2, val_labels = training_labels[:train_size], training_labels[train_size:]
    # use val labels
    # ----------------------------------------------

    # dictionary of words and their counter
    # counter = wordCounter(comments)
    counter = wordCounter(training_comments)

    # number of unique words
    num_unique_words = len(counter)

    # vectorise text corpus by turning each comment into a sequence of integers
    # tokenizer = Tokenizer(num_words=num_unique_words)
    tokenizer = Tokenizer(num_words=num_unique_words, oov_token='<OOV>')
    tokenizer.fit_on_texts(training_comments)
    # tokenizer.fit_on_texts(training_comments2)
    # word_index = tokenizer.word_index

    # he said change testing comments to val comments
    train_sequences = tokenizer.texts_to_sequences(training_comments)
    val_sequences = tokenizer.texts_to_sequences(testing_comments)
    # train_sequences = tokenizer.texts_to_sequences(training_comments2)
    # val_sequences = tokenizer.texts_to_sequences(val_comments)

    # we want every sequence to have same length so we'll use padding
    max_length = 500
    training_padded = pad_sequences(train_sequences, maxlen=max_length, padding="post", truncating="post")
    val_padded = pad_sequences(val_sequences, maxlen=max_length, padding="post", truncating="post")

    print("padded shape: ", training_padded.shape, val_padded.shape)
    # save tokenizer code
    # with open('tokenizer3', 'wb') as file:
    #     pickle.dump(tokenizer, file)
    return [num_unique_words, training_padded, training_labels, val_padded, testing_labels]


# format data appropriately and generate ml model
def createModel(left_wing, right_wing):
    values = finalPreprocessing(left_wing, right_wing)
    num_unique_words = values[0]
    training_padded = values[1]
    training_labels = values[2]
    val_padded = values[3]
    testing_labels = values[4]
    max_length = 500
    # create keras model
    model = Sequential()
    model.add(Embedding(num_unique_words, 32, input_length=max_length))
    model.add(GlobalAveragePooling1D())
    # model.add(LSTM(32, activation='relu'))
    model.add(Dense(32, activation="relu"))
    # model.add(Dropout(0.40))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()
    model.fit(np.asarray(training_padded), np.asarray(training_labels), epochs=20,
              validation_data=(np.asarray(val_padded), np.asarray(testing_labels)), verbose=2)

    # code to save model and tokenizer
    # model.save('model3')


# def naiveModel(left_wing, right_wing):
# model = GaussianNB()
# model.fit(training_padded, training_labels)
# score = model.score(val_padded, testing_labels)
# print("Guassian Accuracy: ", score)
# model2 = MultinomialNB()
# model2.fit(training_padded, training_labels)
# score = model2.score(val_padded, testing_labels)
# print("Multinomial Accuracy: ", score)


# function that returns a list of data to be shown on website table
def predictComments(page_type, comments):
    left_wing_dataset = []
    right_wing_dataset = []
    max_length = 500
    # load model
    model = keras.models.load_model('model3')
    # load tokenizer
    with open('tokenizer3', 'rb') as file:
        tokenizer = pickle.load(file)
    # dataset stores all author, comment, sentiment value
    # dataset = []
    for comment in comments:
        # only calculate sentiment value for comments where author exists and where comment is not empty
        if comment.author:
            author_name = comment.author.name
            comment_text = comment.body
            # filter comment
            filtered_text = filterComment(comment_text)
            if filtered_text != '':
                # use tokenizer to tokenize comments
                test_sequences = tokenizer.texts_to_sequences(filtered_text)
                # pad comments
                padded_comments = pad_sequences(test_sequences, maxlen=max_length, padding="post")
                # store and calculate sentiment value
                sentiment_val = model.predict(padded_comments).tolist()[0][0]
                # make sentiment value readable
                readable_sentiment = getReadableSentiment(sentiment_val)
                # if user chooses subreddit, we need to add author name
                if page_type == 'subredditPage':
                    author_name = encryptName(author_name)
                    if sentiment_val > 0.5:
                        right_wing_dataset.append([readable_sentiment, comment_text, author_name])
                    else:
                        left_wing_dataset.append([readable_sentiment, comment_text, author_name])
                # if user chooses username, we don't need the author name
                elif page_type == 'usernamePage':
                    if sentiment_val > 0.5:
                        right_wing_dataset.append([readable_sentiment, comment_text])
                    else:
                        left_wing_dataset.append([readable_sentiment, comment_text])
    return left_wing_dataset, right_wing_dataset


# takes in sentiment value e.g 0.20
# converts 0.0 to '100% Left Wing'
def getReadableSentiment(value):
    threshold = 0.5
    unformatted_sentiment = (1 - value / threshold) * 100
    # left_wing = False
    # if value <= threshold:
    #     left_wing = True
    # round to 2 decimal places
    rounded_value = ("{:.0f}".format(abs(unformatted_sentiment)))
    readable_sentiment = str(rounded_value) + '%'
    # if left_wing:
    #     readable_sentiment = str(rounded_value) + '% Left Wing'
    # else:
    #     readable_sentiment = str(rounded_value) + '% Right Wing'
    return readable_sentiment


if __name__ == '__main__':
    pass
    # pubkey, privkey = rsa.newkeys(512)
    # print(pubkey)
    # print(privkey)
    # comments = generateTrainingData(100, 100)
    # comments = generateTrainingData(100, 100)
    # raw comments
    # left_wing = pickle.load(open("three_left.txt"))
    # right_wing = pickle.load(open("three_right.txt"))
    # left_wing, right_wing = comments[0], comments[1]
    # print('no of left wing comments: ', len(left_wing))
    # print('no of right wing comments: ', len(right_wing))
    # naiveModel(left_wing, right_wing)
    # createModel(left_wing, right_wing)
    # leftfile = open("left_wing.txt", "w")
    # for element in left_wing:
    #     leftfile.write(element + "\n")
    # leftfile.close()
    #
    # rightfile = open("right_wing.txt", "w")
    # for element in right_wing:
    #     rightfile.write(element + "\n")
    # rightfile.close()

    # code to read from file
    # left_wing = []
    # right_wing = []
    #



    # with open('three_left.txt') as f:
    #     left_wing = [line.rstrip('\n') for line in f]
    #
    # with open('three_right.txt') as f:
    #     right_wing = [line.rstrip('\n') for line in f]
    #
    # print('no of left wing comments: ', len(left_wing))
    # print('no of right wing comments: ', len(right_wing))
    # # createModel(left_wing, right_wing)
    #
    # filter_left = filterAllComments(left_wing)
    # filter_right = filterAllComments(right_wing)
    #
    # left_counter = wordCounter(filter_left)
    # right_counter = wordCounter(filter_right)
    # print(left_counter)
    # print(right_counter)
