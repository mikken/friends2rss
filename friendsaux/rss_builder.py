#/usr/bin/env python3
"""This module builds XML file with RSS feed using extracted information.

Author: Paul Volkov
"""

import re
import sys
import datetime
import html

timezone_shift = 4

class Entry:
    """Stores a single post entry with all related info."""
    __slots__ = ('author', 'date', 'subject', 'link', 'text')

    def __repr__(self):
        return repr((self.author, self.date, self.subject, 
                self.link, self.text))

def convert_date(old_date):
    """Converts a date found in LJ's HTML code into RSS format."""
    month_names = ('January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December')
    weekday_names = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    match = re.search(r'(.+) (\d+) (\d\d\d\d), (\d\d):(\d\d)', old_date)
    if match:
        day = int(match.group(2))
        month = match.group(1)
        year = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        try:
            month = month_names.index(month) + 1
        except ValueError:
            sys.stderr.write('Strange "month" encountered\n')
            sys.exit(11)
        pubdate = datetime.datetime(year, month, day, hour, minute)
        zoneshift = datetime.timedelta(0, timezone_shift * 3600, 0)
        pubdate = pubdate - zoneshift
        weekday = weekday_names[pubdate.weekday()]
        day = str(pubdate.day)
        month = month_names[pubdate.month - 1][:3]
        year = str(pubdate.year)
        hour = str(pubdate.hour)
        minute = str(pubdate.minute)
        if len(hour) == 1:
            hour = '0' + hour
        if len(minute) == 1:
            minute = '0' + minute
        return weekday + ', ' + day + ' ' + month + ' ' + year + \
                ' ' + hour + ':' + minute + ':00 GMT'
    else:
        sys.stderr.write("Couldn't parse date {0}\n".format(repr(old_date)))
        sys.exit(10)

def build_rss(entries, title, link, description, image):
    """Returns string with RSS code built from 'entries' list."""
    rss_feed = ["""<?xml version="1.0" encoding="utf-8" ?>\n\
            <rss version="2.0"><channel><title>{0}</title>\n\
            <link>{1}</link><description>{2}</description>\n"""\
            .format(title, link, description)]
    rss_feed.append('<lastBuildDate>{0}</lastBuildDate>'\
            .format(convert_date(entries[0].date)))
    rss_feed.append('<image><url>{url}</url><title>{title}</title>\
            <link>{link}</link></image>'.format(**image))
    for entry in entries:
        rss_feed.append('<item>')
        rss_feed.append('<title>{0}</title>'.format(entry.subject))
        rss_feed.append('<author>{0}</author>'.format(entry.author))
        rss_feed.append('<link>{0}</link>'.format(entry.link))
        rss_feed.append('<pubDate>{0}</pubDate>'.format(\
                convert_date(entry.date)))
        rss_feed.append('<description>{0}</description>'.format(\
                html.escape(entry.text)))
        rss_feed.append('</item>')
    rss_feed.append('</channel></rss>')
    return '\n'.join(rss_feed)
