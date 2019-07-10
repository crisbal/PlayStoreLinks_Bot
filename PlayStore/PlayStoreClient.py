import requests
import urllib

import logging

from PlayStore import App, AppNotFoundException

from lxml.html import fromstring

SEARCH_URL = "https://play.google.com/store/search"

class PlayStoreClient():
    def __init__(self, logger_name = None):
        if logger_name:
            self.logger = logging.getLogger(logger_name)
        else:
            logger = logging.getLogger('PlayStore')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            console_logger = logging.StreamHandler()
            console_logger.setFormatter(formatter)
            console_logger.setLevel(logging.DEBUG)
            logger.addHandler(console_logger)
            self.logger = logger

    def search(self, query):
        self.logger.info("Searching for '{}'".format(query))

        self.logger.debug("Sending request for quoted search")
        params = {"q": '"{}"'.format(query), "c": "apps", "hl": "en", "gl": "us"};  # first try with
        page_request = requests.post(SEARCH_URL, params=params)
        self.logger.debug('POST: {}'.format(page_request.url))        
        self.logger.debug("Analyzing request for quoted search")
        app = self.parse_search_page(page_request.text)

        if app is None:
            self.logger.debug("Sending request for unquoted search")
            params = { "q": query, "c": "apps", "hl": "en", "gl": "us"};
            page_request = requests.post(SEARCH_URL, params=params)
            self.logger.debug('POST: {}'.format(page_request.url))        
            self.logger.debug("Analyzing request for unquoted search")
            app = self.parse_search_page(page_request.text)

        if app is None:
            #if app is still none
            self.logger.warning("Can't find {} on the Play Store!".format(query))
            raise AppNotFoundException("Can't find {} on the Play Store!".format(query))

        self.logger.info("App was found")
        return app

    def parse_search_page(self, search_page_html):
        #we need to parse the resulting page to get the app we are looking for

        document = fromstring(search_page_html)
        cards = document.find_class("card") #we are looking for div with class set to 'card', these are search results

        if len(cards) > 0:
            #we need to get info on the first card/app we find since it's probably the correct guess
            card = cards[0]

            app = App()

            #let's do some html/css parsing
            app.name =  card.find_class("title")[0].get("title")
            self.logger.debug("Got app.name")

            app.link =  "https://play.google.com" + card.find_class("title")[0].get("href")
            self.logger.debug("Got app.link")

            app.rating = card.find_class("current-rating")[0].get("style").strip().replace("width: ","").replace("%","")[:3].replace(".","")
            #we get the rating, reading it from the style attribute
            self.logger.debug("Got app.rating")

            #we also download the page of the app to check for IAP and more
            self.logger.debug("Downloading the App's page")
            app_page_html = requests.get(app.link, {"hl": "en", "gl": "us"}).text
            self.logger.debug("Analyzing the App's page")

            app_document = fromstring(app_page_html)

            price_element = app_document.xpath("//meta[@itemprop='price']")[0]
            app.price = price_element.get("content")
            self.logger.debug("Got app.price")

            if app.price is "0":
                app.free = True
            else:
                app.free = False
            self.logger.debug("Got app.free")

            app.author = app_document.xpath("//a[contains(@href,'apps/dev')]")[0].text.strip() 
            #Hacky fix to parse additional information section at bottom of page
            app.IAP = False
            additional_info_elements = app_document.xpath("//c-wiz/div/div/h2[text() = 'Additional Information']")[0].getparent().getparent().xpath("./div[2]/div[1]/div[not(contains(@class, ' '))]")
            for item in additional_info_elements:
                item_name = item.getchildren()[0].text.strip()
                valid_items = ["Updated", "Size", "Installs", "In-app Products"]
                if item_name in valid_items:
                    data = item.getchildren()[1].getchildren()[0].getchildren()[0].text.strip()
                    if item_name == "Updated":
                        app.update_date = data
                        self.logger.debug("Got app.update_date")
                    elif item_name == "Size":
                        if data != "Varies with Device":
                            app.file_size = data
                            self.logger.debug("Got app.file_size")
                    elif item_name == "Installs":
                        app.num_downloads = data
                        self.logger.debug("Got app.num_downloads")
                    elif item_name == "In-app Products":
                        app.IAP = True
                        self.logger.debug("Got app.IAP")

            #num_ratings_element = app_document.xpath('//meta[@itemprop="ratingCount"]')[0]
            #app.num_ratings = num_ratings_element.attrib['content']
            #self.logger.debug("Got app.num_ratings")

            description_element = app_document.xpath('//meta[@name="description"]')[0]
            app.description = description_element.get('content')
            self.logger.debug("Got app.description")

            return app
        else:
            return None
