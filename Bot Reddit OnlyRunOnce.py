"""
/u/PlayStoreLinks_Bot

A bot made by /u/cris9696

UNDER MIT LICENSE

IF YOU FIND ANY BUG OR ANYTHING EVIL OR ANY EXPLOITABLE PART PLEASE REPORT IT TO ME

TODO:

*fix random crashes, sometimes I find the cache file smaller, this mean the bot crashed while running(?)
"""
import praw   #reddit wrapper
import requests
import time
import re   #regex stuff
import pickle  #dump list and dict to file
import os
import sys
import atexit  #this is needed to handle unexpected crashes or just normal exiting
from time import gmtime, strftime 
from bs4 import BeautifulSoup  #to parse html
import logging


dbFile = "db" + "7"   #which is the file i need to save already done applications?
cacheFile = '/tmp/botcommentscache' #which is the file i need to save already done comments?
categoriesFolder = "categories"
logging.basicConfig(filename='bot.log',level=logging.INFO,format="%(asctime)s %(message)s")


fileOpened = False   #flag to check if cache files are already opened, I need to do something better


"""
 _____ _   _ _   _  ____ _____ ___ ___  _   _ ____  
|  ___| | | | \ | |/ ___|_   _|_ _/ _ \| \ | / ___| 
| |_  | | | |  \| | |     | |  | | | | |  \| \___ \ 
|  _| | |_| | |\  | |___  | |  | | |_| | |\  |___) |
|_|    \___/|_| \_|\____| |_| |___\___/|_| \_|____/ 
                                                    
 ____  _____ ____ _        _    ____      _  _____ ___ ___  _   _ 
|  _ \| ____/ ___| |      / \  |  _ \    / \|_   _|_ _/ _ \| \ | |
| | | |  _|| |   | |     / _ \ | |_) |  / _ \ | |  | | | | |  \| |
| |_| | |__| |___| |___ / ___ \|  _ <  / ___ \| |  | | |_| | |\  |
|____/|_____\____|_____/_/   \_\_| \_\/_/   \_\_| |___\___/|_| \_|

"""

def exit_handler():  #called when exiting the program
	if fileOpened:   #if file are opened we dump the cache in them
		pickle.dump(already_done, f)
		f.close()
		pickle.dump(nameLinkDict, fi)
		fi.close()
	log("Shutting Down\n\n\n")  
	os.remove("theBotIsRunning")   #this file is to check if the bot is running

atexit.register(exit_handler)  #register the function that get called on exit

 
def cleanString(appName):   #take care of "exploits" done by formatting the app name
 	return appName.replace("*","").replace("~~","").replace("^","").replace("\""," ").replace("]"," ").replace("["," ").replace("("," ").replace(")"," ").strip()


#find the app name and get the url
def generateComment( comment ):
	appName = cleanString(comment).lower()
	log ("Now searching for app: " + appName)

	if appName in nameLinkDict:  #if I have the app on the local cache
		comment = "[**" + appName.title() + "**](" + nameLinkDict[appName] + ")  -  "  #generate the first url
		comment += "Search for \"" + appName.title() + "\" on the [**Play Store**](https://play.google.com/store/search?q=" + appName.replace("+","%2B").replace(" ","+") + ")\n\n"
		log (appName + " found on the local cache") 
		return comment

	while True:
		try:
			#this is a literal search, it uses " " to match the exact same name, if this is not working I use similar search
			request = requests.get("http://play.google.com/store/search?q=\"" + appName.replace("+","%2B").replace(" ","+").replace("&","%26")+"\"&c=apps&hl=en")  #send the request  
			
			page = BeautifulSoup(request.text)  #parse the page we just got to so we can use it as an object for bs4

			searchResults = page.findAll(attrs={'class': "card-content-link"})
			if len(searchResults) is not 0:
				link = searchResults[0] #we get the link if it exists
				parent = link.parent.parent
				trueName = cleanString(parent.findAll(attrs={'class': "title"})[0].get('title'))
				if link is not None: #if the link is not null
					appLink = "https://play.google.com" + link.get('href')  #url of the app
					nameLinkDict[trueName.lower()] = appLink
					comment = "[**" + trueName + "**](" + appLink + ")  -  "  #generate the first url
					comment += "Search for \"" + appName.title() + "\" on the [**Play Store**](https://play.google.com/store/search?q=" + appName.replace("+","%2B").replace(" ","+") + ")\n\n"  #generate the second url (aka search url)
					
					log("Search: " + appName.title() + " - Found: " + trueName + " - LITERAL SEARCH") #log
					
					return comment;
				else:
					return similarSearch(appName)
			else:
				return similarSearch(appName)
		except Exception as e:
			log ("Exception occured on LITERAL SEARCH: " + str(e))
			time.sleep(3)



def similarSearch(appName):
	#similar search: only if literal search returned no results, we use similar search, this means "what google play store thinks is the app we are looking for"
	#it should also fix spelling error
	try:
		request = requests.get("http://play.google.com/store/search?q=" + appName.replace("+","%2B").replace(" ","+").replace("&","%26")+"&c=apps&hl=en")  #send the request
			   
		page = BeautifulSoup(request.text)  #parse the page we just got to so we can use it as an object for bs4

		if len(page.findAll(attrs={'class': "card-content-link"})) is not 0:
			searchResults = page.findAll(attrs={'class': "card-content-link"})
			if len(searchResults) is not 0:
				link = searchResults[0] #we get the link if it exists
				parent = link.parent.parent
				trueName = cleanString(parent.findAll(attrs={'class': "title"})[0].get('title'))
				if link is not None: #if the link is not null
					appLink = "https://play.google.com" + link.get('href')  #url of the app
					nameLinkDict[trueName.lower()] = appLink
					comment = "[**" + trueName + "**](" + appLink + ")  -  "  #generate the first url
					comment += "Search for \"" + appName.title() + "\" on the [**Play Store**](https://play.google.com/store/search?q=" + appName.replace("+","%2B").replace(" ","+") + ")\n\n"  #generate the second url (aka search url)
					
					log("Search: " + appName.title() + " - Found: " + trueName + " - SIMILAR SEARCH") #log
					
					return comment;
			else:
				log("Can't find an app named " + appName.title() + "!") #log
				return False
		else:
			log("Can't find an app named " + appName.title() + "!") #log
			return False
	except Exception as e:
		log ("Exception occured on LITERAL SEARCH: " + str(e))
		time.sleep(3)

def exitBot():  #function to exit the bot, will be used when logging will be implemented
	sys.exit()


def log(what = "Not defined"):   #this log and print everything, use this and not print
	print(str(what.encode("ascii", "ignore")))
	logging.info(what)

def isDone(comment):  #check if a comment object is already done
	if comment.id not in already_done and comment.author.name !="PlayStoreLinks_Bot":  #if it is not in the already_done array it means i need to work on it.
		comment_replies = comment.replies #i get its replies
		for reply in comment_replies: #for each reply
			if reply.author.name == "PlayStoreLinks_Bot":  #i check if i answered
				already_done.append(comment.id)  #i add it to the list
				return True
		return False
	else:
		return True

def reply(what,comment): #reply to a comment object with the what string
	what += "\n\n------\n\n**[^I ^am ^now ^open ^source!](http://www.reddit.com/r/cris9696/comments/1u6d1p/)**^( Feedback/bug report? Send a message to ) ^[cris9696](http://www.reddit.com/message/compose?to=cris9696).\n\n"
	while True:
		try:  #i try to reply to the comment
			comment.reply(what)
			break
		except praw.errors.RateLimitExceeded as error:
			log ("Doing too much, sleeping for " + str(error.sleep_time))
			time.sleep(error.sleep_time)
		except Exception as e:
			log ("Exception occured while replying: " + str(e))
			time.sleep(3)

def generateCategory(categoryName):   #link to a full category of apps, like all reddit apps or facebook apps
	log("Searching for category: " + categoryName)
	text = ""
	dictOfApps= dict()
	categoryName = cleanString(categoryName).lower()

	redditCat = ["reddit","reddit app","reddit apps","reddit client","reddit clients"]
	facebookCat = ["facebook","facebook apps","facebook app","facebook client","facebook clients"]
	keyboardCat = ["keyboard","keyboards"]
	smsCat = ["sms","sms app","sms apps","sms client","sms clients"]
	if categoryName in redditCat:
		text = "List of **Reddit Apps**:\n\n"
		dictOfApps = pickle.load(open(categoriesFolder+"/reddit", 'r+'))
	elif categoryName in facebookCat:
		text = "List of **Facebook Apps**:\n\n"
		dictOfApps = pickle.load(open(categoriesFolder+"/facebook", 'r+'))
	elif categoryName in keyboardCat:
		text = "List of **Keyboards**:\n\n"
		dictOfApps = pickle.load(open(categoriesFolder+"/keyboard", 'r+'))
	elif categoryName in smsCat:
		text = "List of **SMS Apps**:\n\n"
		dictOfApps = pickle.load(open(categoriesFolder+"/sms", 'r+'))
	else:
		return False

	
	for key in sorted(dictOfApps.iterkeys()):
		text += "[**" + key.title() + "**]("+dictOfApps[key]+")\n\n"
	return text + "\n\n^(An app is missing? Please write to my author about it)\n\n"

"""
 __  __    _    ___ _   _ 
|  \/  |  / \  |_ _| \ | |
| |\/| | / _ \  | ||  \| |
| |  | |/ ___ \ | || |\  |
|_|  |_/_/   \_\___|_| \_|
 __  __ _____ _____ _   _  ___  ____  
|  \/  | ____|_   _| | | |/ _ \|  _ \ 
| |\/| |  _|   | | | |_| | | | | | | |
| |  | | |___  | | |  _  | |_| | |_| |
|_|  |_|_____| |_| |_| |_|\___/|____/ 

"""


if(os.path.isfile('theBotIsRunning')):   #if the bot is already running
	log("Bot already running!")
	exitBot()

#the bot was not running 
open('theBotIsRunning', 'w').close()  #create the file that tell the bot is running


try:
	with open ("login.txt", "r") as loginFile:     #reading login info from a file, it should be username (newline) password
		loginInfo = loginFile.readlines()
	loginInfo[0] = loginInfo[0].replace('\n', '')
	loginInfo[1] = loginInfo[1].replace('\n', '')

	r = praw.Reddit('/u/PlayStoreLinks_Bot by /u/cris9696')
	r.login(loginInfo[0], loginInfo[1])
	subreddit = r.get_subreddit('cris9696+AndroidGaming+AndroidQuestions+Android+AndroidUsers+twitaaa+AndroidApps+AndroidThemes+harley+supermoto+bikebuilders+careerguidance+mentalfloss+nexus7+redditsync+nexus5+tasker')   #which subreddits i need to work on?
	#subreddit = r.get_subreddit('cris9696')   #debug
except Exception as e:
	log("Exception occured on login: " + str(e))
	exitBot()

log("Logging in succesfull")

regex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|$)",re.M)   #my regex
regexCategory = re.compile("\\blink[\s]*me[\s]*category[\s]*:[\s]*(.*?)(?:\.|$)",re.M)   #my regex
#regex = re.compile("\\blink[\s]*medebug[\s]*:[\s]*(.*?)(?:\.|$)",re.M)   #my debug regex



###############################COMMENTS CACHE to avoid analyzing already done comments###########################################
already_done = []  #the array filled with entries i already analized
if(os.path.isfile(cacheFile)):
	f = open(cacheFile, 'r+') #my cache
	if f.tell() != os.fstat(f.fileno()).st_size:   #if the file isn't at its end or empty
		already_done = pickle.load(f)
	f.close()
f = open(cacheFile, 'w+')


###############################LINKS CACHE to avoid useless search requests############################################
nameLinkDict = dict()
if(os.path.isfile(dbFile)):
	fi = open(dbFile, 'r+') #my cache for links
	if fi.tell() != os.fstat(fi.fileno()).st_size:   #if the file isn't at its end or empty
		nameLinkDict = pickle.load(fi)
	fi.close()
fi = open(dbFile, 'w+')




#######################################################################################
fileOpened = True

try:	#i try to get the comments
	log("Getting the comments")
	subreddit_comments = subreddit.get_comments()  
except Exception as e:
	log("Exception occured while gettin the comments: " + str(e))
	exitBot()

log("Comments OK")
try:		
	for comment in subreddit_comments: #for each comment in the subreddit
		alreadyAnswered = False
		generatedComment = ""

		normalMatches = regex.findall(comment.body.lower().replace("*","").replace("~~","").replace("^",""))   #i get the regex match
		categoryMatches = regexCategory.findall(comment.body.lower().replace("*","").replace("~~","").replace("^",""))   #i get the regex match
		
		if len(categoryMatches)>0:
			alreadyAnswered = isDone(comment)
			generatedComment = ""
			if not alreadyAnswered: #i need to answer
				for match in categoryMatches:
					match = match.split(",") #split the match.
					for app in match:
						toAdd = generateCategory(app)
						if toAdd is not False:
							generatedComment += toAdd
				if len(generatedComment)>0:
					reply(generatedComment,comment)

		elif len(normalMatches)>0:  #if it is something (aka valid comment)
			alreadyAnswered = isDone(comment)
			if not alreadyAnswered: #i need to answer
				nFound = 0
				i = 0
				for match in normalMatches:
					match = match.split(",") #split the match.
					if len(match)>10 :
						generatedComment += "You requested more than 10 apps. I will only link to the first 10.\n\n"
						log ("More than 10 apps found in a comment")

					for app in match:  #foreach app
						if i<10:
							ind = app.find('.') #i check if i need to remove a dot
							if ind!=-1:
								app = app[:ind]
							if len(app.strip()) > 0:
								toAdd = generateComment(app)   #i generate the comment
								if toAdd is not False:
									generatedComment += toAdd
									nFound = nFound+1
								else:
									generatedComment += "I am sorry, I can't find " + app.title() + ". \n\n"
								i = i+1
						else:
							break
				if nFound > 0:
					reply(generatedComment,comment)
except Exception as e:
	log ("Exception occured in the main try-catch: " + str(e))

exitBot()


	
	

	