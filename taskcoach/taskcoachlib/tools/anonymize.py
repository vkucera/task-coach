'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, wx
from xml.etree import ElementTree as ET
from taskcoachlib.i18n import _


def _anonymize(filename):
    tree = ET.parse(file(filename, 'rb'))
    root = tree.getroot()

    def handle(node):
        for child in node:
            handle(child)

        if 'subject' in node.attrib:
            node.attrib['subject'] = u'X' * len(node.attrib['subject'])

        if node.tag in ['description', 'data'] and node.text:
            node.text = '\n'.join([u'X' * len(line) for line in node.text.split('\n')])
            if node.tag == 'data':
                node.attrib['extension'] = 'X' * len(node.attrib['extension'])

        if node.tag == 'property' and node.attrib.has_key('name') and node.attrib['name'] == 'username':
            node.text = 'XXX' # pylint: disable=W0511

        if node.tag == 'attachment':
            if node.attrib.has_key('location'):
                node.attrib['location'] = 'X' * len(node.attrib['location'])

    handle(root)

    name, ext = os.path.splitext(filename)
    tree.write(name + '.anonymized' + ext)
    return name + '.anonymized' + ext


def anonymize(filename):
    name = _anonymize(filename)
    wx.MessageBox(_('Your task file has been anonymized and saved to:') + '\n' + name,
                  _('Finished'), wx.OK)
