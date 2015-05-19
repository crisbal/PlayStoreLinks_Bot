##[PlayStoreLinks__Bot](http://www.reddit.com/u/PlayStoreLinks__Bot)


A Reddit bot that links to Android Apps from the Play Store when a user asks to do it.


####What's included

* LinkMeBot.py, the main program
* App.py, a class that the bot uses to save data
* AppDB.py, a class used to save data to the database
* Config.py, a simple and easy to understand configuration file
* Test.py, a simple test to see if the Play Store parsing works.
* setup.py, something you need to run before running the bot the first time / applying updates
* requirements.txt, the pip modules you need to install to run the bot
* LICENSE, the license that this project is released under (MIT)
* README, this file


####What you need to know before editing this bot / running it on your local machine

The bot was written on a Linux-Fedora machine with Python 2.7.5

See required packages in requirements.txt

You need to set a valid username and password in the config file
Also in the config file you need to set the subreddits where the bot searches for comments

####How to use it

On the server I use the bot is set to run every two minutes using a cronjob
If you want to test the code I suggest you to post a comment in a subreddit and then run the bot, after configuring it.


####Info / Reddit-related questions / See the bot in action

http://www.reddit.com/r/cris9696

Feel free to make a new post if  you want to test the bot, or just use an existing one.


####TODO

* Autodelete
* Better Code (Separate module for Play Store stuff)


####Want to help or want help?

* If you want to help please feel free to do it.

* If you need help please fell free to ask me.

* If you find any bug or exploit please tell me: I will try to fix them or if you want you can fix them and I will include your changes in the project.
* If you find a way to improve the bot, please share it with everybody.

####LICENSE

MIT License

