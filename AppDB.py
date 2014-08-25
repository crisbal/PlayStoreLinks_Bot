from peewee import *


db = SqliteDatabase('LinkMeBot.db')

class AppDB(Model):
    fullName = CharField()
    link = CharField(unique=True)
    searchName = CharField()
    rating = CharField()
    free = BooleanField()
    iap = BooleanField(null = True)

    class Meta:
        database = db
        indexes = (
            (('fullName', 'link', 'searchName'), True),
        )