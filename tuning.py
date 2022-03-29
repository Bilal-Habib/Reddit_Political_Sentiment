# local file imports
import helper
from ml_model import finalPreprocessing, left_wing_file, right_wing_file, embedding_dim, max_length
from keras.models import Sequential
from keras.layers import Dense, Embedding, GlobalAveragePooling1D, Dropout, LSTM, Bidirectional
# hyper-parameter tuning imports
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.metrics import classification_report


def buildModel(num_unique_words, var_dense, var_dropout, var_activation, var_optimizer):
    """ Uses arguments to build Keras model. """
    model = Sequential()
    model.add(Embedding(num_unique_words, embedding_dim, input_length=max_length))
    model.add(GlobalAveragePooling1D())
    model.add(Dense(var_dense, activation=var_activation))
    model.add(Dropout(var_dropout))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss="binary_crossentropy",
                  optimizer=var_optimizer,
                  metrics=["accuracy"])
    return model


def randomTuning(left_wing, right_wing):
    values = finalPreprocessing(left_wing, right_wing)
    num_unique_words = values[0]
    training_padded = values[1]
    training_labels = values[2]
    testing_padded = values[3]
    testing_labels = values[4]

    _dense_vals = [24, 32, 64]
    _dropouts = [0, 0.2, 0.4, 0.6]
    _activations = ['relu']
    _optimizers = ['adam']
    params = dict(
        num_unique_words=[num_unique_words],
        var_dense=_dense_vals,
        var_dropout=_dropouts,
        var_activation=_activations,
        var_optimizer=_optimizers
    )

    model = KerasClassifier(build_fn=buildModel, epochs=20)

    rscv = RandomizedSearchCV(model, param_distributions=params, n_iter=10)
    rscv.fit(training_padded, training_labels)
    print(" Results from Random Search ")
    print("\n The best estimator across ALL searched params:\n", rscv.best_estimator_)
    print("\n The best score across ALL searched params:\n", rscv.best_score_)
    print("\n The best parameters across ALL searched params:\n", rscv.best_params_)

    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = testing_labels, rscv.predict(testing_padded)
    print(classification_report(y_true, y_pred))
    print()


def exhaustiveTuning(left_wing, right_wing):
    values = finalPreprocessing(left_wing, right_wing)
    num_unique_words = values[0]
    training_padded = values[1]
    training_labels = values[2]
    testing_padded = values[3]
    testing_labels = values[4]
    _dense_vals = [16, 24, 32, 64]
    _dropouts = [0, 0.2, 0.4, 0.6]
    _activations = ['tanh', 'relu', 'selu']
    _optimizers = ['sgd', 'adam']
    _batch_size = [16, 32, 64]
    params = dict(
        num_unique_words=[num_unique_words],
        var_dense=_dense_vals,
        var_dropout=_dropouts,
        var_activation=_activations,
        var_optimizer=_optimizers,
        batch_size=_batch_size)

    model = KerasClassifier(build_fn=buildModel, epochs=20, batch_size=16)

    gscv = GridSearchCV(model, params)
    gscv.fit(training_padded, training_labels)
    print(" Results from Grid Search ")
    print("\n The best estimator across ALL searched params:\n", gscv.best_estimator_)
    print("\n The best score across ALL searched params:\n", gscv.best_score_)
    print("\n The best parameters across ALL searched params:\n", gscv.best_params_)

    print("Detailed classification report:")
    print()
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    print()
    y_true, y_pred = testing_labels, gscv.predict(testing_padded)
    print(classification_report(y_true, y_pred))
    print()


if __name__ == '__main__':
    left_wing = helper.readFromFile(left_wing_file)[:45000]
    right_wing = helper.readFromFile(right_wing_file)[:45000]
    randomTuning(left_wing, right_wing)
    exhaustiveTuning(left_wing, right_wing)
