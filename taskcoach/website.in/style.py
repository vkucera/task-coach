from taskcoachlib import meta


header = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD html 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
        <style type="text/css" media="screen">@import "default.css";</style>
        <link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
        <title>%(name)s</title>
    </head>
    <body>
        <div class="content">
            <h1>
                <img align="center" src="taskcoach.png"/>
                &nbsp;%(name)s - %(description)s
            </h1>
        </div>
        <div class="content">
'''%meta.metaDict

footer = '''        
        </div><!-- end of content div -->
        <div id="navAlpha">
            <div class="navbox">
                <h2>Contents</h2>
                <p>
                    <a href="index.html" title="%(name)s homepage">Home</a><br>
                    <a href="https://sourceforge.net/projects/taskcoach/"
                       title="%(name)s at Sourceforge">Sourceforge home</a><br>
                    <a href="download.html" 
                       title="Get %(name)s here">Download</a><br>
                    <a href="screenshots.html" 
                       title="View some screenshots of %(name)s here">
                         Screenshots</a><br>
                    <a href="features.html" 
                       title="List of features in the current version of %(name)s">Features</a><br>
                    <a href="i18n.html">Translations</a><br>
                    <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719134">Known bugs</a><br>
                    <a href="http://taskcoach.blogspot.com">Blog</a><br>
                    <a href="changes.html">Change history</a><br>
                    <a href="roadmap.html" 
                       title="Future plans for %(name)s">Roadmap</a><br>
                    <a href="license.html">License</a><br>
                    <a href="credits.html">Credits</a><br>
                </p>
            </div>
            <div class="navbox">
                <h2>Get support</h2>
                <p>
                    <a href="mailinglist.html">Join mailinglist</a><br>
                    <a href="faq.html">Frequently asked questions</a><br>
                    <a href="https://sourceforge.net/tracker/?group_id=130831&atid=719137">Request a feature</a><br>
                    <a href="https://sourceforge.net/tracker/?func=add&group_id=130831&atid=719134">Submit a bug report</a>
                </p>
            </div>
            <div class="navbox">
                <h2>Give support</h2>
                <p>
                    <a href="i18n.html">Help translate</a><br>
                    <a href="devinfo.html">Help develop</a><br>
                    <a href="donations.html">Donate</a><br>
                    <a href="http://www.cafepress.com/taskcoach/">Buy the mug</a>
                </p>
            </div>
        </div>
        <div id="navBeta">
            <div class="navbox">
                <h2>Links</h2>
                <p>
                    <a href="http://www.python.org">Python</a><br>
                    <a href="http://www.wxpython.org">wxPython</a><br>
                    <a href="http://www.icon-king.com">Nuvola icon set</a><br>
                    <a href="http://www.jrsoftware.org">Inno Setup</a><br>
                    <a href="http://www.bluerobot.com">Bluerobot.com</a><br>
                    <a href="http://sourceforge.net"><img
                src="http://sflogo.sourceforge.net/sflogo.php?group_id=130831&amp;type=1"
                width="88" height="31" border="0" alt="SourceForge.net"/></a>
                </p>
            </div>
            <div class="navbox">
                <h2>A word of warning</h2>
                <p>
                    %(name)s is currently alpha-state software. 
                    New releases are made available approximately 
                    twice a month and old releases are not supported.
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

