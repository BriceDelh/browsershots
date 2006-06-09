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
Screenshot request handling.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'

from shotserver03 import database

export_methods = ['poll']

def poll(factory, crypt):
    """
    poll(string, string) => array
    Try to find a matching screenshot request for a given factory.

    Arguments:
        factory -- the name of the factory (string, length max 20)
        crypt -- crypted password (hex string, length 32)

    Return value:
        status -- 'OK' or error message
        challenge -- random authentication challenge (salt + nonce)
        options -- dictionary with requested configuration

    If successful, the request will be locked for 3 minutes. This is
    to make sure that no requests are processed by two factories at
    the same time. If your factory takes longer to process a request,
    it is possible that somebody else will lock it. In this case, your
    upload will fail.

    The challenge consists of a salt (4 characters) and a nonce (32
    characters). The password is encrypted with MD5 as follows:
    crypt = md5(md5(salt + password) + nonce)

    If successful, options contains the following keys:
        browser -- browser name, possibly with version number
        width -- screen width in pixels
        bpp -- color depth (bits per pixel)
        js -- javascript version string
        java -- java version string
        flash -- flash version string
        media -- media player string

    """
    database.connect()
    try:
        factory = database.factory.select_serial(factory)
        ip = req.connection.remote_ip
        status = database.nonce.authenticate_factory(factory, ip, crypt)
        if status != 'OK':
            return status, '', '', 0, 0, '', '', '', ''
        where = database.factory.features(factory)
        row = database.request.match(where)
        if row is None:
            return 'No matching request.', '', {}
        else:
            request = row[0]
            database.lock.attempt(factory, request)
            salt = database.factory.select_salt(factory)
            nonce = database.nonce.create_request_nonce(request, ip)
            options = database.request.to_dict(row)
            challenge = salt + nonce
            return 'OK', challenge, options
    finally:
        database.disconnect()
