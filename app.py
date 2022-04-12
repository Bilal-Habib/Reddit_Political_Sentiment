from flask import Flask, render_template, request
import reddit_connection as rc
import ml_model
import rsa


app = Flask(__name__)
# generate public and private key when app loads up
public_key, private_key = rsa.newkeys(512)


@app.route('/')
def home():
    return render_template('index.html')


# endpoint receives user input and sends back data (to front-end) to create visualisations
@app.route('/getuserinput', methods=['POST'])
def getUserInput():
    # get user input in JSON format
    user_inp = request.get_json()
    print('Retrieved User Input:', user_inp)
    page_type = user_inp['page_type']
    page_name = user_inp['page_name']
    no_posts = user_inp['no_posts']
    post_sort_type = user_inp['sort_type']
    is_encrypted = user_inp['is_encrypted']
    print(type(page_type), type(page_name), type(no_posts), type(post_sort_type), type(is_encrypted))
    comments = []
    column_names = []
    # check if page type requested is a subreddit or a user
    if page_type == 'r/':
        # check if subreddit exists
        if rc.subExists(page_name):
            print('Subreddit IS REAL!!!')
            print('Comments from subreddit are being fetched')
            column_names = ['Sentiment Weight', 'Comment', 'Username']
            comments = rc.getSubredditComments(page_name, no_posts, post_sort_type)
        else:
            print('Subreddit Does Not Exist!!!')
            return {'connection': '404'}
    elif page_type == 'u/':
        # check if user exists if it is not encrypted
        if is_encrypted == 'no':
            if rc.userExists(page_name):
                print('User IS REAL!!!')
                print('Comments from user are being fetched')
                column_names = ['Sentiment Weight', 'Comment']
                comments = rc.getUserComments(is_encrypted, page_name, no_posts, post_sort_type)
            else:
                print('User Does Not Exist!!!')
                return {'connection': '404'}
        else:
            print('User IS REAL!!!')
            column_names = ['Sentiment Weight', 'Comment']
            comments = rc.getUserComments(is_encrypted, page_name, no_posts, post_sort_type)

    left_wing_dataset, right_wing_dataset = ml_model.predictComments(page_type, comments)

    return {'connection': 'Successful', 'column_names': column_names,
            'left_wing_dataset': left_wing_dataset, 'right_wing_dataset': right_wing_dataset}


if __name__ == '__main__':
    app.run()
