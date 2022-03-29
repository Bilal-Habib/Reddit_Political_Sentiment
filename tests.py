import unittest
from ml_model import filterComment


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # expected output for each case
        expected = 'boris johnson prime minister'

        # comment with special chars
        comment = 'boris johnson is our prime minister $% $%^^ ^%^%^'
        self.assertEqual(filterComment(comment), expected)

        # comment with url
        comment = 'boris johnson is our prime minister https://www.nltk.org/data.html'
        self.assertEqual(filterComment(comment), expected)

        # comment with extra spaces in between words
        comment = 'boris johnson   is   our    prime  minister   '
        self.assertEqual(filterComment(comment), expected)

        # comment with uppercase letters
        comment = 'BORIS Johnson is our PRIME minister'
        self.assertEqual(filterComment(comment), expected)

        # comment with alphanumeric characters
        comment = 'boris johnson is our prime minister 1234'
        self.assertEqual(filterComment(comment), expected)

        # comment with emojis
        comment = 'boris johnson is our prime minister 😂'
        self.assertEqual(filterComment(comment), expected)

        # comment with special chars, url, extra spaces, uppercase letters, alphanumeric chars and emojis
        comment = 'boris johnson $%%>>?? is    https://www.exam.com OUr prime 123 minister 😂'
        self.assertEqual(filterComment(comment), expected)

if __name__ == '__main__':
    unittest.main()
