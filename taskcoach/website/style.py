from taskcoachlib import meta


header = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<HTML>
    <HEAD>
        <META http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
        <LINK rel="stylesheet" type="text/css" href="default.css" />
        <link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />
        <TITLE>%(name)s</TITLE>
    </HEAD>
    <BODY>
        <DIV id="banner">
        %(name)s - %(description)s
        </DIV>
        <DIV id="content">
'''%meta.metaDict

footer = '''        
        </DIV><!-- end of content DIV -->
        <DIV id="links">
            <H4>Contents</H4>
            <UL>
                <LI><A HREF="index.html">Home</A></LI>
                <LI><A HREF="https://sourceforge.net/projects/taskcoach/">Sourceforge
                home</A></LI>
                <LI><A HREF="download.html">Download</A></LI>
                <LI><A HREF="screenshots.html">Screenshots</A></LI>
                <LI><A HREF="features.html">Features</A></LI>
                <LI><A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719137">Request a feature</A></LI>
                <LI><A HREF="https://sourceforge.net/tracker/?group_id=130831&atid=719134">Known bugs</A></LI>
                <LI><A HREF="https://sourceforge.net/tracker/?func=add&group_id=130831&atid=719134">Submit a bug report</A></LI>
                <LI><A HREF="changes.html">Change history</A></LI>
                <LI><A HREF="license.html">License</A></LI>
                <LI><A HREF="http://groups.yahoo.com/group/taskcoach/join">
                Join mailinglist</A></LI>
                <LI><A HREF="credits.html">Credits</A></LI>
            </UL>
            <H4>Links</H4>
            <UL>
                <LI><A HREF="http://www.python.org">Python</A></LI>
                <LI><A HREF="http://www.wxpython.org">wxPython</A></LI>
                <LI><A HREF="http://www.icon-king.com">Nuvola icon set</A></LI>
                <LI><A HREF="http://www.jrsoftware.org">Inno Setup</A></LI>
                <LI><A href="http://sourceforge.net"><IMG
            src="http://sourceforge.net/sflogo.php?group_id=130831&type=1"
            width="88" height="31" border="0" alt="SourceForge.net Logo"/></A>
            </UL>
        </DIV>
    </BODY>
</HTML>
'''%meta.metaDict

