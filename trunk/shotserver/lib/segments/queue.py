# -*- coding: utf-8 -*-
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
Show all queued requests for a given website.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'

# import time
from shotserver03.interface import xhtml
from shotserver03 import database

def write():
    """
    Write XHTML table with queued requests for a given website.
    """
    database.connect()
    try:
        for row in database.request.select_by_website(req.params.website):
            xhtml.write_open_tag('p', _class="queue")
            group, bpp, js, java, flash, media, submitted, expire = row

            options = []
            if bpp is not None:
                options.append("%d BPP" % bpp)
            if js is not None:
                options.append("JavaScript")
            if java is not None:
                options.append("Java")
            if flash is not None:
                options.append("Flash")
            if media is not None:
                if media == 'wmp':
                    options.append("Windows Media Player")
                else:
                    options.append(media)
            xhtml.write_tag('b', ', '.join(options))
            # time.strftime('%H:%M', time.localtime(submitted)),
            # time.strftime('%H:%M', time.localtime(submitted + expire)),
        xhtml.write_close_tag_line('p') # class="queue"
    finally:
        database.disconnect()
