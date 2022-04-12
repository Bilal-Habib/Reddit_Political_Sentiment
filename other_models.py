from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
import time
from sklearn import svm
from sklearn.metrics import classification_report
from ml_model import getCommentsLabels, filterAllComments


def getFilteredData(left_wing, right_wing):
    # set comments and labels
    comments, labels = getCommentsLabels(left_wing, right_wing)

    # filter comments
    comments = filterAllComments(comments)

    # split both into training/testing (start with 80/20)
    n_comments = len(comments)
    train_size = int(0.80 * n_comments)
    training_comments, testing_comments = comments[:train_size], comments[train_size:]
    training_labels, testing_labels = labels[:train_size], labels[train_size:]
    return [training_comments, testing_comments, training_labels, testing_labels]


def getVectorizer(training_comments, testing_comments):
    vectorizer = TfidfVectorizer(min_df=2,
                                 sublinear_tf=True,
                                 use_idf=True)
    train_term = vectorizer.fit_transform(training_comments)
    test_term = vectorizer.transform(testing_comments)
    return train_term, test_term


def createNaiveBayes(left_wing, right_wing):
    # filter data
    filtered_data = getFilteredData(left_wing, right_wing)
    training_comments, testing_comments = filtered_data[0], filtered_data[1]
    training_labels, testing_labels = filtered_data[2], filtered_data[3]

    # Create feature vectors
    train_vectors, test_vectors = getVectorizer(training_comments, testing_comments)

    model = MultinomialNB()
    model.fit(train_vectors, training_labels)
    predictions_train = model.predict(train_vectors)
    predictions_test = model.predict(test_vectors)
    print('Train Accuracy:', accuracy_score(training_labels, predictions_train))
    print('Test Accuracy:', accuracy_score(testing_labels, predictions_test))


def createSvm(left_wing, right_wing):
    # filter data
    filtered_data = getFilteredData(left_wing, right_wing)
    training_comments, testing_comments = filtered_data[0], filtered_data[1]
    training_labels, testing_labels = filtered_data[2], filtered_data[3]

    # Create feature vectors
    train_vectors, test_vectors = getVectorizer(training_comments, testing_comments)

    # Perform classification with SVM, kernel=linear
    model = svm.SVC(kernel='linear')
    t0 = time.time()
    model.fit(train_vectors, training_labels)
    t1 = time.time()
    prediction_linear = model.predict(test_vectors)
    t2 = time.time()
    time_linear_train = t1 - t0
    time_linear_predict = t2 - t1

    # results
    print("Training time: %fs; Prediction time: %fs" % (time_linear_train, time_linear_predict))
    print(classification_report(testing_labels, prediction_linear, output_dict=True))
    predictions_train = model.predict(train_vectors)
    predictions_test = model.predict(test_vectors)
    print('Train Accuracy:', accuracy_score(training_labels, predictions_train))
    print('Test Accuracy:', accuracy_score(testing_labels, predictions_test))
