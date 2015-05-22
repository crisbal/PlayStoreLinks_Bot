"""
/u/PlayStoreLinks__Bot

A bot made by /u/cris9696

General workflow:

* login
* get comments
* analyze comments
* reply to valid comments
* shutdown
"""

#general
import praw
import logging
import os
import sys
import re
import cPickle as pickle

#web
import urllib
import HTMLParser

#mine
import Config

from PlayStore import PlayStore

try:
    alreadyDone = pickle.load( open( "done.p", "rb" ) )
except IOError:
    alreadyDone = []
    
def stopBot(removeFile = False):
    """if removeFile:
        os.remove(Config.botRunningFile)"""
    pickle.dump( alreadyDone, open( "done.p", "wb" ) )
    sys.exit(0)


def removeRedditFormatting(text):
    return text.replace("*", "").replace("~", "").replace("^", "").replace(">","").replace("[","").replace("]","").replace("(","").replace(")","")

def isDone(comment):
    #TODO check if in the database
    if comment.id in alreadyDone:
        logger.debug("Already replied to \"" + comment.id + "\"")
        return True

    alreadyDone.append(comment.id)
    return False


def generateComment(linkRequests):
    reply = ""
    nOfRequestedApps = 0
    nOfFoundApps = 0
    for linkRequest in linkRequests:    #for each linkme command
        appsToLink = linkRequest.split(",") #split the apps
        for app_name in appsToLink:
            app_name = app_name.strip()
            if len(app_name) > 0:
                app_name = HTMLParser.HTMLParser().unescape(app_name)  #html encoding to normal encoding 
                nOfRequestedApps += 1
                if nOfRequestedApps <= Config.maxAppsPerComment:
                    foundApp = findApp(app_name)
                    if foundApp:
                        nOfFoundApps += 1
                        reply += "[**" + foundApp.name + "**](" + foundApp.link + ") - " + ("Free" if foundApp.free else "Paid") + " " + (" with IAP -" if foundApp.IAP else " - ") + " Rating: " + foundApp.rating + "/100 - "
                        reply += "Search for \"" + app_name + "\" on the [**Play Store**](https://play.google.com/store/search?q=" + urllib.quote_plus(app_name.encode("utf-8")) + ")\n\n"
                        logger.info("\"" + app_name + "\" found. Full Name: " + foundApp.name + " - Link: " + foundApp.link)
                    else:
                        reply +="I am sorry, I can't find any app named \"" + app_name + "\".\n\n"
                        logger.info("Can't find any app named \"" + app_name + "\"")

    if nOfRequestedApps > Config.maxAppsPerComment:
        reply = "You requested more than " + str(Config.maxAppsPerComment) + " apps. I will only link to the first " + str(Config.maxAppsPerComment) + " apps.\n\n" + reply
    
    if nOfFoundApps == 0:
        reply = None

    return reply


def findApp(appName):
    logger.debug("Searching for \"" + appName + "\"")
    appName = appName.lower()
    app = None
    if len(appName)>0:
        #app = searchInDatabase(appName)
        #if app:
        #     return app
        # else:
        try:
            app = PlayStore.search(appName)
            return app
        except PlayStore.AppNotFoundException as e:
            return None 
    else:
        return None

def reply(comment,myReply):
    logger.debug("Replying to \"" + comment.id + "\"")
    myReply += Config.closingFormula
    tryAgain = True
    while tryAgain:
        tryAgain = False
        try:
            comment.reply(myReply)
            logger.info("Successfully replied to comment \"" + comment.id + "\"\n")
            break
        except praw.errors.RateLimitExceeded as timeError:
            logger.warning("Doing too much, sleeping for " + str(timeError.sleep_time))
            time.sleep(timeError.sleep_time)
            tryAgain = True
        except Exception as e:
            logger.error("Exception \"" + str(e) + "\" occured while replying to \"" + comment.id + "\"! Shutting down!")
            stopBot(True)



####### main method #######
if __name__ == "__main__":

    logger = logging.getLogger('LinkMeBot')
    logger.setLevel(Config.loggingLevel)
    fh = logging.FileHandler(Config.logFile)
    fh.setLevel(Config.loggingLevel)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    """if os.path.isfile(Config.botRunningFile):
            logger.warning("The bot is already running! Shutting down!")
            stopBot()

    open(Config.botRunningFile, "w").close()"""


    logger.debug("Logging in")
    try:
        r = praw.Reddit("/u/PlayStoreLinks__Bot by /u/cris9696")
        r.login(Config.username, Config.password)
        logger.debug("Successfully logged in")

    except praw.errors.RateLimitExceeded as error:
        logger.error("The bot is doing too much! Sleeping for " + str(error.sleep_time) + " and then shutting down!")
        time.sleep(error.sleep_time)
        stopBot(True)

    except Exception as e:
        logger.error("Exception \"" + str(e) + "\" occured on login! Shutting down!")
        stopBot(True)



    subreddits = r.get_subreddit("+".join(Config.subreddits))


    linkRequestRegex = re.compile("\\blink[\s]*medebug[\s]*:[\s]*(.*?)(?:\.|$)", re.M | re.I)

    try:
        logger.debug("Getting the comments")
        comments = subreddits.get_comments()
        logger.debug("Comments successfully loaded")
    except Exception as e:
        logger.error("Exception \"" + str(e) + "\" occured while getting comments! Shutting down!")
        stopBot(True)

    for comment in comments:
        myReply = ""
        body = removeRedditFormatting(comment.body)

        linkRequests = linkRequestRegex.findall(body)

        if len(linkRequests) > 0:
            if not isDone(comment):
                logger.info("Generating reply to \"" + comment.id + "\"")
                myReply = generateComment(linkRequests)
                
                if myReply is not None:
                    reply(comment,myReply)
                else:
                    logger.info("No apps found for comment \"" + comment.id + "\"\n\n")

    logger.debug("Shutting down")
    stopBot(True)
