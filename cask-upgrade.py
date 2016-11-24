#!/usr/bin/env python

from __future__ import print_function

import os
import re
import subprocess
from distutils.version import LooseVersion
from shutil import rmtree


INSTALLED_PATH = '/usr/local/Caskroom'
METADATA_PATHS = [
    '/usr/local/Homebrew/Library/Taps/caskroom/homebrew-cask/Casks',
    '/usr/local/Homebrew/Library/Taps/caskroom/homebrew-versions/Casks',
]


def main():
    check_folders_exist()
    for application in os.listdir(INSTALLED_PATH):
        if not os.path.isdir(os.path.join(INSTALLED_PATH, application)):
            continue

        latest_installed_version, old_installed_versions = get_installed_versions(application)

        if not latest_installed_version:
            continue

        latest_version, auto_updates = get_latest_version_and_auto_update(application)

        if not latest_version:
            continue

        if latest_version > latest_installed_version:
            print('{} is outdated:'.format(application))
            print('- Installed version: {}'.format(latest_installed_version))
            print('- Latest version: {}'.format(latest_version))

            if auto_updates:
                print('Note: {} may have auto updated to the latest version'.format(application))

            if confirmed('Upgrade? '):
                print()
                upgrade(application)
                latest_installed_version, old_installed_versions = get_installed_versions(application)

            print()

        if old_installed_versions:
            print('{} has old versions installed:'.format(application))
            for version in old_installed_versions:
                print('- {}'.format(version))

            if confirmed('Remove? '):
                remove_old_versions(application, old_installed_versions)

            print()


def check_folders_exist():
    if not os.path.isdir(INSTALLED_PATH):
        print('Error: {} does not exist, are you sure Homebrew-Cask is installed?'.format(INSTALLED_PATH))
        exit(1)

    if not os.path.isdir(METADATA_PATHS[0]):
        print('Error: {} does not exist, are you sure Homebrew-Cask is installed?'.format(METADATA_PATHS[0]))
        exit(1)

    for path in METADATA_PATHS[1:]:
        if not os.path.isdir(path):
            METADATA_PATHS.remove(path)


def get_installed_versions(application):
    versions = os.listdir(os.path.join(INSTALLED_PATH, application))
    versions = [LooseVersion(version) for version in versions if version != '.metadata']

    if versions:
        versions.sort(reverse=True)
        return versions[0], versions[1:]

    return False, False


def get_latest_version_and_auto_update(application):
    for directory in METADATA_PATHS:
        metadata_path = os.path.join(directory, '{}.rb'.format(application))
        if not os.path.isfile(metadata_path):
            continue

        with open(metadata_path, 'r') as metadata_file:
            metadata = metadata_file.read()

        versions = re.findall(r'^\W*version (\S+)', metadata, re.MULTILINE)
        if not versions:
            continue

        latest_version = None
        for version in versions:
            version = LooseVersion(version.strip('\'":'))

            if version.vstring == 'latest':
                latest_version = version
                break

            if not latest_version or version > latest_version:
                latest_version = version

        auto_updates = re.search(r'^\W*auto_updates true\W', metadata, re.MULTILINE)

        return latest_version, bool(auto_updates)

    return False, False


def confirmed(message):
    try:
        # Python 2
        ask = raw_input
    except NameError:
        # Python 3
        ask = input

    while True:
        response = ask(message).strip().lower()

        if response in {'y', 'yes'}:
            return True
        elif response in {'n', 'no'}:
            return False


def upgrade(application):
    # --force is needed after homebrew-cask started moving apps to /Applications
    subprocess.call(['brew', 'cask', 'install', '--force', application])


def remove_old_versions(application, versions):
    for version in versions:
        rmtree(os.path.join(INSTALLED_PATH, application, version.vstring))


if __name__ == '__main__':
    main()
