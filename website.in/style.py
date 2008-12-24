'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

from taskcoachlib import meta


header = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD html 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <style type="text/css" media="screen">@import "default.css";</style>
        <link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
        <title>%(name)s</title>
    </head>
    <body>
        <div class="content">
            <table cellspacing=5>
                <tr>
                    <td valign=top>
                        <a href="index.html">
                            <img align="center" src="taskcoach.png"
                                 style="border-style: none"/>
                        </a>
                    </td>
                    <td>
                        <h1>%(name)s - %(description)s</h1>
                    </td>
                </tr>
            </table>
        </div>
        <div class="content">
'''%meta.metaDict

footer = '''        
        </div><!-- end of content div -->
        <div id="navAlpha">
            <div class="navbox">
                <h2>Download</h2>
                <p>
                    &raquo; <a href="download.html" title="Get %(name)s here">
                        Get %(name)s here
                    </a>
                </p>
            </div>
            <div class="navbox">
                <h2>About</h2>
                <p>
                    &raquo; <a href="index.html" title="%(name)s overview">Overview</a><br>
                    &raquo; <a href="screenshots.html" 
                       title="View some screenshots of %(name)s here">
                         Screenshots</a><br>
                    &raquo; <a href="features.html" 
                       title="List of features in the current version of %(name)s">
                         Features</a><br>
                    &raquo; <a href="i18n.html" 
                               title="Available translations">
                         Translations</a><br>
                    &raquo; <a href="changes.html">Change history</a><br>
                    &raquo; <a href="roadmap.html" 
                       title="Future plans for %(name)s">Roadmap</a><br>
                    &raquo; <a href="http://taskcoach.blogspot.com">Frank's blog</a><br>
                    &raquo; <a href="https://sourceforge.net/projects/taskcoach/"
                       title="%(name)s @ Sourceforge">Sourceforge pages</a><br>
                    &raquo; <a href="http://www.fraca7.net:8010/waterfall">Buildbot waterfall</a><br>
                    &raquo; <a href="license.html">License</a><br>
                    &raquo; <a href="credits.html">Credits</a>
                </p>
            </div>
            <div class="navbox">
                <h2>Get support</h2>
                <p>
                    &raquo; <a href="mailinglist.html">Join mailinglist</a><br>
                    &raquo; <a href="faq.html">Frequently asked questions</a><br>
                    &raquo; <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719135">Request support</a><br>
                    &raquo; <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719134">Browse known bugs</a><br>
                    &raquo; <a
                    href="https://sourceforge.net/tracker/?func=add&group_id=130831&atid=719134">Submit a bug report</a><br>
                    &raquo; <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719137">Request a feature</a>
                </p>
            </div>
            <div class="navbox">
                <h2>Give support</h2>
                <p>                    
                    &raquo; <a href="i18n.html">Help translate</a><br>
                    &raquo; <a href="devinfo.html">Help develop</a><br>
                    &raquo; <a href="donations.html">Donate</a><br>
                    &raquo; <a href="http://www.cafepress.com/taskcoach/">Buy the mug</a>
                </p>
            </div>
        </div>
        <div id="navBeta">
            <div class="navbox">
                <h2>Links</h2>
                <p>
                    <a href="http://www.python.org"><img
                    src="python-powered-w-70x28.png" alt="Python"
                    width="70" height="28" border="0"></a><br>
                    <a href="http://www.wxpython.org"><img
                    src="powered-by-wxpython-80x15.png"
                    alt="wxPython" width="80" height="15" border="0"></a><br>
                    <a href="http://www.icon-king.com">Nuvola icon set</a><br>
                    <a href="http://www.jrsoftware.org">Inno Setup</a><br>
                    <a href="http://www.bluerobot.com">Bluerobot.com</a><br>
                    <a href="http://sourceforge.net"><img
                src="http://sflogo.sourceforge.net/sflogo.php?group_id=130831&amp;type=1"
                width="88" height="31" border="0" alt="SourceForge.net"/></a><br>
                    <SCRIPT type='text/javascript' language='JavaScript' src='http://www.ohloh.net/projects/5109;badge_js'></SCRIPT>
                </p>
            </div>
            <div class="navbox">
                <h2>News</h2>
                <p>
                <a href="download.html">%(name)s %(version)s</a> was released
                on %(date)s.
                </p>
            </div>
            <div class="navbox">
                <h2>A word of warning</h2>
                <p>
                    %(name)s is currently alpha-state software. 
                    There are no separate stable and development branches, 
                    just a development branch. New versions usually contain 
                    a mix of new or changed features and bugfixes, and 
                    unfortunately, sometimes new bugs. So, if you use 
                    %(name)s in a production-like setting, backing up your 
                    work on a regular basis is strongly advised.
                </p>
            </div>
        </div>
    </body>
</html>
'''%meta.metaDict

