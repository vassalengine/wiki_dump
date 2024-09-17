import json
import re
import urllib.parse

import semver


def try_semver(version):
    try:
        return semver.Version.parse(version)
    except ValueError:
        try:
            return semver.Version.parse(version + '.0')
        except ValueError:
            try:
                return semver.Version.parse(version + '.0.0')
            except ValueError:
                return None


def try_parse_version(version):
    # First, strip spaces
    base = version.strip()
    if len(base) <= 0:
        return None

    # Pre-release defaults to empty
    pre  = ''

    # Strip leading stuff which isn't a number
    m = re.match(r'(^[^-0-9._]*) *(.*)', base)
    if m is not None and len(m.groups()) >= 1:
#        pre = ('-' + m[1].strip().replace('-', '')) if len(m[1]) > 0 else ''
        base = m[2].strip()

    # Then see if we have a leading "version"
    m = re.match(r'(v|version|ver) *([-0-9._ ]+.*)', base, re.IGNORECASE)
    if m is not None and len(m.groups()) > 1:
        base = m[2].strip()

    # Replace '-', '_', and ',' with '.', and strip leading/trailing whitespace
    base = base.replace('_', '.').replace('-', '.').replace(',', '.').strip()

    # See if we have something that looks like a release
    m = re.match(r'([-0-9.]+)([^0-9.]+.*)', base)
    if m is not None and len(m.groups()) > 1:
        base = m[1].replace(' ', '_')
        pre = '-' + m[2].strip().replace('-','')

    # If the first character is a dot, prepend a zero
    if base.startswith('.'):
        base = '0' + base

    # Now remove '.0' from string.
    while True:
        m = re.match(r'(.*)\.0(.*)', base)
        if m is None:
            break
        base = '.'.join(m.groups())
        #print('->',base)

    # Remove leading and trailing dots,
    # replace double dots with a 0 inbetween
    base = base.strip('.')
    base = base.replace('..', '.0.')
    #print('=>',base)

    # Check how many dots we have and pad or remove as needed
    if base.count('.') >= 3:
        spl = base.split('.')
        #print('~',spl)
        pre  = '-' + '_'.join(spl[3:])
        base = '.'.join(spl[:3])
        #print('~~',base,pre)
    elif base.count('.') == 2:
        pass
    elif base.count('.') == 1:
        base += '.0'
    elif base.count('.') == 0:
        base += '.0.0'

    if len(pre) >= 30:
        pre = ''
    elif pre:
        pre = pre.replace(' ', '').replace('(', '').replace(')', '').replace('+', '').replace('_', '')

    # Form our final estimate
    test = base + pre

    if v := try_semver(test):
        return v

    return None


def run():
    mpath = 'data/file_meta'
    opath = 'data/file_meta.json'

    meta = {}

    with open(mpath, 'r') as f:
        for line in f:

            url, size, sha256, version = line.split('\t')

            url = url.strip()
            rest, filename = url.rsplit('/', maxsplit=1)
            filename = urllib.parse.quote(filename)
            url = f"{rest}/{filename}"

            version = version.strip()
            v = try_parse_version(version)

            rec = {
                'size': size,
                'sha256': sha256,
                'version': version
            }

            if v is not None:
                rec['version_parsed'] = (
                    v.major,
                    v.minor,
                    v.patch,
                    v.prerelease,
                    v.build
                )

            meta[url] = rec

    with open(opath, 'w') as f:
        json.dump(meta, f, indent=2)


if __name__ == '__main__':
    run()
