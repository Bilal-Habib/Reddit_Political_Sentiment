from flask import Flask, render_template, request
import reddit_connection
import ml_model
import rsa

app = Flask(__name__)
public_key, private_key = rsa.newkeys(512)


@app.route('/')
def home():
    return render_template('index.html')


# endpoint receives user input and sends back data (to front-end) to create table
@app.route('/getuserinput', methods=['POST'])
def getUserInput():
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
        column_names = ['Sentiment Value', 'Comment', 'Username']
        comments = reddit_connection.getSubredditComments(page_name, no_posts, post_sort_type)
    elif page_type == 'u/':
        column_names = ['Sentiment Value', 'Comment']
        comments = reddit_connection.getUserComments(is_encrypted, page_name, no_posts, post_sort_type)

    left_wing_dataset, right_wing_dataset = ml_model.predictComments(page_type, comments)

    return {'connection': 'Successful', 'column_names': column_names,
            'left_wing_dataset': left_wing_dataset, 'right_wing_dataset': right_wing_dataset}


if __name__ == '__main__':
    app.run()
