#!/usr/bin/env python

from __future__ import print_function

import os
import re
import subprocess
from distutils.version import LooseVersion
from shutil import rmtree


# Gets the location of Homebrew
BREW_LOCATION = subprocess.check_output(['which', 'brew'])[:-9]
INSTALLED_PATH = BREW_LOCATION + 'Caskroom'
METADATA_PATHS = [
    BREW_LOCATION + 'Homebrew/Library/Taps/caskroom/homebrew-cask/Casks',
    BREW_LOCATION + 'Homebrew/Library/Taps/caskroom/homebrew-versions/Casks',
]


# Main method
def main():
    check_folders_exist()
    updates_required = False
    for application in os.listdir(INSTALLED_PATH):
        if not os.path.isdir(os.path.join(INSTALLED_PATH, application)):
            continue

        latest_installed_version, old_installed_versions = get_installed_versions(application)

        if not latest_installed_version:
            updates_required = True
            continue

        latest_version = get_latest_version(application)

        if not latest_version:
            continue

        if latest_version > latest_installed_version:
            print('{} is outdated:'.format(application))
            print('- Installed version: {}'.format(latest_installed_version))
            print('- Latest version: {}'.format(latest_version))
            subprocess.call(['brew', 'cask', 'install', '--force', application])
            latest_installed_version, old_installed_versions = get_installed_versions(application)
        if old_installed_versions:
            for version in versions:
                rmtree(os.path.join(INSTALLED_PATH, application, version.vstring))

    if not updates_required:
        print('All casks are currently up to date.')


# Checks if Homebrew Cask is installed
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


# Gets the currently installed versions of the application
def get_installed_versions(application):
    versions = os.listdir(os.path.join(INSTALLED_PATH, application))
    versions = [LooseVersion(version) for version in versions if version != '.metadata']

    if versions:
        versions.sort(reverse=True)
        return versions[0], versions[1:]

    return False, False


# Gets the latest version of the application
def get_latest_version(application):
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

        return latest_version

    return False


# Calls main method
if __name__ == '__main__':
    main()
