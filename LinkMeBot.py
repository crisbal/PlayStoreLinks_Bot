"""
/u/PlayStoreLinks__Bot

A Reddit Bot made by /u/cris9696 

General workflow:

* login
* get comments
* analyze comments
* reply to valid comments
* shutdown


"""

#reddit
import praw
#general
import sys
import time
import os
import re
import cPickle as pickle
#web
import urllib
import HTMLParser
#mine
import Config
from PlayStore import PlayStore


def stopBot(doSave = True):
    logger.info("Shutting down")

    if os.path.isfile(Config.botRunningFile):
        logger.debug("Deleting lock file")
        os.remove(Config.botRunningFile)

    if doSave:
        logger.debug("Dumping already_done")
        pickle.dump( already_done, open( "done.p", "wb" ) )
        logger.debug("Really shutting down")

    sys.exit(0)

def removeRedditFormatting(text):
    return text.replace("*", "").replace("~", "").replace("^", "").replace(">","").replace("[","").replace("]","").replace("(","").replace(")","")


def isDone(comment):
    #TODO check if in the database
    if comment.id in already_done:
        logger.debug("Already replied to '" + comment.id + "'")
        return True

    already_done.append(comment.id)
    return False

def generateReply(link_me_requests):
    my_reply = ""

    nOfRequestedApps = 0
    nOfFoundApps = 0
    for link_me_request in link_me_requests:    #for each linkme command
        requested_apps = link_me_request.split(",") #split the apps by ,

        for app_name in requested_apps:
            app_name = app_name.strip()

            if len(app_name) > 0:
                app_name = HTMLParser.HTMLParser().unescape(app_name)  #html encoding to normal encoding 
                nOfRequestedApps += 1
                
                if nOfRequestedApps <= Config.maxAppsPerComment:
                    app = findApp(app_name)

                    if app:
                        nOfFoundApps += 1
                        my_reply += "[**" + app.name + "**](" + app.link + ") - " + ("Free" if app.free else "Paid") + " " + (" with IAP -" if app.IAP else " - ") + " Rating: " + app.rating + "/100 - "
                        my_reply += "Search for '" + app_name + "' on the [**Play Store**](https://play.google.com/store/search?q=" + urllib.quote_plus(app_name.encode("utf-8")) + ")\n\n"
                        
                        logger.info("'" + app_name + "' found. Name: " + app.name)
                    else:
                        my_reply +="I am sorry, I can't find any app named '" + app_name + "'.\n\n"
                        logger.info("Can't find any app named '" + app_name + "'")

    if nOfRequestedApps > Config.maxAppsPerComment:
        my_reply = "You requested more than " + str(Config.maxAppsPerComment) + " apps. I will only link to the first " + str(Config.maxAppsPerComment) + " apps.\n\n" + my_reply
    
    my_reply += Config.closingFormula

    if nOfFoundApps == 0:   #return None because we don't want to answer
        my_reply = None

    return my_reply


def findApp(app_name):
    logger.debug("Searching for '" + app_name + "'")
    app_name = app_name.lower()
    app = None

    if len(app_name)>0:
        #app = searchInDatabase(app_name)
        #if app:
        #     return app
        # else:
        try:
            app = PlayStore.search(app_name)
            return app
        except PlayStore.AppNotFoundException as e:
            return None 
    else:
        return None

def doReply(comment,myReply):
    logger.debug("Replying to '" + comment.id + "'")
    
    tryAgain = True
    while tryAgain:
        tryAgain = False
        try:
            # "#&#009;\n\n###&#009;\n\n#####&#009;\n"
            comment.reply(myReply)
            logger.info("Successfully replied to comment '" + comment.id + "'\n")
            break
        except praw.errors.RateLimitExceeded as timeError:
            logger.warning("Doing too much, sleeping for " + str(timeError.sleep_time))
            time.sleep(timeError.sleep_time)
            tryAgain = True
        except Exception as e:
            logger.error("Exception '" + str(e) + "' occured while replying to '" + comment.id + "'!")
            stopBot()


#building the logger
import logging
logger = logging.getLogger('LinkMeBot')
logger.setLevel(Config.loggingLevel)
fh = logging.FileHandler(Config.logFile)
fh.setLevel(Config.loggingLevel)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

#main method
if __name__ == "__main__":

    logger.info("Starting up")

    if os.path.isfile("/tmp/botRunning"):
        logger.warning("Bot is already running!")
        stopBot(False)
    else:
        with open(Config.botRunningFile, 'a'):
            pass

    logger.debug("Loading already_done")
    try:
        already_done = pickle.load( open( "done.p", "rb" ) )
    except IOError:
        already_done = []
    

    logger.debug("Logging in")


    try:
        r = praw.Reddit("/u/PlayStoreLinks__Bot by /u/cris9696 V2.0")
        r.login(Config.username, Config.password, disable_warning=True)
        logger.info("Successfully logged in")

    except praw.errors.RateLimitExceeded as error:
        logger.error("The Bot is doing too much! Sleeping for " + str(error.sleep_time) + " and then shutting down!")
        time.sleep(error.sleep_time)
        stopBot()

    except Exception as e:
        logger.error("Exception '" + str(e) + "' occured on login!")
        stopBot()


    subreddits = r.get_subreddit("+".join(Config.subreddits))

    link_me_regex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|;|$)", re.M | re.I)

    try:
        logger.debug("Getting the comments")
        comments = subreddits.get_comments()
        logger.info("Comments successfully downloaded")
    except Exception as e:
        logger.error("Exception '" + str(e) + "' occured while getting comments!")
        stopBot()

    for comment in comments:

        #to avoid injection of stuff
        clean_comment = removeRedditFormatting(comment.body)

        #match the request
        link_me_requests = link_me_regex.findall(clean_comment)
        #if it matches
        if len(link_me_requests) > 0:
            if not isDone(comment): #we check if we have not already answered to the comment
                logger.debug("Generating reply to '" + comment.id + "'")
                reply = generateReply(link_me_requests)
                if reply is not None:
                    doReply(comment,reply)
                else:
                    logger.info("No Apps found for comment '" + comment.id + "'. Ignoring reply.")
    stopBot()
