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
    r = praw.Reddit("/u/PlayStoreLinks__Bot by /u/cris9696 V3.0")
    r.login(Config.username, Config.password, disable_warning=True)
    logger.info("Successfully logged in")

except praw.errors.RateLimitExceeded as error:
    logger.error("The Bot is doing too much! Sleeping for " + str(error.sleep_time) + " and then shutting down!")
    time.sleep(error.sleep_time)
    stopBot()

except Exception as e:
    logger.error("Exception '" + str(e) + "' occured on login!")
    stopBot()


user = r.get_redditor(Config.username)
comments = user.get_comments()

for comment in comments:
    if(comment.score <= -1):
        logger.warn("Removing comment " + comment.id)
        comment.delete()
