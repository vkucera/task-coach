
from twisted.application import service
from buildbot.slave.bot import BuildSlave

basedir = r'c:\build\WinXPSP2'
buildmaster_host = '192.168.0.10'
port = 9989
slavename = 'WinXPSP2'
passwd = file('.passwd', 'rb').readlines()[0].strip()
keepalive = 600
usepty = 1
umask = None

application = service.Application('buildslave')
s = BuildSlave(buildmaster_host, port, slavename, passwd, basedir,
               keepalive, usepty, umask=umask)
s.setServiceParent(application)

