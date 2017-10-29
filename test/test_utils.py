import unittest

from LinkMeBot.utils import get_text_from_markdown 

class TestUtils(unittest.TestCase):
    def test_get_text_from_markdown(self):
        markdown = '**test** [^this](https://google.com) ~~is~~ _a_ test! https://google.com'
        text = 'test this is a test!'
        self.assertEqual(get_text_from_markdown(markdown), text)

        # make sure quoted text is discarded
        markdown = '''test
> this is a test

hello world
        '''
        text = 'test\n\nhello world'
        self.assertEqual(get_text_from_markdown(markdown), text)
        

if __name__ == '__main__':
    unittest.main()