import contextlib
import secrets
import sqlite3
import time

import requests


def create_user(url, headers, username, realname, email, password):
    data = {
        'approved': True,
        'active': True,
        'name': realname,
        'username': username,
        'email': email,
        'password': password
    }

    while True:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 429:
            wait = int(response.headers['Retry-After'])
            print(f"retrying in {wait}s")
            time.sleep(wait)
            continue
        elif not response.ok:
            continue

        r = response.json()

        if r['success'] != True:
#            print(r)
            print('failed')
            break

        print('ok')
        break


def run():

    url = 'https://forum.vassalengine.org/users.json'

    headers = {
        'Api-Key': '',
        'Api-Username': 'system'
    }

    dbpath = 'projects.db'

    with contextlib.closing(sqlite3.connect(dbpath)) as conn:
        with conn as cur:
            rows = cur.execute('SELECT username, realname, email FROM users_w WHERE matched = 0 AND email IS NOT NULL AND email != "" AND realname IS NOT NULL AND realname != "" AND username IS NOT NULL AND username != ""')
            for row in rows:
                print(row, end=' ')
                create_user(url, headers, *row, secrets.token_urlsafe(20))


if __name__ == '__main__':
    run()
