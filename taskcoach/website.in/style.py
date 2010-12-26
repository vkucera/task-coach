# -*- coding: ISO-8859-1 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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
        <style type="text/css" media="screen">@import "css/default.css";</style>
        <script type="text/javascript" src="js/prototype.js"></script>
        <script type="text/javascript" src="js/scriptaculous.js?load=effects,builder"></script>
        <script type="text/javascript" src="js/lightbox.js"></script>
        <link rel="stylesheet" href="css/lightbox.css" type="text/css" media="screen" />
        <link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
        <title>%(name)s</title>
    </head>
    <body>
    <script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%%3E%%3C/script%%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-8814256-1");
pageTracker._trackPageview();
} catch(err) {}</script>
        <div class="content">
            <table cellspacing=5>
                <tr>
                    <td valign=top>
                        <a href="index.html">
                            <img align="center" src="images/taskcoach.png"
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
                <h2>About %(name)s</h2>
                <p>%(name)s %(version)s was released on %(date)s.</p>
                <ul>
                    <li><a href="index.html" title="%(name)s overview">Overview</a></li>
                    <li><a href="screenshots.html" 
                       title="View some screenshots of %(name)s here">Screenshots</a></li>
                    <li><a href="features.html" 
                       title="List of features in the current version of %(name)s">Features</a></li>
                    <li><a href="i18n.html" 
                               title="Available translations">Translations</a></li>
                    <li><a href="changes.html" 
                       title="An overview of bugs fixed and features added per version of %(name)s">Change history</a></li>
                    <li><a href="license.html" 
                       title="Your rights and obligations when using %(name)s">License</a></li>
                </ul>
            </div>
            <div class="navbox">
                <h2>Get %(name)s</h2>
                <ul>
                    <li><a href="download_for_windows.html" title="Download %(name)s for Windows">Windows</a></li>
                    <li><a href="download_for_mac.html" title="Download %(name)s for Mac OS X">Mac OS X</a></li>
                    <li><a href="download_for_linux.html" title="Download %(name)s for Linux">Linux</a></li>
                    <li><a href="download_for_iphone.html" title="Download %(name)s for iPhone and iPod Touch">iPhone and iPod Touch</a></li>
                    <li><a href="download_sources.html" title="Download %(name)s sources">Sources</a></li>
                    <li><a href="download_daily_build.html" title="Download %(name)s daily builds">Daily builds</a></li>
                    <li><a href="download_old_releases.html" title="Download old releases of %(name)s ">Old releases</a></li>
                </ul>
            </div>
            <div class="navbox">
                <h2>Get support</h2>
                <ul>
                    <li><a href="mailinglist.html">Join mailinglist</a></li>
                    <li><a href="https://answers.launchpad.net/taskcoach/+faqs">Frequently asked questions</a></li>
                    <li><a href="http://taskcoach.wikispaces.com">User manual</a></li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719135">Request support</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719134">Browse known bugs</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?func=add&group_id=130831&atid=719134">Report a bug</a>
                    </li>
                    <li><a href="http://taskcoach.uservoice.com/">Request a feature</a>
                    </li>
                </ul>
            </div>
            <div class="navbox">
                <h2>Give support</h2>
                <ul valign=top>                    
                    <li><a href="i18n.html">Help translate</a></li>
                    <li><a href="http://taskcoach.wikispaces.com">Help write the manual</a></li>
                    <li><a href="devinfo.html">Help develop</a></li>
                    <li><a href="donations.html">Donate</a></li>
                    <li><a href="http://twitter.com/share" class="twitter-share-button" data-url="http://taskcoach.org" data-text="Check out Task Coach: a free and open source todo app for Windows, Mac, Linux and iPhone." data-count="horizontal" data-via="taskcoach">Tweet</a><script type="text/javascript" src="http://platform.twitter.com/widgets.js"></script><br>
                        <iframe src="http://www.facebook.com/plugins/like.php?href=http%%3A%%2F%%2Ftaskcoach.org&amp;layout=button_count&amp;show_faces=true&amp;width=190&amp;action=like&amp;colorscheme=light&amp;height=21" 
                                scrolling="no" frameborder="0" 
                                style="border:none; overflow:hidden; width:190px; height:21px;" 
                                allowTransparency="true">
                        </iframe>
                    </li>
                </p>
            </div>
        </div>
        <div id="navBeta">
            <div class="navbox">
                <p>
<script type="text/javascript"><!--
google_ad_client = "pub-2371570118755412";
/* 120x240, gemaakt 10-5-09 */
google_ad_slot = "6528039249";
google_ad_width = 120;
google_ad_height = 240;
//-->
</script>
<script type="text/javascript"
src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>
                </p>
            </div>
            <div class="navbox">
                <h2>Twitter updates</h2>
                <div id="twitter_div">
                    <h2 style="display: none;" >Twitter Updates</h2>
                    <ul id="twitter_update_list"></ul>
                    <a href="http://twitter.com/taskcoach" id="twitter-link" style="display:block;text-align:left;">Follow Task Coach on Twitter</a>
                </div>
                <script type="text/javascript" src="http://twitter.com/javascripts/blogger.js"></script>
                <script type="text/javascript" src="http://twitter.com/statuses/user_timeline/taskcoach.json?callback=twitterCallback2&amp;count=3"></script>
            </div>
            <div class="navbox">
                <h2>Credits</h2>
                <ul>
                    <li>Web hosting courtesy of <a href="http://www.hostland.com">Hostland</a> and
                        <a href="http://henry.olders.ca">Henry Olders</a></li>
                    <li><a href="http://www.python.org"><img src="images/python-powered-w-70x28.png" alt="Python"
                           align=middle width="70" height="28" border="0"></a></li>
                    <li><a href="http://www.wxpython.org"><img
                           src="images/powered-by-wxpython-80x15.png"
                           alt="wxPython" width="80" height="15" border="0"></a></li>
                    <li><a href="http://www.icon-king.com">Nuvola icon set</a></li>
                    <li><a href="http://www.jrsoftware.org">Inno Setup</a></li>
                    <li><a href="http://www.bluerobot.com">Bluerobot.com</a></li>
                    <li><a href="http://sourceforge.net/projects/taskcoach"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=130831&type=8" 
                           width="80" height="15" border="0" alt="Task Coach at SourceForge.net"/>
                        </a></li>
                    <li><SCRIPT type='text/javascript' language='JavaScript' 
                                src='http://www.ohloh.net/projects/5109;badge_js'></SCRIPT></li>
                </ul>
            </div>
        </div>
    </body>
</html>
'''%meta.metaDict
