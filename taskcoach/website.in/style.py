# -*- coding: ISO-8859-1 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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
                <h2>Get %(name)s for</h2>
                <ul>
                    <li><a href="download.html" title="Download %(name)s">Windows, Linux, and Mac OS X</a></li>
                    <li><a href="iPhone.html" title="iPhone/iPod app">iPhone and iPod Touch</a></li>
                    <li><a href="portable.html" title="Portable %(name)s">Portable devices</a></li>
                </ul>
            </div>
            <div class="navbox">
                <h2>Get support</h2>
                <ul>
                    <li><a href="mailinglist.html">Join mailinglist</a></li>
                    <li><a href="faq.html">Frequently asked questions</a></li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719135" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/request_support');">Request support</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719134" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/browse_bugs');">Browse known bugs</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?func=add&group_id=130831&atid=719134" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/submit_bug');">Report a bug</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719137" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/request_feature');">Request a feature (desktop version)</a>
                    </li>
                    <li><a href="http://taskcoach.uservoice.com/" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/uservoice.com/iPhone');">Request a feature (iPhone/iPod version)</a>
                    </li>

                </ul>
            </div>
            <div class="navbox">
                <h2>Give support</h2>
                <ul>                    
                    <li><a href="i18n.html">Help translate</a></li>
                    <li><a href="devinfo.html">Help develop</a></li>
                    <li><a href="donations.html">Donate</a></li>
                    <li><a href="http://www.cafepress.com/taskcoach/" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/cafepress.com/taskcoach');">Buy the mug</a>
                    </li>
                </p>
            </div>
            <div class="navbox">
                <h2>Credits</h2>
                <p>
                    <a href="http://www.python.org" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/python.org');"><img src="python-powered-w-70x28.png" alt="Python"
                       width="70" height="28" border="0"></a><br>
                    <a href="http://www.wxpython.org" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/wxpython.org');"><img
                       src="powered-by-wxpython-80x15.png"
                       alt="wxPython" width="80" height="15" border="0"></a><br>
                    <a href="http://www.icon-king.com" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/icon-king.com');">Nuvola icon set</a><br>
                    <a href="http://www.jrsoftware.org" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/jrsoftware.org');">Inno Setup</a><br>
                    <a href="http://www.bluerobot.com" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/bluerobot.com');">Bluerobot.com</a><br>
                    <a href="http://sourceforge.net/projects/taskcoach" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/projects/taskcoach');">
                        <img src="http://sflogo.sourceforge.net/sflogo.php?group_id=130831&type=8" 
                             width="80" height="15" border="0" alt="Task Coach at SourceForge.net"/>
                    </a><br>
                    <SCRIPT type='text/javascript' language='JavaScript' 
                            src='http://www.ohloh.net/projects/5109;badge_js'></SCRIPT>
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
        </div>
    </body>
</html>
'''%meta.metaDict


footer_fr = unicode('''        
        </div><!-- end of content div -->
        <div id="navAlpha">
            <div class="navbox">
                <h2>A propos de %(name)s</h2>
                <p>%(name)s %(version)s est sorti le %(date)s.</p>
                <ul>
                    <li><b><a href="download.html" title="Télécharger %(name)s">Téléchargement</a></b></li>
                    <li><a href="index.html" title="Survol de %(name)s">Survol</a></li>
                    <li><a href="screenshots.html" 
                       title="Voir des captures d'écran de %(name)s ici">Captures d'écran</a></li>
                    <li><a href="features.html" 
                       title="Liste des fonctionnalités de la version actuelle de %(name)s">Fonctionnalités</a></li>
                    <li><a href="i18n.html" 
                               title="Traductions disponibles">Traductions</a></li>
                    <li><a href="changes.html" 
                       title="Un survol des bogues corrigés et des fonctionnalités ajoutées par version de %(name)s">Historique</a></li>
                    <li><a href="license.html" 
                       title="Vos droits et devoirs liés à l'utilisation de %(name)s">Licence</a></li>
                </ul>
            </div>
            <div class="navbox">
                <h2>Obtenir de l'aide</h2>
                <ul>
                    <li><a href="mailinglist.html">S'inscrire à la chaîne de courriels</a></li>
                    <li><a href="faq.html">Questions fréquemment posées</a></li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719135" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/request_support');">Demande d'aide</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719134" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/browse_bugs');">Parcourir les bogues connus</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?func=add&group_id=130831&atid=719134" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/submit_bug');">Rapporter un bogue</a>
                    </li>
                    <li><a href="https://sourceforge.net/tracker/?group_id=130831&atid=719137" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/tracker/request_feature');">Demander une fonctionnalité</a>
                    </li>
                </ul>
            </div>
            <div class="navbox">
                <h2>Nous aider</h2>
                <ul>                    
                    <li><a href="i18n.html">Aider à traduire</a></li>
                    <li><a href="devinfo.html">Aider à développer</a></li>
                    <li><a href="donations.html">Dons</a></li>
                    <li><a href="http://www.cafepress.com/taskcoach/" 
                           onClick="javascript: pageTracker._trackPageview('/outgoing/cafepress.com/taskcoach');">Acheter le mug</a>
                    </li>
                </p>
            </div>
            <div class="navbox">
                <h2>Références</h2>
                <p>
                    <a href="http://www.python.org" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/python.org');"><img src="python-powered-w-70x28.png" alt="Python"
                       width="70" height="28" border="0"></a><br>
                    <a href="http://www.wxpython.org" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/wxpython.org');"><img
                       src="powered-by-wxpython-80x15.png"
                       alt="wxPython" width="80" height="15" border="0"></a><br>
                    <a href="http://www.icon-king.com" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/icon-king.com');">Nuvola icon set</a><br>
                    <a href="http://www.jrsoftware.org" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/jrsoftware.org');">Inno Setup</a><br>
                    <a href="http://www.bluerobot.com" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/bluerobot.com');">Bluerobot.com</a><br>
                    <a href="http://sourceforge.net/projects/taskcoach" 
                       onClick="javascript: pageTracker._trackPageview('/outgoing/sourceforge.net/projects/taskcoach');">
                        <img src="http://sflogo.sourceforge.net/sflogo.php?group_id=130831&type=8" 
                             width="80" height="15" border="0" alt="Task Coach at SourceForge.net"/>
                    </a><br>
                    <SCRIPT type='text/javascript' language='JavaScript' 
                            src='http://www.ohloh.net/projects/5109;badge_js'></SCRIPT>
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
                <h2>Mises à jour Twitter</h2>
                <div id="twitter_div">
                    <h2 style="display: none;" >Mises à jour Twitter</h2>
                    <ul id="twitter_update_list"></ul>
                    <a href="http://twitter.com/taskcoach" id="twitter-link" style="display:block;text-align:left;">Suivre Task Coach sur Twitter</a>
                </div>
                <script type="text/javascript" src="http://twitter.com/javascripts/blogger.js"></script>
                <script type="text/javascript" src="http://twitter.com/statuses/user_timeline/taskcoach.json?callback=twitterCallback2&amp;count=3"></script>
            </div>
        </div>
    </body>
</html>
''', 'ISO-8859-1')%meta.metaDict
