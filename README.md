friends2rss python script
=========================

Introduction
------------

Since LiveJournal does not allow to fetch RSS friends feeds for
basic accounts, we introduce this Python 3 script for generating
it locally.

How to use
----------

- Generate cookies file by executing `lj_login.py`.
  It will ask for your username and password and store cookies in
  `lj_cookies.txt`.

- Set friends page URL and parse depth (in pages) in configuration
  file (`python2rss.conf`). Use `python2rss.conf.example` as a reference.

- `protected_prefix` option is used for prefixing protected post's
  subject.

- Executing `friends2rss.py` will generate the actual feed.
  It'll be stored in `friends.xml`.

- You should generate the feed periodically using your favourite
  tool and add it into agregator software or online services.

- Use -q argument for 'quiet' mode.

Requirements
------------

You need to have lxml installed.

Restrictions
------------

This software will work with new LiveJournal friend feed style.
It's not designed to work with old style.
