#reddit
import praw
#mine
import Config

#general
import sys
import time

#building the logger
import logging
logger = logging.getLogger('LinkMeBot')
logger.setLevel(Config.loggingLevel)
fh = logging.FileHandler(Config.logFileDelete)
fh.setLevel(Config.loggingLevel)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

def stopBot():
    logger.info("Shutting down")
    sys.exit(0)

try:
    r = praw.Reddit(client_id=Config.client_id,
        client_secret=Config.client_secret,
        username=Config.username,
        password=Config.password,
        user_agent="/u/PlayStoreLinks__Bot by /u/cris9696 v4.0")
    logger.info("Successfully logged in")
except praw.errors.RateLimitExceeded as error:
    logger.error("The Bot is doing too much! Sleeping for {} and then shutting down!".format(error.sleep_time))
    time.sleep(error.sleep_time)
    stopBot()
except Exception as e:
    logger.error("Exception '{}' occured on login!".format(e))
    stopBot()


user = r.redditor(Config.username)
comments = user.comments.new()

for comment in comments:
    if(comment.score <= -1):
        logger.warn("Removing comment {}".format(comment.id))
        comment.delete()
