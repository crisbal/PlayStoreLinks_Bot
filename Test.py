import unittest
import Config
import logging
Config.loggingLevel = logging.ERROR

from PlayStore import PlayStore


class TestLinkMe(unittest.TestCase):
    def setUp(self):
        self.appPlayStore = PlayStore.search("facebook")
        self.appPlayStore2 = PlayStore.search("Sleep as Android Unlock")
        
        #self.appDB = linkMe.searchInDatabase("Facebook")

    def test_playStore(self):
        self.assertEqual(self.appPlayStore.name, "Facebook",'Wrong name')
        self.assertEqual(self.appPlayStore.free, True,'Wrong Price')
        self.assertEqual(self.appPlayStore.link, "https://play.google.com/store/apps/details?id=com.facebook.katana",'Wrong Link')

        self.assertEqual(self.appPlayStore2.name, "Sleep as Android Unlock",'Wrong fullName')
        self.assertEqual(self.appPlayStore2.free, False,'Wrong Price')
        self.assertEqual(self.appPlayStore2.link, "https://play.google.com/store/apps/details?id=com.urbandroid.sleep.full.key",'Wrong Link')


if __name__ == '__main__':
    unittest.main()







