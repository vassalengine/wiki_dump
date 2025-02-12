import glob
import json
import sys

import semver

import versions


def try_semver(v):
    try:
        v = '.'.join(str(int(p)) for p in v.split('.'))
        return versions.try_semver(v)
    except:
        return None


def run():
    ipath = sys.argv[1]

    recs = {}

    for f in glob.glob(f"{ipath}/[0-9]*.json"):
        with open(f, 'r') as j:
            p = json.load(j)

        proj = {
            'title': p['title'],
            'pkgs': {} 
        }

        for pkg, rels in p['modules'].items():
            for rel, files in rels.items():
                for f in files:
                    proj['pkgs'].setdefault(pkg, {}).setdefault(rel, []).append((f.get('version', None), f['filename']))

        recs[p['title']] = proj

    for t in sorted(recs.keys()):
        r = recs[t]
        print('')
        print(r['title'])
        for pn, pv in r['pkgs'].items():
            print(f"  {pn}")
#            for rn, rv in pv.items():
            for rn, rv in sorted(pv.items(), key=lambda x: versions.try_semver(x[0]), reverse=True):
                print(f"    {rn}")
                rv.sort(key=lambda x: x[1])
                rv.sort(key=lambda x: semver.Version.parse(x[0] or '0.0.0'), reverse=True)
                for m in rv: 
                    print(f"      {m}")

#        if (all(try_semver(s['name']) for s in r['secs']) or (len(r['secs']) == 1 and r['secs'][0]['name'] == 'Module')) and all(m[0] is not None for s in r['secs'] for m in s['files']) and all(len(set(m[0] for m in s['files'])) == len(s['files']) for s in r['secs']):
#            print(f"    \"{r['title']}\": collapse_pkgs,")
#        else:
#            print(f"    \"{r['title']}\": None,")


if __name__ == '__main__':
    run()
