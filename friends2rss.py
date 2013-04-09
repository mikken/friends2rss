#!/usr/bin/python3
"""This script loads LJ cookies and then generates RSS feed from friends page.

Author: Paul Volkov
"""

import sys
import configparser
import urllib.request
import urllib.error
import http.cookiejar
import http.client
from os.path import abspath, realpath, dirname
from os import chdir

from lxml import etree

from friendsaux import rss_builder

def open_url():
    """Retreives friends page and returns the response."""
    if not keep_quiet:
        print('opening page', URL)
    try:
        return opener.open(URL)
    except urllib.error.URLError:
        sys.stderr.write('error while loading page\n')
        sys.exit(2)


def read_response():
    try:
        response = open_url()
        tree = etree.parse(response, parser=etree.HTMLParser())
    except http.client.IncompleteRead:
        sys.stderr.write('Could not read server response\n')
        sys.exit(27)
    return tree


def parse_page(soup, entries):
    """Goes through a page and generates a list with entries."""
    glob_divs = soup.findall('.//div[@class="b-lenta-item-wrapper"]')
    for glob_div_tag in glob_divs:
        entry = rss_builder.Entry()

        span_tag = glob_div_tag.find('.//span[@class="ljuser  i-ljuser     "]')
        entry.author = span_tag.get('lj:user')

        date_tag = glob_div_tag.find('.//p[@class="b-lenta-item-date"]')
        entry.date = date_tag.text
        a_tag = glob_div_tag.find('.//h3[@class="b-lenta-item-title"]/a')
        entry.subject = a_tag.text
        protected_tag = glob_div_tag.find('.//li[@title="Friends-only"]')
        if (protected_tag is not None):
            entry.subject = protected_prefix + ' ' + entry.subject
        entry.link = a_tag.get('href')

        entrytext_tag = glob_div_tag.find('.//div[@class="b-lenta-item-content"]')
        # iframes vary between refetches, we strip them
        for iframe_tag in entrytext_tag.findall('iframe'):
            entrytext_tag.replace(iframe_tag, etree.XML('<b>(IFRAME)</b>'))
        # strip LJ userheads
        for img_tag in entrytext_tag.findall('.//img[@class="i-ljuser-userhead"]'):
            img_tag.attrib['src'] = 'http://l-stat.livejournal.com/img/userinfo.gif'
        # need to strip <div> and </div>
        content = etree.tostring(entrytext_tag, with_tail=False, \
                encoding='utf-8').decode('utf-8')
        pos = content.find('>')
        content = content[pos + 1:-6].strip()
        entry.text=content
        entries.append(entry)


def check_logged_state(soup):
    """Checks if we are logged in by analyzing HTML page.

    Returns True in case of a yes."""
    mark_tag = soup.find('.//input[@name="user"]')
    if (not mark_tag):
        return True
    else:
        return False


def main():
    """Script entry point"""
    global URL, opener, protected_prefix
    # First, set working directory to current .py's location
    chdir(dirname(realpath(abspath(__file__))))
    # Load config
    try:
        config = configparser.ConfigParser()
        config.read('friends2rss.conf')
        URL = config['global']['URL']
        initialURL = URL
        depth = int(config['global']['depth'])
        protected_prefix = config['global']['protected_prefix']
    except IOError:
        sys.stderr.write('Could not read config file\n')
        sys.exit(3)
    except (KeyError, ValueError):
        sys.stderr.write("Config file isn't sane\n")
        sys.exit(4)
    # Load cookies generated by login script
    jar = http.cookiejar.MozillaCookieJar()
    try:
        jar.load('lj_cookies.txt')
    except IOError:
        sys.stderr.write('Error loading cookies\n')
        sys.exit(1)
    cooker = urllib.request.HTTPCookieProcessor(jar)
    opener = urllib.request.build_opener(cooker)
    tree=read_response()
    soup = tree.getroot()
    if not check_logged_state(soup):
        sys.stderr.write('Not logged in\n')
        sys.exit(26)
    title = soup.find('.//head/title').text
    userpic_tag = soup.find('.//img[@class="userpic"]')
    ara_tag = soup.find('.//a[@class="s-navmenu-rootlink"]')
    userpic = userpic_tag.get('src')
    alink = ara_tag.get('href')
    image = {'url' : userpic, \
            'link' : alink, \
            'title' : 'image', \
            'width' : '100', \
            'height' : '100'}
    entries = []
    parse_page(soup, entries)
    depth -= 1
    while depth > 0:
        a_tag = soup.find('.//a[@class="b-pager-link"]')
        URL = a_tag.get('href')
        if not URL:
            sys.stderr.write("Couldn't extract next level URL")
            break
        soup = read_response().getroot()
        parse_page(soup, entries)
        depth -= 1
    rss_feed = rss_builder.build_rss(entries, title, initialURL, \
            'livejournal friends feed', image)
    with open('friends.xml', 'w') as f:
        f.write(rss_feed)


if __name__ == '__main__':
    # Parse argument list
    usage = 'Usage: friend2rss.py [-q]\n\n'
    keep_quiet = False
    for argument in sys.argv[1:]:
        if argument == '-q':
            keep_quiet = True
        else:
            sys.stderr.write(usage)
            sys.exit(25)
    # Execute main procedure
    main()
