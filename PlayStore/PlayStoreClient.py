import requests
import urllib

import logging

from PlayStore import App, AppNotFoundException

from lxml.html import fromstring


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

        self.logger.debug("Sending request for quoted seach")
        params = {"q": '"{}"'.format(query), "c": "apps", "hl": "en"};  # first try with
        page_request = requests.get("http://play.google.com/store/search", params=params)

        self.logger.debug("Analyzing request for quoted seach")
        app = self.parse_search_page(page_request.text)

        if app is None:
            self.logger.debug("Sending request for unquoted seach")
            params = { "q": query, "c": "apps", "hl": "en"};
            page_request = requests.get("http://play.google.com/store/search", params=params)

            self.logger.debug("Analyzing request for unquoted seach")
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

            iap_element = app_document.find_class("inapp-msg")
            if len(iap_element) > 0:
                app.IAP = True
            else:
                app.IAP = False
            self.logger.debug("Got app.IAP")

            author_element = app_document.find_class('details-info')[0].xpath('//span[@itemprop="name"]')[0]
            app.author = author_element.text_content()
            self.logger.debug("Got app.author")

            last_update_element = app_document.xpath('//div[@itemprop="datePublished"]')[0]
            app.update_date = last_update_element.text_content()
            self.logger.debug("Got app.update_date")

            file_size_elements = app_document.xpath('//div[@itemprop="fileSize"]')
            if len(file_size_elements) > 0:
                app.file_size = file_size_elements[0].text_content()
                self.logger.debug("Got app.file_size")
            else:
                self.logger.debug("Can't get app.file_size")

            num_downloads_element = app_document.xpath('//div[@itemprop="numDownloads"]')[0]
            app.num_downloads = num_downloads_element.text_content()
            self.logger.debug("Got app.num_downloads")

            num_ratings_element = app_document.find_class("reviews-num")[0]
            app.num_ratings = num_ratings_element.text_content()
            self.logger.debug("Got app.num_ratings")

            description_element = app_document.xpath('//meta[@name="description"]')[0]
            app.description = description_element.get('content')
            self.logger.debug("Got app.description")

            return app
        else:
            return None