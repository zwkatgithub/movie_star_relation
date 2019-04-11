import pymysql

class Sql:

    def __init__(self, ip, username, password, db):
        self.db = pymysql.connect(
            ip, username, password, db
        )
        self.cursor = self.db.cursor()

db = Sql("localhost", "learn", "zwk19950102", "ms")