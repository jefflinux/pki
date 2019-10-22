# Authors:
#     Endi S. Dewata <edewata@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright (C) 2019 Red Hat, Inc.
# All rights reserved.

from __future__ import absolute_import
import logging
from lxml import etree
import os

import pki

logger = logging.getLogger(__name__)


class RemoveUserDatabase(pki.server.upgrade.PKIServerUpgradeScriptlet):

    def __init__(self):
        super(RemoveUserDatabase, self).__init__()
        self.message = 'Remove unused UserDatabase from server.xml'

        self.parser = etree.XMLParser(remove_blank_text=True)

    def upgrade_instance(self, instance):

        self.upgrade_server_xml(instance)

        logger.info('Removing tomcat-users.xml')

        tomcat_users_xml = os.path.join(instance.conf_dir, 'tomcat-users.xml')

        if os.path.lexists(tomcat_users_xml):
            self.backup(tomcat_users_xml)
            pki.util.remove(tomcat_users_xml)

        logger.info('Removing tomcat-users.xsd')

        tomcat_users_xsd = os.path.join(instance.conf_dir, 'tomcat-users.xsd')

        if os.path.lexists(tomcat_users_xsd):
            self.backup(tomcat_users_xsd)
            pki.util.remove(tomcat_users_xsd)

    def upgrade_server_xml(self, instance):

        self.backup(instance.server_xml)

        document = etree.parse(instance.server_xml, self.parser)

        instance.remove_lockout_realm(document)
        instance.remove_default_user_database(document)

        with open(instance.server_xml, 'wb') as f:
            document.write(f, pretty_print=True, encoding='utf-8')