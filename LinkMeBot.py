"""
/u/PlayStoreLinks__Bot

A bot made by /u/cris9696

General workflow:

*login
*get comments
*reply
*shutdown
"""

#general
import praw
import logging
import os
import sys
import re

#web
import urllib
import HTMLParser
from bs4 import BeautifulSoup
import requests


#DB
from peewee import fn
#mine
import Config
from App import App
from AppDB import AppDB

#setting up the logger

logging.basicConfig(filename=Config.logFile,level=Config.loggingLevel,format='%(levelname)-8s %(message)s')

console = logging.StreamHandler()
console.setLevel(Config.loggingLevel)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(console)


def stopBot(removeFile = False):
    """if removeFile:
        os.remove(Config.botRunningFile)"""
    sys.exit(0)


def removeRedditFormatting(text):
    return text.replace("*", "").replace("~", "").replace("^", "").replace(">","").replace("[","").replace("]","").replace("(","").replace(")","")

def isDone(comment):
    #TODO check if in the database
    for reply in comment.replies:
        if reply.author.name == Config.username:
            logging.debug("Already replied to \"" + comment.id + "\"")
            return True

    return False


def generateComment(linkRequests):
    reply = ""
    nOfRequestedApps = 0
    nOfFoundApps = 0
    for linkRequest in linkRequests:    #for each linkme command
        appsToLink = linkRequest.split(",") #split the apps
        for app in appsToLink:
            app = app.strip()
            if len(app) > 0:
                app = HTMLParser.HTMLParser().unescape(app)  #html encoding to normal encoding 
                nOfRequestedApps += 1
                if nOfRequestedApps <= Config.maxAppsPerComment:
                    foundApp = findApp(app)
                    if foundApp:
                        nOfFoundApps += 1
                        reply += "[**" + foundApp.fullName + "**](" + foundApp.link + ") - Price: " + ("Free" if foundApp.free else "Paid") + " - Rating: " + foundApp.rating + "/100 - "
                        reply += "Search for \"" + app + "\" on the [**Play Store**](https://play.google.com/store/search?q=" + urllib.quote_plus(foundApp.searchName.encode("utf-8")) + ")\n\n"
                        logging.info("\"" + app + "\" found. Full Name: " + foundApp.fullName + " - Link: " + foundApp.link)
                    else:
                        reply +="I am sorry, I can't find any app named \"" + app + "\".\n\n"
                        logging.info("Can't find any app named \"" + app + "\"")

    if nOfRequestedApps > Config.maxAppsPerComment:
        reply = "You requested more than " + str(Config.maxAppsPerComment) + " apps. I will only link to the first " + str(Config.maxAppsPerComment) + " apps.\n\n" + reply
    
    if nOfFoundApps == 0:
        reply = None

    return reply


def findApp(appName):
    logging.debug("Searching for \"" + appName + "\"")
    appName = appName.lower()
    app = None
    if len(appName)>0:
       #app = searchInDatabase(appName)
       #if app:
       #     return app
       # else:
       return searchOnPlayStore(appName)
    else:
        return None

def searchInDatabase(appName):
    logging.debug("Searching in database for '" + appName + "'")
    try:
        appDB = AppDB.select().where((fn.Lower(AppDB.fullName) == appName) | (fn.Lower(AppDB.searchName) == appName)).get()
    except AppDB.DoesNotExist:
        logging.debug("'" + appName + "' NOT found in the DB")
        return None
    #logging.info("'" + appName + "' found in the DB")
    #return appDB
    return None

def parseResultsPage(request,appName):
    page = BeautifulSoup(request.text)
    cards = page.findAll(attrs={"class": "card"})
    if len(cards) > 0:
        app = getAppFromCard(cards[0])
        if app:
            app.searchName = appName
            #addToDB(app)
        return app
    else:
        return None

def searchOnPlayStore(appName):
    appNameNoUnicode = appName.encode('utf-8') #to utf-8 because quote_plus don't like unicode!
    encodedName = urllib.quote_plus(appNameNoUnicode)
    try:
        request = requests.get("http://play.google.com/store/search?q=\"" + encodedName + "\"&c=apps&hl=en")
        app = parseResultsPage(request,appName)

        if app == None:
            request = requests.get("http://play.google.com/store/search?q=" + encodedName + "&c=apps&hl=en")
            app = parseResultsPage(request,appName)
        
        logging.info("'" + appName + "' found on the PlayStore")
        return app
    except Exception as e:
        logging.error("Exception \"" + str(e) + "\" occured while searching on the Play Store! Shutting down!")
        stopBot(True)

def getAppFromCard(card):
    app = App()
    app.fullName =  card.find(attrs={"class": "title"}).get("title")
    app.link =  "https://play.google.com" + card.find(attrs={"class": "title"}).get("href")
    price = card.find(attrs={"class": "display-price"}).get_text().strip().lower()
    app.free = True if price == "" or price == "free" else False
    app.rating = card.find(attrs={"class": "current-rating"})["style"].strip().replace("width: ","").replace("%","")[:3].replace(".","")
    return app

def reply(comment,myReply):
    logging.debug("Replying to \"" + comment.id + "\"")
    myReply += Config.closingFormula
    tryAgain = True
    while tryAgain:
        tryAgain = False
        try:
            comment.reply(myReply)
            logging.info("Successfully replied to comment \"" + comment.id + "\"\n")
            break
        except praw.errors.RateLimitExceeded as timeError:
            logging.warning("Doing too much, sleeping for " + str(timeError.sleep_time))
            time.sleep(timeError.sleep_time)
            tryAgain = True
        except Exception as e:
            logging.error("Exception \"" + str(e) + "\" occured while replying to \"" + comment.id + "\"! Shutting down!")
            stopBot(True)

def addToDB(app):
    appDB = AppDB()
    appDB.fullName = app.fullName
    appDB.link = app.link
    appDB.rating = app.rating
    appDB.free = app.free
    appDB.searchName = app.searchName
    appDB.save()
####### main method #######
if __name__ == "__main__":

    """if os.path.isfile(Config.botRunningFile):
            logging.warning("The bot is already running! Shutting down!")
            stopBot()

    open(Config.botRunningFile, "w").close()"""


    logging.debug("Logging in")
    try:
        r = praw.Reddit("/u/PlayStoreLinks__Bot by /u/cris9696")
        r.login(Config.username, Config.password)
        logging.debug("Successfully logged in")

    except praw.errors.RateLimitExceeded as error:
        logging.error("The bot is doing too much! Sleeping for " + str(error.sleep_time) + " and then shutting down!")
        time.sleep(error.sleep_time)
        stopBot(True)

    except Exception as e:
        logging.error("Exception \"" + str(e) + "\" occured on login! Shutting down!")
        stopBot(True)



    subreddits = r.get_subreddit("+".join(Config.subreddits))


    linkRequestRegex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|$)", re.M | re.I)

    try:
        logging.debug("Getting the comments")
        comments = subreddits.get_comments()
        logging.debug("Comments successfully loaded")
    except Exception as e:
        logging.error("Exception \"" + str(e) + "\" occured while getting comments! Shutting down!")
        stopBot(True)

    
    for comment in comments:
        myReply = ""
        body = removeRedditFormatting(comment.body)

        linkRequests = linkRequestRegex.findall(body)

        if len(linkRequests) > 0:
            if not isDone(comment):
                logging.info("Generating reply to \"" + comment.id + "\"")
                myReply = generateComment(linkRequests)
                
                if myReply is not None:
                    reply(comment,myReply)
                else:
                    logging.info("No apps found for comment \"" + comment.id + "\"\n\n")
                
    logging.debug("Shutting down")
    
    stopBot(True)
