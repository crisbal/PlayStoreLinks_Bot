import pickle
import os
dbFile = "db" + "7"

nameLinkDict = dict()
if(os.path.isfile(dbFile)):
	fi = open(dbFile, 'r+') #my cache for links
	if fi.tell() != os.fstat(fi.fileno()).st_size:   #if the file isn't at its end
		nameLinkDict = pickle.load(fi)
	fi.close()
fi = open(dbFile, 'w+')


appName = ".."
while appName != "0":
	appName = str(raw_input("Search Term (0 to exit): ").lower().strip())
	if appName != "0":
		if appName in nameLinkDict:
			print(appName + " found in cache: " + nameLinkDict[appName])
			if raw_input("Do you want to edit the link? (y/n)").lower() == "y":
				nameLinkDict[appName] = raw_input("New link: ").lower().strip()
		else:
			nameLinkDict[appName] = raw_input("Link for " + appName + ": ").lower().strip()

pickle.dump(nameLinkDict, fi)
fi.close()
