# browsershots.org - Test your web design in different browsers
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
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
Request models.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

from datetime import datetime
from xmlrpclib import Fault
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timesince import timesince, timeuntil
from django.utils.text import capfirst
from django.contrib.auth.models import User
from shotserver04.websites.models import Website
from shotserver04.platforms.models import Platform
from shotserver04.factories.models import Factory
from shotserver04.browsers.models import BrowserGroup, Browser
from shotserver04.features.models import Javascript, Java, Flash
from shotserver04.screenshots.models import Screenshot
from shotserver04.common import lock_timeout


class RequestGroup(models.Model):
    """
    Common options for a group of screenshot requests.
    """

    website = models.ForeignKey(Website,
        verbose_name=_('website'), raw_id_admin=True)
    width = models.IntegerField(
        _('screen width'), null=True, blank=True)
    height = models.IntegerField(
        _('screen height'), null=True, blank=True)
    bits_per_pixel = models.IntegerField(
        _('bits per pixel'), null=True, blank=True)
    javascript = models.ForeignKey(Javascript,
        verbose_name=_('Javascript'), blank=True, null=True)
    java = models.ForeignKey(Java,
        verbose_name=_('Java'), blank=True, null=True)
    flash = models.ForeignKey(Flash,
        verbose_name=_('Flash'), blank=True, null=True)
    user = models.ForeignKey(User,
        verbose_name=_('submitter'), blank=True, null=True)
    ip = models.IPAddressField(
        _('IP'))
    submitted = models.DateTimeField(
        _('submitted'), auto_now_add=True)
    expire = models.DateTimeField(
        _('expire'))

    class Admin:
        fields = (
            (None, {'fields': (
            'website',
            ('width', 'bits_per_pixel'),
            ('javascript', 'java', 'flash'),
            'submitter',
            'expire',
            )}),
            )
        list_display = ('__str__', 'width', 'javascript', 'java', 'flash')
        search_fields = ('website__url', )
        date_hierarchy = 'submitted'

    class Meta:
        verbose_name = _('request group')
        verbose_name_plural = _('request groups')
        ordering = ('-submitted', )

    def is_pending(self):
        """True if there are pending screenshot requests in this group."""
        return self.expire > datetime.now() and self.request_set.filter(
            screenshot__isnull=True).count()

    def time_since_submitted(self):
        """Human-readable formatting of interval since submitted."""
        return '<li>%s</li>' % (
            capfirst(_("requested %(interval)s ago")) %
            {'interval': timesince(self.submitted)})

    def time_until_expire(self):
        """Human-readable formatting of interval before expiration."""
        if not self.is_pending():
            return ''
        return '<li>%s</li>' % (
            capfirst(_("expires in %(interval)s")) %
            {'interval': timeuntil(self.expire)})

    def options(self):
        """Human-readable output of requested options."""
        result = []
        for attr in ('javascript', 'java', 'flash',
                     'width', 'bits_per_pixel'):
            option = getattr(self, attr)
            if option is None:
                continue
            name = self._meta.get_field(attr).verbose_name
            if attr == 'width':
                result.append('%s pixels wide' % (option))
            elif attr == 'bits_per_pixel':
                result.append('%s bits per pixel' % (option))
            else:
                result.append('%s %s' % (name, option))
        if not result:
            return ''
        return '<li>%s</li>' % ', '.join(result)

    def previews(self):
        """Thumbnails of screenshots for this request group."""
        screenshots = []
        requests = self.request_set.filter(screenshot__isnull=False)
        for request in requests:
            screenshot = request.screenshot
            screenshots.append(
                (screenshot.id, screenshot.preview_div()))
        screenshots.sort()
        if not screenshots and self.is_pending():
            return '<p class="hint">%s</p>' % (
                _("Your screenshots will appear here."))
        return '\n'.join([entry[1] for entry in screenshots])

    def pending_requests(self):
        """
        Human-readable list of pending screenshot requests, with
        request state (e.g. loading).
        """
        if not self.is_pending():
            return ''
        result = []
        for platform in Platform.objects.all():
            browsers = []
            for request in self.request_set.filter(
                screenshot__isnull=True, platform=platform):
                browser = request.browser_string()
                state = request.state()
                if state:
                    browsers.append('%s (%s)' % (browser, state))
                else:
                    browsers.append(browser)
            if browsers:
                browsers.sort()
                result.append('<li>%s: %s</li>' % (
                    platform.name, ', '.join(browsers)))
        return '\n'.join(result)


class Request(models.Model):
    """
    Request for a screenshot of a specified browser.
    Contains state during processing.
    """

    request_group = models.ForeignKey(RequestGroup,
        verbose_name=_('request group'), raw_id_admin=True)
    platform = models.ForeignKey(Platform,
        verbose_name=_('platform'), blank=True, null=True)
    browser_group = models.ForeignKey(BrowserGroup,
        verbose_name=_('browser group'))
    major = models.IntegerField(
        _('major'), blank=True, null=True)
    minor = models.IntegerField(
        _('minor'), blank=True, null=True)
    factory = models.ForeignKey(Factory,
        verbose_name=_('factory'), blank=True, null=True)
    locked = models.DateTimeField(
        _('locked'), blank=True, null=True)
    browser = models.ForeignKey(Browser,
        verbose_name=_('browser'), raw_id_admin=True,
        blank=True, null=True)
    redirected = models.DateTimeField(
        _('redirected'), blank=True, null=True)
    screenshot = models.ForeignKey(Screenshot,
        verbose_name=_('screenshot'), raw_id_admin=True,
        blank=True, null=True)

    class Admin:
        fields = (
            (None, {'fields': (
            'request_group',
            'platform',
            ('browser_group', 'major', 'minor'),
            )}),
            )
        list_display = ('browser_group', 'major', 'minor', 'platform')

    class Meta:
        verbose_name = _('request')
        verbose_name_plural = _('requests')

    def __str__(self):
        return '%s on %s' % (self.browser_string(), self.platform.name)

    def browser_string(self):
        """
        Human-readable formatting of requested browser.
        """
        result = [self.browser_group.name]
        if self.major is not None:
            result.append(' ' + str(self.major))
            if self.minor is not None:
                result.append('.' + str(self.minor))
        return ''.join(result)

    def state(self):
        """
        Human-readable output of request state.
        """
        if self.locked and self.locked < lock_timeout():
            return _('failed')
        if self.screenshot:
            return _('uploaded')
        if self.redirected:
            return _('loading')
        if self.locked:
            return _('starting')
        return ''

    def check_factory_lock(self, factory):
        """
        Check that the request is locked by this factory.
        """
        if self.factory is None:
            raise Fault(0,
                "Request %d was not locked." % self.id)
        if factory != self.factory:
            raise Fault(0,
                "Request %d was locked by factory %s." %
                (self.id, self.factory.name))
