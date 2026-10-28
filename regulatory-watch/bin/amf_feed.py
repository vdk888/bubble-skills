#!/usr/bin/env python3
"""List AMF publications of a period from the official AMF RSS feeds.

Usage: amf_feed.py [--du YYYY-MM-DD] [--au YYYY-MM-DD] [--flux 21,28,31] [--fichier feed.xml ...]
Default period: the last full Monday-Sunday week. --fichier reads local RSS files instead
of the network (offline, tests). Prints one tab-separated line per item:
date, feed, title, link. Feed status goes to stderr.
Exit 0 = at least one feed read, 2 = usage error, 3 = no feed could be read.
Standard library only. Only contacts https://www.amf-france.org.
"""
import argparse
import datetime as dt
import email.utils
import sys
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://www.amf-france.org/fr/flux-rss/display/"
FEEDS = {"21": "toutes les actualités", "28": "alertes et mises en garde", "31": "réglementation"}
LINK_PREFIX = "https://www.amf-france.org/"


def last_week(today):
    monday = today - dt.timedelta(days=today.weekday() + 7)
    return monday, monday + dt.timedelta(days=6)


def items(xml_bytes):
    for it in ET.fromstring(xml_bytes).iter("item"):
        title = " ".join((it.findtext("title") or "").split())
        link = (it.findtext("link") or "").strip().split("#")[0]
        try:
            day = email.utils.parsedate_to_datetime(it.findtext("pubDate") or "").date()
        except (TypeError, ValueError):
            continue
        if title and link.startswith(LINK_PREFIX):
            yield day, title, link


def fetch(feed_id):
    req = urllib.request.Request(BASE + feed_id, headers={"User-Agent": "bubble-regulatory-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main(argv):
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--du")
    p.add_argument("--au")
    p.add_argument("--flux", default=",".join(FEEDS))
    p.add_argument("--fichier", action="append", default=[])
    a = p.parse_args(argv[1:])
    try:
        start, end = last_week(dt.date.today())
        start = dt.date.fromisoformat(a.du) if a.du else start
        end = dt.date.fromisoformat(a.au) if a.au else end
    except ValueError:
        print("error: dates must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if end < start:
        print("error: --au before --du", file=sys.stderr)
        return 2
    sources = [(f, lambda f=f: open(f, "rb").read()) for f in a.fichier] or \
              [(f, lambda f=f: fetch(f)) for f in a.flux.split(",") if f in FEEDS]
    found, read = {}, 0
    for name, load in sources:
        try:
            got = [x for x in items(load()) if start <= x[0] <= end]
        except Exception as e:  # network, IO or XML error: report and go on
            print(f"flux {name}: non lu ({e})", file=sys.stderr)
            continue
        read += 1
        print(f"flux {name}: lu, {len(got)} élément(s) du {start} au {end}", file=sys.stderr)
        for day, title, link in got:
            found.setdefault(link, (day, name, title))
    for link, (day, name, title) in sorted(found.items(), key=lambda kv: kv[1][0], reverse=True):
        print(f"{day}\t{name}\t{title}\t{link}")
    return 0 if read else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
