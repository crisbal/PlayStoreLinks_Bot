from bs4 import BeautifulSoup
import requests
import urllib

import logging

from PlayStore import App, AppNotFoundException

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
        self.logger.info("Searching for '" + query + "'")
        
        self.logger.debug("Sending request for quoted seach")
        params = { "q": "\"" + query + "\"", "c": "apps", "hl": "en"}; #first try with 
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
            self.logger.warning("Can't find " + query + " on the Play Store!")
            raise AppNotFoundException("Can't find " + query + " on the Play Store!")
        
        self.logger.info("App was found")
        return app

    def parse_search_page(self, page_html):
        #we need to parse the resulting page to get the app we are looking for
        
        document = BeautifulSoup(page_html, "html.parser")
        cards = document.findAll(attrs={"class": "card"}) #we are looking for div with class set to 'card', these are search results

        if len(cards) > 0:
            #we need to get info on the first card/app we find since it's probably the correct guess
            card = cards[0]

            app = App()
            
            #let's do some html/css parsing
            app.name =  card.find(attrs={"class": "title"}).get("title")
            self.logger.debug("Got app.name")

            app.link =  "https://play.google.com" + card.find(attrs={"class": "title"}).get("href")
            self.logger.debug("Got app.link")
            
            app.rating = card.find(attrs={"class": "current-rating"})["style"].strip().replace("width: ","").replace("%","")[:3].replace(".","")
            #we get the rating, reading it from the style attribute
            self.logger.debug("Got app.rating")

            #we also download the page of the app to check for IAP and more
            self.logger.debug("Downloading the App's page")
            app_page = requests.get(app.link, {"hl": "en", "gl": "us"})
            self.logger.debug("Analyzing the App's page")
            
            app_document = BeautifulSoup(app_page.text, "html.parser")
            
            price_element = app_document.find("meta", attrs={"itemprop": "price"})
            app.price = price_element["content"]
            self.logger.debug("Got app.price")
            
            if app.price is "0":
                app.free = True
            else:
                app.free = False
            self.logger.debug("Got app.free")

            iap_element = app_document.findAll(attrs={"class": "inapp-msg"})
            if len(iap_element) > 0:
                app.IAP = True
            else:
                app.IAP = False
            self.logger.debug("Got app.IAP")

            """ads_element = app_document.findAll(attrs={"class": "ads-supported-label-msg"})
            if len(ads_element) > 0:
                app.ads = True
            else:
                app.ads = False
            self.logger.debug("Got app.ads")"""

            author_element = app_document.find(attrs={"class": "details-info"}).find("span", attrs={"itemprop": "name"})
            app.author = author_element.getText()
            self.logger.debug("Got app.author")

            last_update_element = app_document.find(attrs={"itemprop": "datePublished"})
            app.update_date = last_update_element.getText()
            self.logger.debug("Got app.update_date")

            file_size_element = app_document.find(attrs={"itemprop": "fileSize"})
            app.file_size = file_size_element.getText()
            self.logger.debug("Got app.file_size")

            num_downloads_element = app_document.find(attrs={"itemprop": "numDownloads"})
            app.num_downloads = num_downloads_element.getText()
            self.logger.debug("Got app.num_downloads")

            num_ratings_element = app_document.find(attrs={"class": "reviews-num"})
            app.num_ratings = num_ratings_element.getText();
            self.logger.debug("Got app.num_ratings")

            description_element = app_document.find("meta", attrs={"name": "description"})
            app.description = description_element['content'];
            self.logger.debug("Got app.description")

            return app
        else:
            return None