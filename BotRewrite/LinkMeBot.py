"""
/u/PlayStoreLinks__Bot

A bot made by /u/cris9696

General workflow:

*login
*get comments
*reply
*shutdown

"""
import praw
import logging
import os
import sys
import re

import Config


#setting up the logger

logging.basicConfig(filename=Config.logFile,level=Config.loggingLevelFile,format='%(asctime)s %(levelname)-8s %(message)s')

console = logging.StreamHandler()
console.setLevel(Config.logginLevelConsole)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(console)


def stopBot(removeFile = False):
    if removeFile:
        os.remove(Config.botRunningFile)
    sys.exit(0)


def removeRedditFormatting(text):
    return text.replace("*", "").replace("~", "").replace("^", "").replace(">","")

def isDone(comment):
    #TODO check if in the database
    for reply in comment.replies
        if reply.name == Config.username:
            return True

    return False


def generateComment(linkRequests):
    reply = ""
    nOfFoundApps = 0
    for linkRequest in linkRequests:    #for each linkme command
        appsToLink = linkRequest.split(",") #split the apps
        for app in appsToLink:
            if nOfFoundApps<Config.maxAppsPerComment:
                foundApp = findApp(app)
                if foundApp:
                    nOfFoundApps+=1
                    reply += "[**" + foundApp.fullName + "**](" + foundApp.link + ")  -  Price: " + ("Free" if foundApp.free else "Paid") + " - Rating: " + foundApp.rating + "/100 - "
                    reply += "Search for \"" + foundApp.searchName + "\" on the [**Play Store**](https://play.google.com/store/search?q=" + foundApp.searchName + ")\n\n"
                else:
                    reply +="I am sorry, I can't find any app named \"" + app + "\".\n\n"

    if nOfFoundApps>=Config.maxAppsPerComment:
        reply = "You requestes more than " + str(Config.maxAppsPerComment) + " apps. I will only link to the first " + str(Config.maxAppsPerComment) + ".\n\n" + reply
    
    return reply

def findApp(appName):
    appName = appName.strip()
    app = App()
    if len(appName)>0:
        app = searchInDatabase(appName)
        if app:
            return app
        else:
            return searchOnPlayStore(appName)
    else:
        return None

def searchInDatabase(appName):
    return None

def searchOnPlayStore(appName):
    return None

####### main method #######
if __name__ == "__main__":

    if os.path.isfile(Config.botRunningFile):
            logging.warning("The bot is already running! Shutting down!")
            stopBot()

    open(Config.botRunningFile, "w").close()


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


    linkRequestRegex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|$)", re.M)

    try:
        logging.debug("Getting the comments")
        comments = subreddit.get_comments()
        logging.debug("Comments successfully loaded")
    except Exception as e:
        logging.error("Exception \"" + str(e) + "\" occured while getting comments! Shutting down!")
        stopBot(True)

    
    for comment in comments:
        myReply = ""

        comment.body = removeRedditFormatting(comment.body)

        linkRequests = linkRequestRegex.findall(comment.body)

        if len(linkRequests) > 0:
            if not isDone(comment):
                myReply = generateComment(linkRequests)
                

                





    stopBot(True)

