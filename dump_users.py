import contextlib
import sqlite3
import json


def run():
    upath = 'data/users.json'
    dbpath = 'users.db'

    with open(upath, 'r') as f:
        users = json.load(f)

    with contextlib.closing(sqlite3.connect(dbpath)) as conn:
        with conn as cur:
            for u in users:
                print((u['id'], u['username'], u['avatar_template']))
                cur.execute('INSERT INTO users (user_id, username, avatar_template) VALUES(?, ?, ?)', (u['id'], u['username'], u['avatar_template']))


if __name__ == '__main__':
    run()
