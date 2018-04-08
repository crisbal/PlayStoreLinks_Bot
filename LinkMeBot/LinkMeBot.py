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

# reddit
import praw

# general
import sys
import time
import os
import re
import pickle

# web
import urllib
import html

# mine
from . import Config
from .utils import make_logger, get_text_from_markdown, human_readable_download_number

import PlayStore

def stopBot(delete_lockfile=True):
    logger.info("Shutting down")
    if os.path.isfile(Config.botRunningFile):
        logger.debug("Deleting lock file")
        os.remove(Config.botRunningFile)
    sys.exit(0)

def is_done(comment):
    #TODO check if in the database
    comments = pickle.load( open( "doneComments", "rb" ) )
    comment.refresh()
    comment.refresh()
    if comment.id in comments:
        logger.debug('Already replied to "{}" via pickle'.format(comment.id))
        return True    
    else:
        comments.append(comment.id)
        pickle.dump(comments, open( "doneComments", "wb" ) )

    for reply in comment.replies:
        if reply.author.name.lower() == Config.username.lower():
            logger.debug('Already replied to "{}"'.format(comment.id))
            return True
    return False


def generate_reply(link_me_requests):
    reply_body = ""
    
    app_names = []
    for link_me_request in link_me_requests: # for each linkme command
        requested_apps = link_me_request.split(",") # split the apps by ','
        for app_name in requested_apps: # for each app
            app_name = app_name.strip()
            if len(app_name) > 0 and len(app_name) <= 32:
                app_names.append(app_name) 
    app_names = {v.lower(): v for v in app_names}.values() # https://stackoverflow.com/a/27531275

    nOfRequestedApps = 0
    nOfFoundApps = 0
    for app_name in app_names:
        app_name = html.unescape(app_name)  # html encoding to normal encoding 
        nOfRequestedApps += 1
        
        if nOfRequestedApps <= Config.maxAppsPerComment:
            app = find_app(app_name)

            if app:
                if len(requested_apps) == 1 and len(link_me_requests) == 1: #build pretty reply
                    reply_body += "[**{}**]({}&referrer=utm_source%3Dreddit-playstorelinks__bot) by {} | ".format(app.name, app.link, app.author)
                    reply_body += (" Free " if app.free else ("Paid: {} ".format(app.price)))
                    reply_body += ("with IAP" if app.IAP else "") + "\n\n"
                    reply_body += "> {}\n\n".format(app.description)
                    reply_body += "Rating: {}/100 | ".format(app.rating)
                    reply_body += "{} installs\n\n".format(human_readable_download_number(app.num_downloads))
                    reply_body += "[Search manually](https://play.google.com/store/search?q={})\n\n".format(app_name, urllib.parse.quote_plus(app_name))
                else:
                    reply_body += "[**{}**]({}&referrer=utm_source%3Dreddit-playstorelinks__bot) - ".format(app.name, app.link)
                    reply_body += ("Free " if app.free else ("Paid: {} ".format(app.price)))
                    reply_body += ("with IAP - " if app.IAP else " - ") 
                    reply_body += "Rating: {}/100 - ".format(app.rating)
                    reply_body += "[Search manually](https://play.google.com/store/search?q={})\n\n".format(app_name, urllib.parse.quote_plus(app_name))
                
                nOfFoundApps += 1
                logger.info("'{}' found. Name: {}".format(app_name, app.name))
            else:
                reply_body += "I can't find any app named '{}'.\n\n".format(app_name)
                logger.info("Can't find any app named '{}'".format(app_name))

    if nOfRequestedApps > Config.maxAppsPerComment:
        reply_body = "You requested more than {0} apps. I will only link to the first {0} apps.\n\n".format(Config.maxAppsPerComment) + reply_body
    
    reply_body += Config.closingFormula

    if nOfFoundApps == 0: #return None because we don't want to answer
        reply_body = None

    return reply_body


def find_app(app_name):
    logger.debug("Searching for '{}'".format(app_name))
    app_name = app_name.lower()
    try:
        playstoreclient = PlayStore.PlayStoreClient(logger_name=Config.loggerName)
        app = playstoreclient.search(app_name)
        return app
    except PlayStore.AppNotFoundException as e:
        return None 


def doReply(comment,myReply):
    logger.debug("Replying to '{}'".format(comment.id))
    
    tryAgain = True
    while tryAgain:
        tryAgain = False
        try:
            comment.reply(myReply)
            logger.info("Successfully replied to comment '{}'\n".format(comment.id))
            break
        except praw.errors.RateLimitExceeded as timeError:
            logger.warning("Doing too much, sleeping for {}".format(timeError.sleep_time))
            time.sleep(timeError.sleep_time)
            tryAgain = True
        except Exception as e:
            logger.error("Exception '{}' occured while replying to '{}'!".format(e, comment.id))
            stopBot()

logger = make_logger(Config.loggerName, 
    logfile=Config.logFile, 
    loggin_level=Config.loggingLevel)

#main method
if __name__ == "__main__":
    logger.info("Starting up")
    if os.path.isfile(Config.botRunningFile):
        logger.warning("The bot is already running")
        stopBot(delete_lockfile=False)
    else:
        with open(Config.botRunningFile, 'a'):
            pass
    logger.debug("Logging in")

    try:
        r = praw.Reddit(client_id=Config.client_id,
            client_secret=Config.client_secret,
            username=Config.username,
            password=Config.password,
            user_agent="/u/PlayStoreLinks__Bot by /u/cris9696 v4.0")
        logger.info("Successfully logged in")
    except praw.exceptions.APIException as error:
        logger.critical("Praw exception '{}' occured on login!".format(error))
        stopBot()
    except Exception as e:
        logger.critical("Unknown exception '{}' occured on login!".format(e))
        stopBot()

    subreddits = r.subreddit("+".join(Config.subreddits))

    link_me_regex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|;|$)", re.M | re.I)

    try:
        logger.debug("Getting the comments")
        comments = subreddits.comments()
        logger.info("Comments successfully downloaded")
    except Exception as e:
        logger.critical("Exception '{}' occured while getting comments!".format(e))
        stopBot()

    for comment in comments:
        # to avoid injection of stuff
        clean_comment = get_text_from_markdown(comment.body)

        # match the request
        link_me_requests = link_me_regex.findall(clean_comment)
        if len(link_me_requests) > 0:
            if not is_done(comment): # we check if we have not already answered to the comment
                logger.debug("Generating reply to '{}'".format(comment.id))
                reply = generate_reply(link_me_requests)
                if reply is not None:
                    doReply(comment, reply)
                else:
                    logger.info("No apps found for comment '{}'. Ignoring reply.".format(comment.id))
    stopBot()
