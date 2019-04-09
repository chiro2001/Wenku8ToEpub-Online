import copy
import hashlib
import json
import os
import time


class DataBase:
    def __init__(self):
        self.file_db_init = "db_init.sql"

        self.tables = ['go', ]

        self.opposite = {
            0: 0,
            1: 2,
            2: 1,
        }

        # self.sql_type = "PostgreSQL"
        self.sql_types = {"SQLite": 0, "PostgreSQL": 1}
        # self.sql_type = self.sql_types['PostgreSQL']
        # self.sql_type = self.sql_types['SQLite']
        if os.environ.get('PORT', '5000') == '5000':
            # Local
            self.sql_type = self.sql_types['SQLite']
        else:
            # Remote
            self.sql_type = self.sql_types['PostgreSQL']
        self.sql_chars = ["?", "%s"]
        self.sql_char = self.sql_chars[self.sql_type]

        self.connect_init()

    def v(self, string: str):
        return string.replace('%s', self.sql_char)

    def make_result(self, code, **args):
        result = {
            "code": int(code),
            "data": args
        }
        return json.dumps(result)

    def connect_init(self):
        if self.sql_type == self.sql_types['SQLite']:
            import sqlite3 as sql
            self.conn = sql.connect('data_sql.db', check_same_thread=False)
        else:
            import psycopg2 as sql
            self.conn = sql.connect(host='ec2-50-17-246-114.compute-1.amazonaws.com',
                                    database='de5kjan1c7bsh8',
                                    user='fhvsqdrzvqgsww',
                                    port='5432',
                                    password='2fe833a144e72ffd656e1adc4ea49ad0571d329ecfa83c51c03c187df0b35152')

    def cursor_get(self):
        cursor = self.conn.cursor()
        return cursor

    def cursor_finish(self, cursor):
        self.conn.commit()
        cursor.close()

    def db_init(self):
        try:
            cursor = self.cursor_get()
            for table in self.tables:
                try:
                    cursor.execute("DROP TABLE IF EXISTS %s" % table)
                except Exception as e:
                    print('Error when dropping:', table, '\nException:\n', e)
                    self.cursor_finish(cursor)
                    cursor = self.cursor_get()
            self.cursor_finish(cursor)
        except Exception as e:
            print(e)
        self.conn.close()
        self.connect_init()
        cursor = self.cursor_get()
        # 一次只能执行一个语句。需要分割。而且中间居然不能有空语句。。
        with open(self.file_db_init, encoding='utf8') as f:
            string = f.read()
            for s in string.split(';'):
                try:
                    if s != '':
                        cursor.execute(s)
                except Exception as e:
                    print('Error:\n', s, 'Exception:\n', e)
        self.cursor_finish(cursor)

    def write(self, code: str, player: int, data_str: str, winner: int=0):
        cursor = self.cursor_get()
        cursor.execute(self.v("SELECT code FROM go WHERE code = %s"), (code, ))
        data = cursor.fetchall()
        if len(data) == 0:
            cursor.execute(self.v("INSERT INTO go (code, status, data, uptime, winner) VALUES (%s, %s, %s, %s, %s)"),
                           (code, self.opposite[player], data_str, int(time.time()), 0))
            self.cursor_finish(cursor)
        else:
            cursor.execute(self.v("UPDATE go SET status = %s, data = %s, uptime = %s, winner = %s WHERE code = %s"),
                           (self.opposite[player], data_str, int(time.time()), winner, code))
            self.cursor_finish(cursor)

        return self.make_result(0)

    def read(self, code):
        cursor = self.cursor_get()
        cursor.execute(self.v("SELECT status, data, uptime, winner FROM go WHERE code = %s"), (code, ))
        data = cursor.fetchall()
        self.cursor_finish(cursor)
        if len(data) == 0:
            return {
                "code": code,
                "status": 0,
                "data": '',
                "uptime": 0,
                "winner": 0,
                "error": "No such of code."
            }
        data = data[0]
        return {
            "code": code,
            "status": data[0],
            "data": data[1],
            "uptime": data[2],
            "winner": data[3],
        }


def jsonify(string: str):
    return json.loads(string)


if __name__ == '__main__':
    db = DataBase()
    db.db_init()
    print(db.opposite[0])
    db.write('code', 1, '0000\n0000\n0000\n0000', 0)
    print(db.read('code'))
    db.write('code', 1, '0000\n0010\n0000\n0000', 0)
    print(db.read('code'))


