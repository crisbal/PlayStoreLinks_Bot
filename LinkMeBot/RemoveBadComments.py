#reddit
import praw
#mine
from . import Config
from .utils import make_logger

#general
import sys
import time

#building the logger
logger = make_logger(Config.loggerName + '-Remover', 
    logfile=Config.logFile, 
    loggin_level=Config.loggingLevel)

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

stopBot()