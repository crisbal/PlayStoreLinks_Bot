import unittest
import Config
import logging
Config.loggingLevel = logging.ERROR

import LinkMeBot as linkMe


class TestLinkMe(unittest.TestCase):
    def setUp(self):
        self.appPlayStore = linkMe.searchOnPlayStore("facebook")
        #self.appDB = linkMe.searchInDatabase("Facebook")

    def test_playStore(self):
        self.assertEqual(self.appPlayStore.fullName, "Facebook",'Wrong fullName')
        self.assertEqual(self.appPlayStore.free, True,'Wrong Price')
        self.assertEqual(self.appPlayStore.link, "https://play.google.com/store/apps/details?id=com.facebook.katana",'Wrong Link')
        self.assertEqual(self.appPlayStore.searchName, "facebook",'Wrong Search Name')


if __name__ == '__main__':
    unittest.main()







