import json
import os
import requests

# set path
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DIST_PATH = os.path.join(ROOT_PATH, 'dist')


def create_package_infos():
    print('create packages infos...')
    packages_infos_path = os.path.join(DIST_PATH, 'packages', 'infos')
    r = requests.get('https://api.github.com/orgs/Modular-Life-Assistant/repos')
    for repo in r.json():
        if repo['name'].lower().endswith('module'):
            # set default value (editable value)
            name = ' '.join(repo['name'].split('-')[1:-1])
            package = {
                'package_name': name,
                'name': name.replace('_', ' ').capitalize(),
                'description': repo['description'],
                'issues_url': repo['html_url'] + '/issues',
                'url': repo['homepage'] or repo['html_url'],
                'modules_required': [],
                'modules_optional': [],
            }

            # update value from infos.json (in module)
            info = requests.get(
                'https://raw.githubusercontent.com/'
                '%(full_name)s/%(default_branch)s/infos.json' % repo
            )

            if info:
                info = info.json()
                for index in list(package):
                    package[index] = info.get(index, package[index])

            # none editable value
            package['github_id'] = repo['id']

            # save
            path = os.path.join(packages_infos_path,
                                '%s.json' % package['package_name'])
            with open(path, 'w') as f:
                json.dump(package, f, indent=2)


def build_list(dir_name):
    print('build list of %s ...' % dir_name)
    item_list = []
    list_path = os.path.join(DIST_PATH, dir_name, 'list.json')
    infos_path = os.path.join(DIST_PATH, dir_name, 'infos')
    for file_name in sorted(os.listdir(infos_path)):
        # set default value
        name = file_name.replace('.json', '')
        item = {
            '%s_name' % dir_name[:-1]: name,
            'name': name.replace('_', ' ').capitalize(),
            'description': '',
            'issues_url': '',
            'url': '',
            'modules_required': [],
            'modules_optional': [],
        }

        # update value
        with open(os.path.join(infos_path, file_name)) as f:
            item.update(json.load(f))

        item_list.append(item)

    # save build (projects)
    with open(list_path, 'w') as f:
        json.dump({
            dir_name: item_list,
        }, f, indent=2)
        print('%d %s' % (len(item_list), dir_name))

create_package_infos()
build_list('packages')
build_list('projects')