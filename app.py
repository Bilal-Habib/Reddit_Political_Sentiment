from flask import Flask, render_template, request
import reddit_connection
import ml_model

app = Flask(__name__)


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
    print(type(page_type), type(page_name), type(no_posts), type(post_sort_type))
    comments = []
    column_names = []
    # check if page type requested is a subreddit or a user
    if page_type == 'subredditPage':
        column_names = ['Username', 'Comment', 'Sentiment Value']
        comments = reddit_connection.getSubredditComments(page_name, no_posts, post_sort_type)
    elif page_type == 'usernamePage':
        column_names = ['Comment', 'Sentiment Value']
        comments = reddit_connection.getUserComments(page_name, no_posts, post_sort_type)

    # column_names = ['Username', 'Comment', 'Sentiment Value']
    # comments = reddit_connection.getSubredditComments(page_name, no_posts, post_sort_type)
    table_data = ml_model.predictComments(page_type, comments)

    return {'connection': 'Successful', 'column_names': column_names, 'comments': table_data}


if __name__ == '__main__':
    app.run()
