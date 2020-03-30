#!/usr/bin/env python3

import argparse
import json
import requests
import logging
import sys, os


logger = None
args = None
params = {}
api_url_get_release_id = 'https://api.github.com/repos/{}/{}/releases/tags/{}'
api_url_delete_release = 'https://api.github.com/repos/{}/{}/releases/{}'
api_url_delete_tag = 'https://api.github.com/repos/{}/{}/git/refs/tags/{}'
api_url_get_repo_info = 'https://api.github.com/repos/{}/{}'

def parseArgs():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_name", help="Github owner name")
    parser.add_argument("repo_name", help="Github repository name")
    parser.add_argument("tag_name", help="Tag name of existing release")
    parser.add_argument("api_token", help="Github API token with necessary privilages")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    params["tag_name"] = args.tag_name
    params["api_token"] = args.api_token
    params["user"] = args.owner_name
    params["repo_name"] = args.repo_name
    params["headers"] = {'Authorization': 'token {}'.format(params["api_token"])}


def setupLogger():
    global logger
    logger = logging.getLogger('GitHubHoping')
    ch = logging.StreamHandler()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s [%(lineno)d]- %(levelname)s: %(message)s')
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')

    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug("verbosity turned on")
    logger.debug(args)

def doesRepoExist():
    r = requests.get(url = api_url_get_repo_info.format(params["user"], params["repo_name"]), headers = params["headers"])
    if r.status_code == 200:
        logger.debug("Repository exists:'http://github.com{}/{}'".format(params["user"], params["repo_name"]))
    else:
        logger.error("Repository doesn't exist:'http://github.com{}/{}'".format(params["user"], params["repo_name"]))
        sys.exit(os.EX_CONFIG)

def getReleaseId():
    r = requests.get(url = api_url_get_release_id.format(params["user"], params["repo_name"], params["tag_name"]), headers = params["headers"])
    if r.status_code == 200:
        release_id = r.json()['id']
        logger.debug("Release id:'{}'".format(release_id))
        return release_id
    elif r.status_code == 401:
        logger.error("Unauthorized")
        sys.exit(os.EX_CONFIG)
    else:
        logger.info("Release with a tag name:'{}' doesn't exist".format(params["tag_name"]))
        return 0

def deleteTag():
    r = requests.delete(url = api_url_delete_tag.format(params["user"], params["repo_name"], params["tag_name"]), headers = params["headers"])
    if r.status_code == 204:
        logger.info("Tag '{}' has been deleted".format(params["tag_name"]))
    else:
        logger.error("Tag '{}' can't be deleted, error code: {}".format(params["tag_name"], r.status_coce))
        sys.exit(os.EX_SOFTWARE)

def deleteRelease(release_id):
    r = requests.delete(url = api_url_delete_release.format(params["user"], params["repo_name"], release_id), headers = params["headers"])
    if r.status_code == 204:
        logger.info("Release with tag '{}' has been deleted".format(params["tag_name"]))
    else:
        logger.error("Release with Tag '{}' can't be deleted, error code: {}".format(params["tag_name"], r.status_coce))
        sys.exit(os.EX_SOFTWARE)

def deleteReleaseAndTag():
    doesRepoExist()
    release_id = getReleaseId()
    if release_id != 0:
        deleteRelease(release_id)
        deleteTag()

def main():
    parseArgs()
    setupLogger()
    deleteReleaseAndTag()

main()

