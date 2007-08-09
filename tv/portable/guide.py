# Miro - an RSS based video player application
# Copyright (C) 2005-2007 Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import resources
from database import DDBObject
from template import fillStaticTemplate
from httpclient import grabURL
from urlparse import urlparse, urljoin
from xhtmltools import urlencode
from copy import copy
from util import returnsUnicode, unicodify, checkU
import re
import app
import config
import indexes
import menu
import prefs
import threading
import urllib
import eventloop
import views
import logging
import httpclient
from gtcache import gettext as _
from HTMLParser import HTMLParser,HTMLParseError
import iconcache

HTMLPattern = re.compile("^.*(<head.*?>.*</body\s*>)", re.S)

def isPartOfGuide(url, guideURL):
    """Return if url is part of a channel guide where guideURL is the base URL
    for that guide.
    """
    guideHost = urlparse(guideURL)[1]
    urlHost = urlparse(url)[1]
    return urlHost.endswith(guideHost)

class ChannelGuide(DDBObject):
    ICON_CACHE_SIZES = [
#        (20, 20),
    ]
    def __init__(self, url=None):
        checkU(url)
        self.url = url
        self.updated_url = url
        self.title = None
        self.lastVisitedURL = None
        self.iconCache = iconcache.IconCache(self, is_vital = True)
        self.favicon = None

        DDBObject.__init__(self)
        self.downloadGuide()

    def onRestore(self):
        self.lastVisitedURL = None
        if (self.iconCache == None):
            self.iconCache = iconcache.IconCache (self, is_vital = True)
        else:
            self.iconCache.dbItem = self
            self.iconCache.requestUpdate(True)
        self.downloadGuide()

    def __str__(self):
        return "Miro Guide <%s>" % (self.url,)

    def makeContextMenu(self, templateName, view):
        menuItems = [
            (lambda: app.delegate.copyTextToClipboard(self.getURL()),
                _('Copy URL to clipboard')),
        ]
        if not self.getDefault():
            i = (lambda: app.controller.removeGuide(self), _('Remove'))
            menuItems.append(i)
        return menu.makeMenu(menuItems)

    def remove(self):
        if self.iconCache is not None:
            self.iconCache.remove()
            self.iconCache = None
        DDBObject.remove(self)

    def isPartOfGuide(self, url):
        return isPartOfGuide(url, self.getURL())

    def getURL(self):
        if self.url is not None:
            return self.url
        else:
            return config.get(prefs.CHANNEL_GUIDE_URL)

    def getLastVisitedURL(self):
        if self.lastVisitedURL is not None:
            return self.lastVisitedURL
        else:
            return self.getURL()

    def getDefault(self):
        return self.url is None

    # For the tabs
    @returnsUnicode
    def getTitle(self):
        if self.getDefault():
            return _('Miro Guide')
        elif self.title:
            return self.title
        else:
            return self.getURL()

    def guideDownloaded(self, info):
        self.updated_url = info["updated-url"]
        try:
            parser = GuideHTMLParser(self.updated_url)
            parser.feed(info["body"])
            parser.close()
        except:
            pass
        else:
            self.title = parser.title
            self.favicon = parser.favicon
            self.iconCache.requestUpdate()
            self.signalChange()

    def guideError (self, error):
        pass

    def downloadGuide(self):
        httpclient.grabURL(self.getURL(), self.guideDownloaded, self.guideError)

    @returnsUnicode
    def getIconURL(self):
        if not self.getDefault() and self.iconCache.isValid():
            path = self.iconCache.getResizedFilename(20, 20)
            return resources.absoluteUrl(path)
        else:
            return resources.url("images/channelguide-icon-tablist.png")

    def getThumbnailURL(self):
        if self.favicon:
            return self.favicon
        else:
            if self.updated_url:
                parsed = urlparse(self.updated_url)
            else:
                parsed = urlparse(self.getURL())
            return parsed[0] + "://" + parsed[1] + "/favicon.ico"

# Grabs the feed link from the given webpage
class GuideHTMLParser(HTMLParser):
    def __init__(self, url):
        self.title = None
        self.in_title = False
        self.baseurl = url
        self.favicon = None
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        attrdict = {}
        for (key, value) in attrs:
            attrdict[key] = value
        if tag == 'title' and self.title == None:
            self.in_title = True
            self.title = u""
        if (tag == 'link' and attrdict.has_key('rel') and
            attrdict.has_key('type') and attrdict.has_key('href') and
            'icon' in attrdict['rel'].split(' ') and
            attrdict['type'].startswith("image/")):

            self.favicon = urljoin(self.baseurl,attrdict['href'])
            print self.favicon

    def handle_data(self, data):
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == 'title' and self.in_title:
            self.in_title = False

def getGuideByURL(url):
    return views.guides.getItemWithIndex(indexes.guidesByURL, url)
