# browsershots.org
# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.

"""
Display browsers that are installed on a factory.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'

import time
from shotserver03.interface import xhtml, human
from shotserver03 import database as db

def write():
    """
    Write XHTML table with browsers installed on req.params.factory.
    """
    factory = req.params.factory
    db.connect()
    try:
        rows = db.factory_browser.browsers(factory)
        xhtml.write_open_tag_line('table', _id="factory-browser")
        xhtml.write_table_row((
            "Browser",
            "Engine",
            "Maker",
            # "Last poll",
            # "Last upload",
            "Uploads<br />per hour",
            "Uploads<br />per day",
            "Special<br />command",
            ), element="th")
        for row in rows:
            (browser, name, major, minor, engine, manufacturer, command) = row
            xhtml.write_open_tag('tr')
            # link = xhtml.tag('a', name, href="/browsers/" + name)
            browser_version = db.browser.version_string(name, major, minor)
            xhtml.write_tag('td', browser_version)
            xhtml.write_tag('td', engine)
            xhtml.write_tag('td', manufacturer)

            per_hour = db.screenshot.count_uploads(
                'factory=%s AND browser=%s', (factory, browser), '1:00')
            xhtml.write_tag('td', per_hour)

            per_day = db.screenshot.count_uploads(
                'factory=%s AND browser=%s', (factory, browser), '24:00')
            xhtml.write_tag('td', per_day)

            xhtml.write_tag('td', command)
            xhtml.write_close_tag_line('tr')
        xhtml.write_close_tag_line('table')
    finally:
        db.disconnect()
