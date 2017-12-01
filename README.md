## [PlayStoreLinks_Bot](http://www.reddit.com/u/PlayStoreLinks__Bot)

A Reddit bot that links to Android Apps from the Play Store when a user asks to do it.

The bot was written on an Arch Linux machine with Python 3, so you need Python 3 to run it. It runs on a Raspberry Pi with Debian.

#### Where to look

* `LinkMeBot/LinkMeBot.py`, the main script
* `LinkMeBot/RemoveBadComments.py`, the scripts that remove downvoted comments
* `LinkMeBot/Config.example.py`, an example configuration file
* `PlayStore/`, a module for searching the PlayStore
* `test/`, tests

#### How to run it

* `git clone` the project
* `cd PlayStoreLinks_Bot`
* `python3 -m venv venv`
	* this will create a virtual environment for the bot to run in
* `source venv/bin/activate`
	* activate the bot
* `pip install -r requirements.txt`
	* install requirements
* Create a [reddit app](http://reddit.com/prefs/apps) as script
* Set a valid `username`, `password`, `client_id`, `client_secret` in the `LinkMeBot/Config.py` file
* `python -m LinkMeBot.LinkMeBot`
	* You can run tests with `python -m unittest`

#### Info / Reddit-related questions / See the bot in action

http://www.reddit.com/r/cris9696

Feel free to make a new post if you want to test the bot

#### Want to help or want help?

* If you want to help please feel free to do it.
* If you need help please fell free to ask me.
* If you find any bug or exploit please tell me: I will try to fix them or if you want you can fix them and I will include your changes in the project.
* If you find a way to improve the bot, please share it with everybody.

#### LICENSE

MIT License

