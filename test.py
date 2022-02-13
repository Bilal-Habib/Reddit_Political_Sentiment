import reddit_connection as rc
import re as regex


stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
              'you', "you're", 'your', 'yours',
              'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
              'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
              'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
              'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
              'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
              'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
              'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
              'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
              'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
              'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
              'more', 'most', 'other', 'some', 'such', 'no', 'own',
              'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y']
#
# # posts = rc.getSubredditPosts('labouruk', 200, 'top')
# # for p in posts:
# #     print(p.selftext)
#
# comment = "imagine if it were Corbyn suggesting he would give hundreds of millions to his pals....the outrage, and how r/ukpolitics would have spoken about politburo shenanigans...god I hate this country"
#
# # Take care of non-ascii characters
# comment = (comment.encode('ascii', 'replace')).decode("utf-8")
# print(comment)
#
# # Convert text to Lower case
# comment = comment.lower()
# print(comment)
#
# # Remove multiple spacing
# space = regex.sub(r"\s+", " ", comment, flags=regex.I)
# print(space)
#
# # Remove special characters
# clean_text = regex.sub(r'[!"#$%&()*+,-./:;?@[\]^_`{|}~]', ' ', space)
# print(clean_text)
# space1 = regex.sub(r"\s+", " ", clean_text, flags=regex.I)
# print("space1", space1)
#
# comment_without_noise = [word for word in space1.split() if word not in stop_words]
# print(comment_without_noise)
# filtered_comment = ' '.join(comment_without_noise)
# print(filtered_comment)
#
# # print(comment.split())
# # print([word for word in comment])
#
#
# comment = "hello  my name is boris i hate http://www.hello.com"
# url = regex.compile(r"https?//\S+|www\.\S+")
# removed_url = url.sub(r"", comment)
# print(removed_url)

condition = False
n = 170
while not condition:
    comments = rc.getSubredditComments('tories', n, 'top')
    if len(comments) >= 2000:
        print("right: ", n)
        condition = True
    else:
        n += 1