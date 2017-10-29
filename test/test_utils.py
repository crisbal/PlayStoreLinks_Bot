import unittest

from LinkMeBot.utils import get_text_from_markdown, human_readable_download_number

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
        
    def test_human_readable_download_number(self):
        self.assertEqual(human_readable_download_number('12'), '12')
        self.assertEqual(human_readable_download_number('12000'), '12 thousand')
        self.assertEqual(human_readable_download_number('12000000'), '12 million')
        self.assertEqual(human_readable_download_number('12,000,000 - 15,000,000'), '12 million')        
        
if __name__ == '__main__':
    unittest.main()