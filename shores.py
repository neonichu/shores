#!/usr/bin/env python

import ConfigParser
import cPickle
import os
import sys
import urllib
import urlparse

from BeautifulSoup import BeautifulSoup as bsoup
from feedparser import parse as rssparse
from watchedli import WatchedLi


BASE_URL = 'http://showrss.karmorra.info/?cs=feeds'
FEED_URL = 'http://showrss.karmorra.info/feeds/%s.rss'
CFG_DIR = os.path.expandvars('$HOME/.shores')

CACHE_FILE = os.path.join(CFG_DIR, 'cache')
CFG_FILE = os.path.join(CFG_DIR, 'config')


def dlfile(link, targetDir):
    url = urlparse.urlparse(link)
    path = os.path.join(targetDir, os.path.basename(url[2]))
    if os.path.exists(path):
        return False
    u = urllib.urlopen(link)
    torrent = u.read()
    f = file(path, 'wb')
    f.write(torrent)
    f.close()
    return True


def list_shows():
    result = []
    try:
        inputFP = urllib.urlopen(BASE_URL)
    except Exception, e:
        print e
        return result
    for option in bsoup(inputFP)('option'):
        optContents = ''.join(option.contents)
        optValue = option['value']
        if optValue.isnumeric():
            result.append({optContents: optValue})
    inputFP.close()
    return result


def is_in_cache(cache, key, element):
    if cache.has_key(key):
        return element in cache[key]
    return False


def store_in_cache(cache, key, element):
    if not cache.has_key(key):
        cache[key] = []
    cache[key].append(element)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    inputFP = file(CACHE_FILE)
    result = cPickle.load(inputFP)
    inputFP.close()
    return result


def store_cache(to_cache):
    outputFP = file(CACHE_FILE, 'w')
    cPickle.dump(to_cache, outputFP)
    outputFP.close()


def handle_feed(feed_url, cache, feed_id):
    inputFP = urllib.urlopen(feed_url)
    for item in rssparse(inputFP)['entries']:
        for link in item['links']:
            linked = link['href']
            if not is_in_cache(cache, feed_id, linked):
                try:
                    if dlfile(linked):
                        store_in_cache(cache, feed_id, linked)
                        print 'Fetched torrent file "%s".' % linked
                except Exception, e:
                    print e
    inputFP.close()


def handle_show(showName, listOfShows):
    for show in listOfShows:
        curShowName = show.keys()[0]
        if curShowName.lower() == showName.lower():
            print 'Found matching show "%s".' % curShowName
            handle_feed(FEED_URL % show[curShowName], cache, curShowName)
            store_cache(cache)
            return
    print 'Show "%s" does not exist.' % showName


if __name__ == '__main__':
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)

        dummy_config = file(CFG_FILE, 'w')
        dummy_config.write('[shores]\ntargetDir = %s' % os.path.expandvars('$HOME'))
        dummy_config.close()

    config = ConfigParser.ConfigParser()
    config.read(CFG_FILE)

    targetDir = config.get('shores', 'targetDir')

    cache = load_cache()
    listOfShows = list_shows()

    if len(sys.argv) == 1:
        try:
            watchedLiUser = config.get('shores', 'watchedLiUser')
            watchedLiPass = config.get('shores', 'watchedLiPass')

            watched = WatchedLi(watchedLiUser, watchedLiPass)
            for show in watched.shows():
                handle_show(show, listOfShows)
        except:
            print 'Available shows:'
            for show in listOfShows:
                print '\t%s' % show.keys()[0]
    else:
        showName = ' '.join(sys.argv[1:])
        handle_show(showName, listOfShows)
