#!/usr/bin/env python

##
# Watched.li "API" using some scraping.
##

import cookielib
import mechanize
import urllib
import urllib2

from BeautifulSoup import BeautifulSoup as soup

BASE_URL    = 'http://watched.li/index.php'
MARK_URL    = 'http://watched.li/following/markEpisode'
SHOW_URL    = 'http://watched.li/show/view/'
UNMARK_URL  = 'http://watched.li/following/unmarkEpisode'


class WatchedLi:
    def __init__(self, user, password):
        self.cookie_jar = cookielib.LWPCookieJar()

        self.browser = mechanize.Browser()
        self.browser.set_cookiejar(self.cookie_jar)

        self.browser.open(BASE_URL)
        self.browser.select_form(nr=1)
        self.browser.form['User[email]'] = user
        self.browser.form['User[pass0]'] = password
        self.browser.submit()

    def episode_action(self, url, episode_id):
        if type(episode_id) == dict:
            episode_id = episode_id['wid']

        self.post_request(url, {'episode_id': episode_id})
        return True

    def episodes(self, show_title):
        show_url = SHOW_URL + show_title.lower().replace(' ', '-')
        self.browser.open(show_url)

        show_html = soup(self.browser.response(), convertEntities=soup.HTML_ENTITIES)
        episodes = []
        for season in show_html('tr', {'class': 'episodes-list'}):
            for episode in season('td'):
                if not episode.has_key('data-id'):
                    continue
                episodes.append( {  'wid': episode['data-id'], 
                                    'id': episode('span', {'class': 'e-count'})[0].text,
                                    'name': episode('span', {'class': 'e-title'})[0].text
                    } )
        return episodes

    def markEpisode(self, episode_id):
        return self.episode_action(MARK_URL, episode_id)

    def post_request(self, url, parameters):
        post_data = urllib.urlencode(parameters)
        req = urllib2.Request(url, post_data)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        return soup(opener.open(req), convertEntities=soup.HTML_ENTITIES)

    def shows(self):
        shows = []

        if self.browser.response().geturl() != BASE_URL:
            self.browser.open(BASE_URL)

        index = soup(self.browser.response(), convertEntities=soup.HTML_ENTITIES)
        show_section = index('section', {'class': 'shows'})[0]

        for div in show_section('div'):
            if not div.has_key('class') or not div['class'].startswith('show-tile '):
                continue
            for divInner in div('div', {'class': 'inner'}):
                for h2 in divInner('h2'):
                    shows.append(h2.text)

        return shows

    def unmarkEpisode(self, episode_id):
        return self.episode_action(UNMARK_URL, episode_id)
