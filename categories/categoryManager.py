#this is used to manage categories files, you neeed a name for the file (that will  be opened in the app) and all the apps you want to add

import pickle
import os


catFile = raw_input("Category file to manage: ")
catDict = dict()

if(os.path.isfile(catFile)):
	fi = open(catFile, 'r+') #my cache for links
	if fi.tell() != os.fstat(fi.fileno()).st_size:   #if the file isn't at its end
		catDict = pickle.load(fi)
	fi.close()
fi = open(catFile, 'w+')


appName = ".."
while appName != "0":
	appName = str(raw_input("App name(0 to exit): ").lower().strip())
	if appName != "0":
		if appName in catDict:
			print(appName + " found in cache: " + catDict[appName])
			if raw_input("Do you want to edit the link? (y/n)").lower() == "y":
				catDict[appName] = raw_input("New link: ").lower().strip()
		else:
			catDict[appName] = raw_input("Link for " + appName + ": ").lower().strip()

pickle.dump(catDict, fi)
fi.close()

