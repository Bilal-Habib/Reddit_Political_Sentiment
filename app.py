from flask import Flask, render_template, request
import reddit_connection

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/getuserinput', methods=['POST'])
def getUserInput():
    user_inp = request.get_json(force=True)
    print(user_inp)
    page_name = user_inp["page_name"]
    no_posts = user_inp["no_posts"]
    post_sort_type = user_inp["sort_type"]
    print(page_name, no_posts, post_sort_type)
    comments = reddit_connection.getSubredditComments(page_name, no_posts, post_sort_type)
    for comment in comments:
        print(comment.body)
    print(len(comments))
    # print(comments[0].body)
    return "Connection Successful"


# @app.route('/send-scraped-comments', methods=['POST'])
# def sendScrapedComments():
#     user_input = getUserInput()
#     requests.post(url, data=myobj)


if __name__ == '__main__':
    app.run()
