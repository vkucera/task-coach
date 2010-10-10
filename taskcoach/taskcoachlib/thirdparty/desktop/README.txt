Introduction
------------

The desktop module provides desktop environment detection and resource opening
support for a selection of common and standardised desktop environments. See
the module docstring for a more extensive introduction. See also the following
patch registered in the Python SourceForge project:

http://www.python.org/sf?id=1301512

Some ideas for desktop detection (XFCE) and URL opening (XFCE, X11) were
obtained from the xdg-utils project which seeks to implement programs
performing similar functions to those found in the desktop module. The
xdg-utils project can be found here:

http://portland.freedesktop.org/

Other information regarding desktop icons and menus, screensavers and MIME
configuration can also be found in xdg-utils.

Contact, Copyright and Licence Information
------------------------------------------

No Web page has yet been made available for this work, but the author can be
contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information. Whilst I would
prefer to release my software under the LGPL or GPL, the Python Software
Foundation insists on other licences, and I have chosen one of those in the
hope that this module becomes a part of the Python standard library.

Notes
-----

Notes on desktop application/environment support:

KDE           Supports file and URL opening using kfmclient, where the openURL
              command opens the resource and the exec command runs the
              resource.

GNOME         Supports file and URL opening using gnome-open.

XFCE          Supports file and URL opening using exo-open.

ROX-Filer     Supports file opening using "rox <filename>" but not URL
              opening.

New in desktop 0.3 (Changes since desktop 0.2.4)
------------------------------------------------

  * Made desktop a package.
  * Added support for graphical dialogue boxes through programs such as
    kdialog, zenity and Xdialog.
  * Added support for inspecting desktop windows (currently only for X11).

New in desktop 0.2.4 (Changes since desktop 0.2.3)
--------------------------------------------------

  * Added XFCE support (with advice from Miki Tebeka).
  * Added Ubuntu Feisty (7.04) package support.

New in desktop 0.2.3 (Changes since desktop 0.2.2)
--------------------------------------------------

  * Added Python 2.3 support (using popen2 instead of subprocess).

New in desktop 0.2.2 (Changes since desktop 0.2.1)
--------------------------------------------------

  * Changed the licence to LGPL.

New in desktop 0.2.1 (Changes since desktop 0.2)
------------------------------------------------

  * Added Debian/Ubuntu package support.

New in desktop 0.2 (Changes since desktop 0.1)
----------------------------------------------

  * Added support for waiting for launcher processes.
  * Added a tests directory.

Release Procedures
------------------

Update the desktop __version__ attribute.
Change the version number and package filename/directory in the documentation.
Update the release notes (see above).
Update the package information.
Check the release information in the PKG-INFO file.
Check the setup.py file.
Tag, export.
Archive, upload.
Update PyPI, PythonInfo Wiki, Vaults of Parnassus entries.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-desktop/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
