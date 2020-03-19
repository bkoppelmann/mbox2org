#!/usr/bin/env python3
"""
 Copyright (c) 2020 Bastian Koppelmann <kbastian@mail.upb.de>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, see <http://www.gnu.org/licenses/>.
"""

import os, sys
import argparse
import warnings
from datetime import date, datetime, timedelta, tzinfo
from tzlocal import get_localzone
from pytz import utc
import mailbox
sys.path.append("~/.local/lib/python3.8/site-packages")

from icalendar import Calendar
from ical2orgpy import generate_event_iterator, orgDatetime

def get_icals(folder):
    res = list()
    mdir = mailbox.Maildir(folder)

    for message in mdir:
        if message.get_content_maintype() == 'multipart':
            for part in message.walk():
                if part.get_content_type() == "text/calendar":
                    res.append(part)
    return res

def ical_to_org(ical):
    res = r""
    try:
        msg = ical.get_payload(decode=True)
        cal = Calendar.from_ical(msg)
    except ValueError as e:
        print("ERROR parsing ical file {}".format(str(e)))
        sys.exit(1)
    now = datetime.now(utc)
    start = now - timedelta(days=90)
    end = now + timedelta(days=90)

    tz = get_localzone()
    RECUR_TAG = ":RECURRING:"
    for comp in cal.walk():
        try:
            event_iter = generate_event_iterator(comp, start, end, tz)
            for comp_start, comp_end, rec_event in event_iter:
                summary = ""
                if "SUMMARY" in comp:
                    summary = comp['SUMMARY'].to_ical().decode("utf-8")
                    summary = summary.replace('\\,', ',')
                location = ""
                if "LOCATION" in comp:
                    location = comp['LOCATION'].to_ical().decode("utf-8")
                    location = location.replace('\\,', ',')
                if not summary and not location:
                    summary = u"(No title)"
                else:
                    summary += " - " + location
                res += u"* {}".format(summary)
                if rec_event and RECUR_TAG:
                    res += u" {}\n".format(RECUR_TAG)
                #res += u"\n"
                if isinstance(comp["DTSTART"].dt, datetime):
                    res += u"  {}--{}\n".format(
                        orgDatetime(comp_start, tz),
                        orgDatetime(comp_end, tz))
                else:  # all day event
                    res += u"  {}--{}\n".format(
                        orgDate(comp_start, tz),
                        orgDate(comp_end - timedelta(days=1), tz))
                if 'DESCRIPTION' in comp:
                    description = '\n'.join(comp['DESCRIPTION'].to_ical()
                                            .decode("utf-8").split('\\n'))
                    description = description.replace('\\,', ',')
                    res += u"{}\n".format(description)

                #res += u"\n"
        except Exception as e:
            msg = "Warning: an exception occured: %s" % e
            warnings.warn(msg)
            raise
    return res

def to_org(icals):
    res = list()
    for ical in icals:
        res.append(ical_to_org(ical))
    return res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=str, nargs=1, required=True)
    parser.add_argument('--output', type=str, nargs=1, required=True)
    args = parser.parse_args()

    icals = get_icals(args.folder[0])
    print(len(icals))

    with open(args.output[0], "w") as f:
        org = to_org(icals)
        f.write("".join(org))

main()
