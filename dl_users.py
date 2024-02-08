import json

import requests


def run():
    url = 'https://forum.vassalengine.org/admin/users/list/new.json'

    headers = {
        'Api-Key': 'f3692d76322a3f32f31c19400e26e20230d95b144287a7fab4481faa281ec6cb',
        'Api-Username': 'system'
    }

    users = []

    s = requests.Session()
    retries = requests.adapters.Retry(total=5, backoff_factor=1)
    s.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

    page = 1
    while True:
        params = {
            'page': page,
            'show_emails': 'true'
        }
        response = s.get(url, params=params, headers=headers)
        r = response.json()

        if not r:
            break

        users += r

        print(page)
        page += 1
    
        
    with open('data/users.json', 'w') as f:
        json.dump(users, f)


if __name__ == '__main__':
    run()
