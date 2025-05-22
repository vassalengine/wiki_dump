import json

import requests


def run():
    url = 'https://forum.vassalengine.org/admin/users/list/new.json'

    headers = {
        'Api-Key': 'f3692d76322a3f32f31c19400e26e20230d95b144287a7fab4481faa281ec6cb',
        'Api-Username': 'system'
    }

    s = requests.Session()
    retries = requests.adapters.Retry(total=5, backoff_factor=1)
    s.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

    with open('data/users.json', 'w') as f:
        print('[', file=f)

        first = True

        page = 1
        while True:
            params = {
                'page': page,
                'show_emails': 'true'
            }
            response = s.get(url, params=params, headers=headers)
            response.raise_for_status()

            r = response.json()

            if not r['users']:
                break

            for u in r['users']:
                if first:
                    first = False
                else:
                    print(',', file=f)

                json.dump(u, f)

            print(page)
            page += 1

        print(']', file=f)

if __name__ == '__main__':
    run()
