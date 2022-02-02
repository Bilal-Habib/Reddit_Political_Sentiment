import reddit_connection as rc

# page_name = "labouruk"
# no_posts = 1
# sort_type = "top"
#
# all_text = []
#
# posts = rc.getPosts(page_name, no_posts, sort_type)
# for p in posts:
#     all_text.append(p.selftext)
#
# comments = rc.getComments(page_name, no_posts, sort_type)
# for comment in comments:
#     all_text.append(comment.body)
#
# replies = rc.getReplies(comments)
# for reply in replies:
#     all_text.append(reply.body)
#
# print(all_text)

print(rc.getUserComments('archanidesGrip', 5))

# gather left-wing data
# gather right-wing data
# split both into training/testing (start with 70/30)
# define a list of grammar
# remove grammar from training data to increase accuracy
# create ml model
# define keywords that model should look for
# build model using training data
# get accuracy by testing it on testing data
