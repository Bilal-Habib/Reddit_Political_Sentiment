import pickle
import rsa
import app
import ast


folder = 'pickled_files/'


def readFromFile(filename):
    with open(folder + filename, 'rb') as file:
        loaded_data = pickle.load(file)
    return loaded_data


def writeToFile(filename, data):
    with open(folder + filename, 'wb') as file:
        pickle.dump(data, file)


def encryptName(username):
    cipher_text = str(rsa.encrypt(username.encode(), app.public_key))
    return cipher_text


def decryptName(username):
    decoded = ast.literal_eval(username)
    plain_text = rsa.decrypt(decoded, app.private_key).decode()
    return plain_text
