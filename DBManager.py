from AppDB import AppDB


def list_all():
    apps = AppDB.select()
    for app in apps:
        print("    " + app.fullName + " - " + app.searchName)

    print("Total of " + str(apps.count()) + " apps.")

def search_edit_app():
    search_type = int(input("Search by link(1), fullName(2), searchName(3), back(0)"))
    if search_type == 0:
        return
    else:
        if search_type == 1:
            link = input("App link: ")
            app = AppDB.

while True:

    print("1) List all apps")
    print("2) Search/Edit an app")
    print("0) Exit")

    choice = int(input('Choice: '))
    print("")
    if choice < 0 or choice > 3:
        print ("Wrong Choice!")
    else:
        if choice == 0:
            break
        elif choice == 1:
            list_all()
        elif choice == 2:
            search_edit_app()
            


    print("\n\n")


