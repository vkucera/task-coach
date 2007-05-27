import os, re, imaplib, ConfigParser, wx, tempfile
from i18n import _

_RX_MAILBOX = re.compile('mailbox-message://[\w.]+@(.*)#([0-9]+)')
_RX_IMAP    = re.compile('imap-message://([^@]+)@(.+)/(.*)#([0-9]+)')

def getThunderbirdDir():
    if '__WXMAC__' in wx.PlatformInfo:
        path = os.path.join(os.environ['HOME'], 'Library', 'Thunderbird')
    elif os.name == 'posix':
        path = os.path.join(os.environ['HOME'], '.thunderbird')
    elif os.name == 'nt':
        path = os.path.join(os.environ['APPDATA'], 'Thunderbird')
    else:
        raise EnvironmentError('Unsupported platform: %s' % os.name)

    return path

def getDefaultProfileDir():
    """Returns Thunderbird's default profile directory"""

    path = getThunderbirdDir()

    parser = ConfigParser.RawConfigParser()
    parser.read([os.path.join(path, 'profiles.ini')])

    for section in parser.sections():
        if parser.has_option(section, 'Default') and int(parser.get(section, 'Default')):
            if int(parser.get(section, 'IsRelative')):
                return os.path.join(path, parser.get(section, 'Path'))
            return parser.get(section, 'Path')

    for section in parser.sections():
        if parser.get(section, 'Name') == 'default':
            if int(parser.get(section, 'IsRelative')):
                return os.path.join(path, parser.get(section, 'Path'))
            return parser.get(section, 'Path')

    raise ValueError('No default section in profiles.ini')


class ThunderbirdMailboxReader(object):
    """Extracts an e-mail from a Thunderbird file. Behaves like a
    stream object to read this e-mail."""

    def __init__(self, url):
        """url is the internal reference to the mail, as collected
        through drag-n-drop"""

        mt = _RX_MAILBOX.search(url)

        self.url = url
        self.path = mt.group(1).replace('%20', ' ').split('/')
        self.offset = long(mt.group(2))
        self.filename = os.path.join(getDefaultProfileDir(), 'Mail',
                                     os.path.join(*tuple(self.path)))

        self.fp = file(self.filename, 'rb')
        self.fp.seek(self.offset)

        self.done = False

    def read(self, n=None):
        """Buffer-like read() method"""
        if self.done:
            return ''

        if n is None:
            lines = []
            for line in self.fp:
                if line.strip() == '.':
                    self.done = True
                    return ''.join(lines)
                lines.append(line)

            self.done = True
            return ''.join(lines)
        else:
            bf = self.fp.read(n)

            try:
                idx = bf.find('\r\n.\r\n')
            except ValueError:
                return bf
            else:
                self.done = True
                return bf[:idx] + '\r\n'

    def __iter__(self):
        class Iterator(object):
            def __init__(self, fp):
                self.fp = fp

            def __iter__(self):
                return self

            def next(self):
                line = self.fp.readline()
                if line.strip() == '.':
                    raise StopIteration
                return line

        return Iterator(self.fp)

    def saveToFile(self, fp):
        fp.write(self.read())


class ThunderbirdImapReader(object):
    _PASSWORDS = {}

    def __init__(self, url):
        mt = _RX_IMAP.search(url)

        self.url = url

        self.user = mt.group(1)
        self.server = mt.group(2)
        self.box = mt.group(3)
        self.uid = int(mt.group(4))

        config = {}
        def user_pref(key, value):
            config[key] = value
        for line in file(os.path.join(getDefaultProfileDir(), 'prefs.js'), 'r'):
            if line.startswith('user_pref('):
                exec line in { 'user_pref': user_pref, 'true': True, 'false': False }

        port = None
        stype = None
        isSecure = False
        # We iterate over a maximum of 100 mailservers. You'd think that
        # mailservers would be numbered consecutively, but apparently
        # that is not always the case, so we cannot assume that because
        # serverX does not exist, serverX+1 won't either. 
        for serverIndex in range(100): 
            name = 'mail.server.server%d' % serverIndex
            if config.has_key(name + '.hostname') and \
               config[name + '.hostname'] == self.server and \
               config[name + '.type'] == 'imap':
                if config.has_key(name + '.port'):
                    port = int(config[name + '.port'])
                if config.has_key(name + '.socketType'):
                    stype = config[name + '.socketType']
                if config.has_key(name + '.isSecure'):
                    isSecure = int(config[name + '.isSecure'])
                break

        self.ssl = bool(stype == 3 or isSecure)
        self.port = port or {True: 993, False: 143}[self.ssl]

    def _getMail(self):
        if self.ssl:
            cn = imaplib.IMAP4_SSL(self.server, self.port)
        else:
            cn = imaplib.IMAP4(self.server, self.port)

        if self._PASSWORDS.has_key((self.server, self.user, self.port)):
            pwd = self._PASSWORDS[(self.server, self.user, self.port)]
        else:
            pwd = wx.GetPasswordFromUser(_('Please enter password for user %(user)s on %(server)s:%(port)d') % \
                                         dict(user=self.user, server=self.server, port=self.port))
            if pwd == '':
                raise ValueError('User cancelled')

        while True:
            try:
                response, params = cn.login(self.user, pwd)
            except:
                response = 'KO'

            if response == 'OK':
                break

            pwd = wx.GetPasswordFromUser(_('Wrong password. Please try again.'))
            if pwd == '':
                raise ValueError('User cancelled')

        self._PASSWORDS[(self.server, self.user, self.port)] = pwd

        response, params = cn.select(self.box)

        if response != 'OK':
            raise ValueError('Could not select inbox %s' % self.box)

        response, params = cn.uid('FETCH', str(self.uid), '(RFC822)')

        if response != 'OK':
            raise ValueError('No such mail: %d' % self.uid)

        return params[0][1]

    def saveToFile(self, fp):
        fp.write(self._getMail())

#==============================================================================
#

def getMail(id_):
    if id_.startswith('mailbox-message://'):
        reader = ThunderbirdMailboxReader(id_)
    elif id_.startswith('imap-message://'):
        reader = ThunderbirdImapReader(id_)
    else:
        raise TypeError('Not supported: %s' % id_)

    filename = tempfile.mktemp('.eml')
    reader.saveToFile(file(filename, 'wb'))
    return filename
