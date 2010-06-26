#!/usr/bin/env python

import cPickle, os, sys
import urllib, urlparse

from BeautifulSoup import BeautifulSoup as bsoup
from feedparser import parse as rssparse


BASE_URL = 'http://showrss.karmorra.info/?cs=feeds'
FEED_URL = 'http://showrss.karmorra.info/feeds/%s.rss'
CACHE_FILE = os.path.expandvars('$HOME/.shores')
TARGET_DIR = '.'


def dlfile(link):
	url = urlparse.urlparse(link)
	path = os.path.join(TARGET_DIR, os.path.basename(url[2]))
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
	inputFP = urllib.urlopen(BASE_URL)
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


if __name__ == '__main__':
	cache = load_cache()

	if len(sys.argv) == 1:
		print 'Available shows:'
		for show in list_shows():
			print '\t%s' % show.keys()[0]
	else:
		showName = ' '.join(sys.argv[1:])
		for show in list_shows():
			curShowName = show.keys()[0]
			if curShowName.lower() == showName.lower():
				print 'Found matching show "%s".' % curShowName
				inputFP = urllib.urlopen(FEED_URL % show[curShowName])
				for item in rssparse(inputFP)['entries']:
					for link in item['links']:
						linked = link['href']
						if not is_in_cache(cache, curShowName, linked):
							if dlfile(linked):
								store_in_cache(cache, curShowName, linked)
								print 'Fetched torrent file "%s".' % linked
				inputFP.close()
				store_cache(cache)
				sys.exit(0)
		print 'Show "%s" does not exist.' % showName
