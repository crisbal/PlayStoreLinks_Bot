from bs4 import BeautifulSoup
import requests
import urllib

from App import App

#debug and logging
import logging
logger = logging.getLogger('PlayStore')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console_logger = logging.StreamHandler()
console_logger.setFormatter(formatter)
console_logger.setLevel(logging.DEBUG)
logger.addHandler(console_logger)

def search(app_name):
    logger.info("Searching for '" + app_name + "'")
    encoded_name = urllib.quote_plus(app_name.encode('utf-8')) #we encode the name to a valid string for a url, replacing spaces with "+" and and & with &amp; for example 

    logger.debug("Sending request for quoted seach")
    page = requests.get("http://play.google.com/store/search?q=\"" + encoded_name + "\"&c=apps&hl=en")
    logger.debug("Analyzing request for quoted seach")
    #we search for the exact name adding quotes
    app = parseSearchPage(page)

    if app is None:
        logger.debug("Sending request for unquoted seach")
        page = requests.get("http://play.google.com/store/search?q=" + encoded_name + "&c=apps&hl=en")
        logger.debug("Analyzing request for unquoted seach")
        #we search the default way, corrected by google
        app = parseSearchPage(page)
    
    if app is None:
        #if app is still none
        logger.warning("Impossibile to find " + app_name + " on the Play Store!")
        raise AppNotFoundException("Impossibile to find " + app_name + " on the Play Store!")
    
    logger.info("App was found")
    return app

def parseSearchPage(page):
    #we need to parse the resulting page to get the app we are looking for
    
    document = BeautifulSoup(page.text)
    cards = document.findAll(attrs={"class": "card"}) #we are looking for div with class set to 'card'

    if len(cards) > 0:
        #we need to get info on the first card/app we find
        card = cards[0]

        app = App()
        
        #let's do some html/css parsing
        app.name =  card.find(attrs={"class": "title"}).get("title")
        logger.debug("Got the App's name")

        app.link =  "https://play.google.com" + card.find(attrs={"class": "title"}).get("href")
        logger.debug("Got the App's link")
        
        price = card.find(attrs={"class": "display-price"})
        if price is None:
            app.free = True
        else:
            app.free = None
        logger.debug("Got the App's price")

        app.rating = card.find(attrs={"class": "current-rating"})["style"].strip().replace("width: ","").replace("%","")[:3].replace(".","")
        #we get the rating, reading it from the style attribute
        logger.debug("Got the App's rating")

        #we also download the page of the app to check for IAP and more
        logger.debug("Downlaoding the App's page")
        app_page = requests.get(app.link)
        logger.debug("Analyzing the App's page")
        app_document = BeautifulSoup(app_page.text)
        iap_element = app_document.findAll(attrs={"class": "inapp-msg"})
        if len(iap_element) > 0:
            app.IAP = True
        else:
            app.IAP = False
        logger.debug("Got the App's IAP status")

        return app

    else:
        return None


class AppNotFoundException(Exception):
    pass