from taskcoachlib import meta


header = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<HTML>
    <HEAD>
        <META http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
        <style type="text/css" media="screen">@import "default.css";</style>
        <link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
        <TITLE>%(name)s</TITLE>
    </HEAD>
    <BODY>
        <DIV class="content">
            <H1><IMG align="center" src="taskcoach.png"/>&nbsp;%(name)s - %(description)s</H1>
        </DIV>
        <DIV class="content">
'''%meta.metaDict

footer = '''        
        </DIV><!-- end of content DIV -->
        <DIV id="navAlpha">
            <DIV class="navbox">
                <H2>Contents</H2>
                <P>
                    <A HREF="index.html">Home</A><BR>
                    <A HREF="https://sourceforge.net/projects/taskcoach/">Sourceforge
                    home</A><BR>
                    <A HREF="download.html" title="Get %(name)s here">Download</A><BR>
                    <A HREF="screenshots.html">Screenshots</A><BR>
                    <A HREF="features.html" title="List of features in the current version of %(name)s">Features</A><BR>
                    <A HREF="i18n.html">Translations</A><BR>
                    <A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719134">Known bugs</A><BR>
                    <A HREF="changes.html">Change history</A><BR>
                    <A HREF="license.html">License</A><BR>
                    <A HREF="mailinglist.html">Join mailinglist</A><BR>
                    <A HREF="credits.html">Credits</A>
                </P>
            </DIV>
            <DIV class="navbox">
                <h2>Feedback</h2>
                <P>
                    <A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719137">Request a feature</A><BR>
                    <A HREF="https://sourceforge.net/tracker/?func=add&group_id=130831&atid=719134">Submit a bug report</A>
                </P>
            </DIV>
        </DIV>
        <DIV id="navBeta">
            <DIV class="navbox">
                <H2>Links</H2>
                <P>
                    <A HREF="http://www.python.org">Python</A><BR>
                    <A HREF="http://www.wxpython.org">wxPython</A><BR>
                    <A HREF="http://www.icon-king.com">Nuvola icon set</A><BR>
                    <A HREF="http://www.jrsoftware.org">Inno Setup</A><BR>
                    <A HREF="http://www.bluerobot.com">Bluerobot.com</A><BR>
                    <A href="http://sourceforge.net"><IMG
                src="http://sourceforge.net/sflogo.php?group_id=130831&type=1"
                width="88" height="31" border="0" alt="SourceForge.net Logo"/></A>
                </P>
            </DIV>
        </DIV>
    </BODY>
</HTML>
'''%meta.metaDict

