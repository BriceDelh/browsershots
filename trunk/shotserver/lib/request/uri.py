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
URI information about a HTTP request.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'

from shotserver03.request import tabledict

class IncorrectBasepathError(Exception):
    """The given base path does not match the actual URI."""
    pass

class URI(tabledict.TableDict):
    """
    Make request URI more explicit.
    """

    def __init__(self, basepath = ''):
        tabledict.TableDict.__init__(self)
        self.hostname = req.hostname
        self.raw = req.uri

        while basepath.endswith('/'):
            basepath = basepath[:-1]
        self.basepath = basepath
        fullbase = basepath + '/shotserver'

        self.parts = self.raw.split('/')
        for basepart in fullbase.split('/'):
            if basepart != self.parts[0]:
                raise IncorrectBasepathError('%s != %s' %
                    (repr(basepart), repr(self.parts[0])))
            self.parts.pop(0)

        self.lang = '' # self.parts.pop()
