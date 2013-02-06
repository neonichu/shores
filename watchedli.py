#!/usr/bin/env python

##
# Watched.li "API" using some scraping.
##

import cookielib
import mechanize
from BeautifulSoup import BeautifulSoup as soup

BASE_URL = 'http://watched.li/user/index'


class WatchedLi:
    def __init__(self, user, password):
        self.browser = mechanize.Browser()
        self.browser.set_cookiejar(cookielib.LWPCookieJar())

        self.browser.open(BASE_URL)
        self.browser.select_form(nr=1)
        self.browser.form['User[email]'] = user
        self.browser.form['User[pass0]'] = password
        self.browser.submit()

    def shows(self):
        shows = []

        index = soup(self.browser.response(), convertEntities=soup.HTML_ENTITIES)
        show_section = index('section', {'class': 'shows'})[0]

        for div in show_section('div'):
            if not div.has_key('class') or not div['class'].startswith('show-tile '):
                continue
            for divInner in div('div', {'class': 'inner'}):
                for h2 in divInner('h2'):
                    shows.append(h2.text)

        return shows
