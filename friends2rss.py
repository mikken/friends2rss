#!/usr/bin/python3

# This script loads LJ cookies and then generates RSS feed from friends page

# Base URL
URL = 'http://speckius.livejournal.com/friends/'
initialURL=URL
# How many pages to parse
depth = 2

import urllib.request
import urllib.error
import http.cookiejar
import sys

from bs4 import BeautifulSoup

import rss_builder

def open_url():
    print('opening page', URL)
    try:
        return opener.open(URL)
    except urllib.error.URLError:
        sys.stderr.write('error while loading page\n')
        sys.exit(2)


def find_class(tag, searchtag, searchclass):
    return tag.find(searchtag, {'class' : searchclass})


def parse_page(soup, entries):
    glob_divs = soup.findAll('div', {'class' : 'subcontent'})
    for glob_div_tag in glob_divs:
        entry = rss_builder.Entry()

        font_tag = glob_div_tag.find('font')
        entry.author = font_tag.contents[0]

        datesubject_tag = find_class(glob_div_tag, 'div', 'datesubject')
        date_tag = find_class(datesubject_tag, 'div', 'date')
        entry.date = date_tag.contents[0]
        a_tag = datesubject_tag.find('a')
        entry.subject = a_tag.contents[0]
        try:
            entry.link = a_tag.attrs['href']
        except KeyError:
            divcomments_tag = find_class(glob_div_tag, 'div', 'comments')
            a_tag = divcomments_tag.find('a')
            corrected = a_tag.attrs['href'] 
            entry.link = corrected[:corrected.find('?')]

        entrytext_tag = find_class(glob_div_tag, 'div', 'entry_text')
        entry.text = entrytext_tag.encode('utf-8').decode()
        # need to strip <div> and </div>
        pos = entry.text.find('>')
        entry.text = entry.text[pos + 1:-6]
        entries.append(entry)


jar = http.cookiejar.MozillaCookieJar()
try:
    jar.load('lj_cookies.txt')
except IOError:
    sys.stderr.write('Error loading cookies\n')
    sys.exit(1)
cooker = urllib.request.HTTPCookieProcessor(jar)
opener = urllib.request.build_opener(cooker)
response = open_url()
page = response.read().decode('utf-8')
soup = BeautifulSoup(page)
title = soup.title
userpic_tag = soup.find('img', alt="Userpic")
ara_tag = find_class(soup, 'a', 'i-ljuser-username')
image = {'url' : userpic_tag.attrs['src'], 'link' : ara_tag.attrs['href'], \
        'title' : 'image', 'width' : '100', 'height' : '100'}
entries = []
parse_page(soup, entries)
depth -= 1
while depth > 0:
    footer_tag = find_class(soup, 'ul', 'navfooter')
    a_tag = footer_tag.find('a')
    try:
        URL = a_tag.attrs['href']
    except AttributeError:
        sys.stderr.write("Couldn't extract next level URL")
        break
    response = open_url()
    soup = BeautifulSoup(response.read().decode('utf-8'))
    parse_page(soup, entries)
    depth -= 1
rss_feed = rss_builder.build_rss(entries, title, initialURL, \
        'livejournal friends feed', image)
with open('friends.xml', 'w') as f:
    f.write(rss_feed)
