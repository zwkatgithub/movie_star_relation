import pymysql

class Sql:

    def __init__(self, ip, username, password, db):
        self.db = pymysql.connect(
            ip, username, password, db
        )
        self.cursor = self.db.cursor()
    def commit(self):
        self.db.commit()
    def rollback(self):
        self.db.rollback()

db = Sql("localhost", "learn", "123456", "ms")