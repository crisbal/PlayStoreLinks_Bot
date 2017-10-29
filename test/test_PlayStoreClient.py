import unittest

import PlayStore

class TestLinkMe(unittest.TestCase):
    def setUp(self):
        playStore = PlayStore.PlayStoreClient()
        self.app = playStore.search("facebook")
        self.app2 = playStore.search("Sleep as Android Unlock")
        self.app3 = playStore.search("Plants vs. Zombies FREE")
        
        #self.appDB = linkMe.searchInDatabase("Facebook")

    def test_playStore(self):
        self.assertEqual(self.app.name, "Facebook")
        self.assertEqual(self.app.link, "https://play.google.com/store/apps/details?id=com.facebook.katana")
        self.assertEqual(self.app.free, True)
        self.assertEqual(self.app.price, "0")

        self.assertEqual(self.app2.name, "Sleep as Android Unlock")
        self.assertEqual(self.app2.link, "https://play.google.com/store/apps/details?id=com.urbandroid.sleep.full.key")
        self.assertEqual(self.app2.free, False)
        self.assertNotEqual(self.app2.price, "0")

        self.assertEqual(self.app3.name, "Plants vs. Zombies FREE")
        self.assertEqual(self.app3.link, "https://play.google.com/store/apps/details?id=com.ea.game.pvzfree_row")
        self.assertEqual(self.app3.free, True)
        self.assertEqual(self.app3.price, "0")

if __name__ == '__main__':
    unittest.main()
    