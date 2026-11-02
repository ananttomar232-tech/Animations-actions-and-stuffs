"""Prints the command line the vanilla launcher would use for an installed Forge profile, one argument per line.

    python3 forge_launch.py <minecraft dir> <forge version id> <game dir> <assets dir> [extra JVM args...]

The Forge installer (--installClient) writes the Forge profile and libraries, but not the vanilla version JSON or
the vanilla libraries; those are fetched from Mojang here, as the launcher would. Used by run_production_client.sh.
"""
import json
import os
import sys
import urllib.request

MANIFEST = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'


def main():
    mc, version, game_dir, assets = sys.argv[1:5]
    extra_jvm = sys.argv[5:]
    lib = os.path.join(mc, 'libraries')

    def load(v):
        path = os.path.join(mc, 'versions', v, v + '.json')
        if not os.path.exists(path):
            manifest = json.load(urllib.request.urlopen(MANIFEST))
            url = next(x['url'] for x in manifest['versions'] if x['id'] == v)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(urllib.request.urlopen(url).read())
        with open(path) as f:
            return json.load(f)

    def allowed(rules):
        if not rules:
            return True
        ok = False
        for r in rules:
            os_rule = r.get('os')
            match = (os_rule is None or os_rule.get('name') == 'linux') and 'features' not in r
            if match:
                ok = r['action'] == 'allow'
        return ok

    def fetch(artifact):
        dst = os.path.join(lib, artifact['path'])
        if not os.path.exists(dst) and artifact.get('url'):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as f:
                f.write(urllib.request.urlopen(artifact['url']).read())
        return dst

    child = load(version)
    parent = load(child['inheritsFrom'])
    classpath = []
    for d in (child, parent):
        for library in d['libraries']:
            artifact = library.get('downloads', {}).get('artifact')
            if artifact and allowed(library.get('rules')):
                path = fetch(artifact)
                if path not in classpath:
                    classpath.append(path)
    # The launcher would add versions/<forge id>/<forge id>.jar, which FML ignores; the vanilla jar must not be added.
    sub = {'${library_directory}': lib, '${classpath_separator}': ':', '${version_name}': version,
           '${natives_directory}': os.path.join(mc, 'natives'), '${launcher_name}': 'motionworks-test',
           '${launcher_version}': '1', '${classpath}': ':'.join(classpath)}

    def s(a):
        for k, v in sub.items():
            a = a.replace(k, v)
        return a

    jvm = ['-Xmx3G', '-Djava.library.path=' + sub['${natives_directory}'], '-cp', sub['${classpath}']] + extra_jvm
    jvm += [s(a) for a in child['arguments']['jvm'] if isinstance(a, str)]
    game = ['--username', 'Tester', '--version', version, '--gameDir', game_dir, '--assetsDir', assets,
            '--assetIndex', parent['assetIndex']['id'], '--uuid', '00000000000000000000000000000001',
            '--accessToken', '0', '--userType', 'legacy', '--versionType', 'release']
    game += [s(a) for a in child['arguments']['game'] if isinstance(a, str)]
    print('\n'.join(jvm + [child['mainClass']] + game))


if __name__ == '__main__':
    main()
