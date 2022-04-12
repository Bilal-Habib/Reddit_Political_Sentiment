# local file imports
import helper
import reddit_connection as rc
# machine learning imports
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Embedding, GlobalAveragePooling1D, LSTM, Bidirectional
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
# data processing imports
import numpy as np
import matplotlib.pyplot as plt
import regex
import string
from collections import Counter
from random import seed, shuffle


# global variables
seed(10)
embedding_dim = 64
trunc_type = 'post'
padding_type = 'post'
oov_tok = "<OOV>"
left_wing_file = 'left_dataset'
right_wing_file = 'right_dataset'
tokenizer_file = 'tokenizer'
saved_model = 'model'

# stop words from NLTK
stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
              'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
              'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
              'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were',
              'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
              'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
              'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
              'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
              'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
              'some', 'such', 'no', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
              'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain',
              'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn',
              "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
              "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
              'wouldn', "wouldn't"}

to_del = ['no', 'nor', 'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn',
              "hasn't", 'haven', "haven't", 'isn', "isn't", 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
              "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
              'wouldn', "wouldn't"]

for elem in to_del:
    # Remove element from the set
    stop_words.discard(elem)


def generateDatasets(no_posts):
    labelled_left_dataset = []
    labelled_right_dataset = []

    # gather left-wing data
    uk_left = rc.getSubredditComments('LabourUK', no_posts, 'top')
    usa_left = rc.getSubredditComments('democrats', no_posts, 'top')
    can_left = rc.getSubredditComments('ndp', no_posts, 'top')
    left_comments = uk_left + usa_left + can_left
    for comment in left_comments:
        # extract body only from comment object
        # label left wing comments with 0
        labelled_left_dataset.append([comment.body, 0])

    # gather right-wing data
    uk_right = rc.getSubredditComments('tories', no_posts, 'top')
    usa_right = rc.getSubredditComments('Republican', no_posts, 'top')
    can_right = rc.getSubredditComments('CanadianConservative', no_posts, 'top')
    right_comments = uk_right + usa_right + can_right
    for comment in right_comments:
        # extract body only from comment object
        # label right wing comments with 1
        labelled_right_dataset.append([comment.body, 1])

    print('number of left comments:', len(labelled_left_dataset))
    print('number of right comments:', len(labelled_right_dataset))
    print('total comments generated:', len(labelled_left_dataset) + len(labelled_right_dataset))

    # store labelled comments in files
    helper.writeToFile(left_wing_file, labelled_left_dataset)
    helper.writeToFile(right_wing_file, labelled_right_dataset)


# preprocess data
def filterComment(comment):
    comment = comment.lower()

    pattern = regex.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    comment = pattern.sub('', comment)

    emoji = regex.compile("["
                          u"\U0001F600-\U0001FFFF"  # emoticons
                          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                          u"\U0001F680-\U0001F6FF"  # transport & map symbols
                          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                          u"\U00002702-\U000027B0"
                          u"\U000024C2-\U0001F251"
                          "]+", flags=regex.UNICODE)
    comment = emoji.sub(r'', comment)

    comment = regex.sub(r"i'm", "i am", comment)
    comment = regex.sub(r"he's", "he is", comment)
    comment = regex.sub(r"she's", "she is", comment)
    comment = regex.sub(r"that's", "that is", comment)
    comment = regex.sub(r"what's", "what is", comment)
    comment = regex.sub(r"where's", "where is", comment)
    comment = regex.sub(r"\'ll", " will", comment)
    comment = regex.sub(r"\'ve", " have", comment)
    comment = regex.sub(r"\'re", " are", comment)
    comment = regex.sub(r"\'d", " would", comment)
    comment = regex.sub(r"\'ve", " have", comment)
    comment = regex.sub(r"won't", "will not", comment)
    comment = regex.sub(r"don't", "do not", comment)
    comment = regex.sub(r"did't", "did not", comment)
    comment = regex.sub(r"can't", "can not", comment)
    comment = regex.sub(r"it's", "it is", comment)
    comment = regex.sub(r"couldn't", "could not", comment)
    comment = regex.sub(r"have't", "have not", comment)

    comment = regex.sub(r"[,.\"!@#$%^&*(){}?/;`~:<>+=-]", "", comment)
    tokens = comment.split()
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    # print('STOPWORDS LENGTH:', len(stop_words))
    words = [w for w in words if w not in stop_words]
    filtered_comment = ' '.join(words)
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


# function that retrieves the comments and labels separately
def getCommentsLabels(labelled_left, labelled_right):
    left_comments = []
    left_labels = []
    right_comments = []
    right_labels = []

    for comment in labelled_left:
        left_comments.append(comment[0])
        left_labels.append(comment[1])
    for comment in labelled_right:
        right_comments.append(comment[0])
        right_labels.append(comment[1])

    filtered_left = filterAllComments(left_comments)
    filtered_right = filterAllComments(right_comments)

    combined_comments = []
    for comment in filtered_left:
        combined_comments.append([comment, 0])
    for comment in filtered_right:
        combined_comments.append([comment, 1])

    # filter combined comments
    filtered_combined = [row for row in combined_comments if row[0] != '']
    print('length of filtered combined:', len(filtered_combined))

    shuffle(filtered_combined)

    comments = []
    labels = []
    # separate comments and labels
    for comment in filtered_combined:
        comments.append(comment[0])
        labels.append(comment[1])

    return comments, labels


# counts number of times words appear
def wordCounter(comments):
    count = Counter()
    for comment in comments:
        for word in comment.split():
            count[word] += 1
    return count


def finalPreprocessing(left_wing, right_wing):
    # set comments and labels
    comments, labels = getCommentsLabels(left_wing, right_wing)

    # filter comments
    comments = filterAllComments(comments)

    # train test split
    n_comments = len(comments)
    train_size = int(0.70 * n_comments)
    training_comments, testing_comments = comments[:train_size], comments[train_size:]
    training_labels, testing_labels = labels[:train_size], labels[train_size:]

    # dictionary of words and their counter
    counter = wordCounter(training_comments)

    # number of unique words
    num_unique_words = len(counter) + 2

    # vectorise text corpus by turning each comment into a sequence of integers
    tokenizer = Tokenizer(oov_token=oov_tok)
    tokenizer.fit_on_texts(training_comments)

    train_sequences = tokenizer.texts_to_sequences(training_comments)
    val_sequences = tokenizer.texts_to_sequences(testing_comments)

    max_length = max([len(x) for x in train_sequences])

    # we want every sequence to have same length so we'll use padding
    training_padded = pad_sequences(train_sequences, maxlen=max_length,
                                    padding=padding_type, truncating=trunc_type)
    val_padded = pad_sequences(val_sequences, maxlen=max_length,
                               padding=padding_type, truncating=trunc_type)

    # convert data np arrays for tensorflow v2.x
    training_padded = np.asarray(training_padded)
    training_labels = np.asarray(training_labels)
    val_padded = np.asarray(val_padded)
    testing_labels = np.asarray(testing_labels)

    return [num_unique_words, training_padded, training_labels,
            val_padded, testing_labels, max_length]
def finalPreprocessing(left_wing, right_wing):
    # set comments and labels
    comments, labels = getCommentsLabels(left_wing, right_wing)

    # filter comments
    comments = filterAllComments(comments)

    # split both into training/testing (start with 80/20)
    n_comments = len(comments)
    train_size = int(0.70 * n_comments)
    val_size = n_comments - train_size
    training_comments, testing_comments = comments[:train_size], comments[train_size:]
    training_labels, testing_labels = labels[:train_size], labels[train_size:]
    print('TRAIN DATASET SIZE:', train_size)
    print('VALIDATION DATASET SIZE:', val_size)

    # dictionary of words and their counter
    counter = wordCounter(training_comments)

    # number of unique words
    num_unique_words = len(counter) + 2
    print('num_unique_words:', num_unique_words)

    # vectorise text corpus by turning each comment into a sequence of integers
    tokenizer = Tokenizer(oov_token=oov_tok)
    tokenizer.fit_on_texts(training_comments)

    num_unique_words = len(tokenizer.word_index) + 1
    print('num_unique_words:', num_unique_words)

    train_sequences = tokenizer.texts_to_sequences(training_comments)
    val_sequences = tokenizer.texts_to_sequences(testing_comments)

    max_length = max([len(x) for x in train_sequences])
    print('MAX LENGTH:', max_length)

    # we want every sequence to have same length so we'll use padding
    training_padded = pad_sequences(train_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)
    val_padded = pad_sequences(val_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)

    # convert data np arrays for tensorflow v2.x
    training_padded = np.asarray(training_padded)
    training_labels = np.asarray(training_labels)
    val_padded = np.asarray(val_padded)
    testing_labels = np.asarray(testing_labels)

    print("padded shape: ", training_padded.shape, val_padded.shape)

    return [num_unique_words, training_padded, training_labels, val_padded, testing_labels, max_length]

# format data appropriately and generate ml model
def createModel(left_wing, right_wing):
    values = finalPreprocessing(left_wing, right_wing)
    num_unique_words = values[0]
    training_padded = values[1]
    training_labels = values[2]
    val_padded = values[3]
    testing_labels = values[4]
    max_length = values[5]

    # create keras model
    model = Sequential()
    model.add(Embedding(num_unique_words, embedding_dim, input_length=max_length))
    model.add(GlobalAveragePooling1D())
    model.add(Dense(32, activation="relu"))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()
    train_model = model.fit(training_padded, training_labels, epochs=20,
                            validation_data=(val_padded, testing_labels), verbose=2)
    plotGraph(train_model, "accuracy")
    plotGraph(train_model, "loss")
    # code to save model
    # model.save('model')


def plotGraph(history, attr):
    plt.plot(history.history[attr])
    plt.plot(history.history['val_' + attr])
    plt.xlabel("Epochs")
    plt.ylabel(attr)
    plt.legend([attr, 'val_' + attr])
    plt.show()


# function that returns a list of data to be shown on website table
def predictComments(page_type, comments):
    left_wing_dataset = []
    right_wing_dataset = []
    # load model
    model = keras.models.load_model(saved_model)
    # load tokenizer
    tokenizer = helper.readFromFile(tokenizer_file)

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

                max_length = max([len(x) for x in test_sequences])
                print('MAX TEST LENGTH:', max_length)

                # pad comments
                padded_comments = pad_sequences(test_sequences,
                                                maxlen=max_length, padding=padding_type, truncating=trunc_type)
                # store and calculate sentiment value
                sentiment_val = model.predict(padded_comments).tolist()[0][0]
                # if user chooses subreddit, we need to add author name
                if page_type == 'r/':
                    author_name = helper.encryptName(author_name)
                    if sentiment_val > 0.5:
                        right_wing_dataset.append([sentiment_val, comment_text, author_name])
                    else:
                        left_wing_dataset.append([sentiment_val, comment_text, author_name])
                # if user chooses username, we don't need the author name
                elif page_type == 'u/':
                    if sentiment_val > 0.5:
                        right_wing_dataset.append([sentiment_val, comment_text])
                    else:
                        left_wing_dataset.append([sentiment_val, comment_text])
    return left_wing_dataset, right_wing_dataset


def getWordsIntersection(left_comments, right_comments):
    left_wing = []
    right_wing = []

    # extract comments only (we don't want labels)
    for comment in left_comments:
        left_wing.append(comment[0])
    for comment in right_comments:
        right_wing.append(comment[0])

    # filter comments
    filter_left = filterAllComments(left_wing)
    filter_right = filterAllComments(right_wing)

    # get n most common words from comments
    left_counter = wordCounter(filter_left).most_common(20)
    right_counter = wordCounter(filter_right).most_common(20)

    # extract words only (we don't want the counter of the words)
    first_left = [a_tuple[0] for a_tuple in left_counter]
    first_right = [a_tuple[0] for a_tuple in right_counter]

    # store the intersection of the most common words from the 2 lists
    intersection = list(set(first_left).intersection(first_right))

    print(left_counter)
    print(right_counter)
    print(intersection)

    return intersection


if __name__ == '__main__':
    # generate data
    # generateDatasets(400)

    # get left wing and right wing data
    left_wing = helper.readFromFile(left_wing_file)[:45000]
    right_wing = helper.readFromFile(right_wing_file)[:45000]

    # create ml model from data
    createModel(left_wing, right_wing)
