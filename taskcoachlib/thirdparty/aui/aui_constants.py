"""
This module contains all the constants used by wxPython-AUI.

Especially important and meaningful are constants for AuiManager, AuiDockArt and
AuiNotebook.
"""

__author__ = "Andrea Gavana <andrea.gavana@gmail.com>"
__date__ = "31 March 2009"


import wx
from wx.lib.embeddedimage import PyEmbeddedImage

# ------------------------- #
# - AuiNotebook Constants - #
# ------------------------- #

# For tabart
# --------------

vertical_border_padding = 4
""" Border padding used in drawing tabs. """

if wx.Platform == "__WXMAC__":
    nb_close_bits = "\xFF\xFF\xFF\xFF\x0F\xFE\x03\xF8\x01\xF0\x19\xF3" \
                    "\xB8\xE3\xF0\xE1\xE0\xE0\xF0\xE1\xB8\xE3\x19\xF3" \
                    "\x01\xF0\x03\xF8\x0F\xFE\xFF\xFF"
    """ AuiNotebook close button image on wxMAC. """
    
elif wx.Platform == "__WXGTK__":
    nb_close_bits = "\xff\xff\xff\xff\x07\xf0\xfb\xef\xdb\xed\x8b\xe8" \
                    "\x1b\xec\x3b\xee\x1b\xec\x8b\xe8\xdb\xed\xfb\xef" \
                    "\x07\xf0\xff\xff\xff\xff\xff\xff"
    """ AuiNotebook close button image on wxGTK. """
    
else:
    nb_close_bits = "\xff\xff\xff\xff\xff\xff\xff\xff\xe7\xf3\xcf\xf9" \
                    "\x9f\xfc\x3f\xfe\x3f\xfe\x9f\xfc\xcf\xf9\xe7\xf3" \
                    "\xff\xff\xff\xff\xff\xff\xff\xff"
    """ AuiNotebook close button image on wxMSW. """

nb_left_bits = "\xff\xff\xff\xff\xff\xff\xff\xfe\x7f\xfe\x3f\xfe\x1f" \
               "\xfe\x0f\xfe\x1f\xfe\x3f\xfe\x7f\xfe\xff\xfe\xff\xff" \
               "\xff\xff\xff\xff\xff\xff"
""" AuiNotebook left button image. """

nb_right_bits = "\xff\xff\xff\xff\xff\xff\xdf\xff\x9f\xff\x1f\xff\x1f" \
                "\xfe\x1f\xfc\x1f\xfe\x1f\xff\x9f\xff\xdf\xff\xff\xff" \
                "\xff\xff\xff\xff\xff\xff"
""" AuiNotebook right button image. """

nb_list_bits = "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x0f" \
               "\xf8\xff\xff\x0f\xf8\x1f\xfc\x3f\xfe\x7f\xff\xff\xff" \
               "\xff\xff\xff\xff\xff\xff"
""" AuiNotebook windows list button image. """


#----------------------------------------------------------------------
tab_active_center = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAbCAYAAAC9WOV0AAAABHNCSVQICAgIfAhkiAAAADNJ"
    "REFUCJltzMEJwDAUw9DHX6OLdP/Bop4KDc3F2EIYrsFtrZow8GnH6OD1zvRTajvY2QMHIhNx"
    "jUhuAgAAAABJRU5ErkJggg==")
""" Center active tab image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_active_left = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAbCAYAAACjkdXHAAAABHNCSVQICAgIfAhkiAAAAglJ"
    "REFUOI2Nkk9rE0EYh5/J7mpW06xE2iSmeFHxEoqIAc/FQ5CKgn4DP4KlIQG/QVsQbBEKgop+"
    "Anvy4rV4bLT2JCGJPVXqwaZJd+f1kN26WTfJDrzszDLPPL/5o0jeFGAC54A0YKmEYAo4DzjA"
    "LHAZmElqtIGrhmEsvtzcfPNtb6/V6524SWALKBiGsfhxe/uzFhGth5XEmgVubWxsvA1Az68k"
    "1nngYbPZ7ASg69c06wxwe3V9/b3reVqHwGmwCZRs2370fX//wIuA0+CLwEKj0XilZTSu602G"
    "FcP7vLe7+7XlRaCgPw62gGv5fP6p63raiwFdLWKOgdNArl6vV1UqpQgcYdcYbwooAPfb7c7h"
    "mTWmUjGwCWTL5fL1K6VSLiqQyMTYyLVa/UEwe9IC0chFYKnb/XnkeiIDV+Q0UsG/qNkCnEql"
    "crNQLDpaxpskJnYayD1bXl4S/xrDoPLHKjQOmsHwlCuHv44+ZJ2sLTrGGqzg7zEc+VK1Wl1w"
    "HMcG0DFxw6sFsRVwAZhdWak9FoRJ+w2HCKzzwN3jXv+daVmGDkdWoMKb9fumHz0DFFfX1p5Y"
    "lmXo6N0G48jzVEDOt97pdA9ezOXzGU+PzBmN6VuDqyoDN3Z2vjyfKxQynhYkJuJ/L02Ara3X"
    "n3602r8HrpaTUy3HAy1/+hNq8O+r+q4WETirmFMNBwm3v+gdmytKNIUpAAAAAElFTkSuQmCC")
""" Left active tab image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_active_right = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAbCAYAAACjkdXHAAAABHNCSVQICAgIfAhkiAAAAkpJ"
    "REFUOI2NlM1rU0EUxX9zZ5KaWq3GKKnGutC0FEWCWAWLRUOxBetK/wdp6Re6F6TFXXGhuFdw"
    "b7dCQUUpiFt1XbB2q7Uf1iTvunjzkpe0afNgmLnDnHvOPe/OWCALtAFC+Cktfha4CRwBDnhg"
    "BQhaSrK19bf89dv35WfPX7y01haBbiAFmH3BlUA1Gm8WFt75BFkg0TK4VAl0Y3NL5+efvgIK"
    "wOH92EVjxRljGBi4VgTOeLDbk7kcqEZju1TWX7/Xgtm5J6+BS8ChvdilLhAhkUya4eFbxVQq"
    "1e3ZbUtgg8GKJd/Tk70/NjYCHCPsgX1kV8K5VA70z8amfvy0tAwMAcebSRfijikY8ez5/OlM"
    "JrOncbIjp4K1lmRb0sw8eDgCpAm7rwlz46YIzjpGb48WveyDNPhDfCOuHmNwzpHL5dK9fX3n"
    "mkmvaxJiayOCWMvM1PSdZtJrhiloLJMYIeESDFwf7Acyu0mXGLYmX0PpYi3ZbFdnoVDoBTpp"
    "uCxCjFob1tYKzlnGJyZHd5Mu6uVGkqvMCmCwzjE4eOMqcALoINauUic37hjhLXPWcTSdThWL"
    "QxcJX5yqdGk4H/cP9a4755iYnLpL+M/b8e0qjafrekb9TUskuNx/5TzQ5Y1zO9yOZEd1R7OI"
    "JdXebh/Pzt3zCToAMZv/AjU1orDWWKAGVJVSqcTqysp6X+/ZaeAL8KNac9wsVQ8yNeOsdZw8"
    "let4/2HpEdAPXDAb20HLj7xqeHT158ra4uLbz2bdg03krmetxrH9KDAmHP8Bn0j1t/01UV0A"
    "AAAASUVORK5CYII=")
""" Right active tab image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_close = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABHNCSVQICAgIfAhkiAAAAI9J"
    "REFUKJG90MEKAWEUxfEfM4rxAFIommzZzNb7v4BsLJTsiGQlYjHfME3flrO75/xvnXv5p/qY"
    "R/wcWTUktWCKFbrYB6/AAhecmwunAI/RwQAjbLGpoFakwjLATxzqMLQjC68A3/FohkljLkKN"
    "Ha4YKg8+VkBag3Pll9a1GikmuPk+4qMMs0jFMXoR/0d6A9JRFV/jxY+iAAAAAElFTkSuQmCC")
""" Normal close button image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_close_h = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABHNCSVQICAgIfAhkiAAAAOlJ"
    "REFUKJGVkiFuw0AQRd849hUS7iPUwGEllhyjYJ+gaK9Q4CsY9QTFIY4shQQucI8Q7l6h3Z0S"
    "r7UgjdrPZvVm52k0wpJLWe4y51qgVpECQFQnYPzabN4ra2cAAbgWxZMmyavAkTtROIn33fM0"
    "fcilLHep92+/wXHTd5K8JJlzbYD3w8C2aVZo2zTsh4FF5Zg516ZAHYBb35MbszbkxnDr+3hQ"
    "napIIUv1eT6vYPggvAGoSJE88r6XVFQnRA7BOdYIk8IUUZ1SYAQOsXOskRsT1+P/11pZO4v3"
    "ncLpESzed5W1c1jQn0/jBzPfck1qdmfjAAAAAElFTkSuQmCC")
""" Hover close button image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_close_p = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABHNCSVQICAgIfAhkiAAAASxJ"
    "REFUKJF9kbFLQlEYxX/nvbs55OAkiJAE7k7Nibo9xf+hrTlyr3Boipb+BCGq0bApJEQcG0Ms"
    "aQ0Lmq5+Dc+nDtbZ7uHce37fd8VSlWwh50PfRKqClWJXI8y6bu5uHj5e3wEEcJDP75txLBSx"
    "RYbdS7QfJ5PnsJIt5BbB4hQjkrQtjxlFILOXyvQDH/qmUCSJznDAYetkFTxsndAZDggkhCIf"
    "+qaLmWP1bu8oN+qrC+VGnd7t3bpKqrp4wBjl+ux8FUweSLwlXCnYCv2PHGgE1BLmTYykad2i"
    "kcOsi1TbZN7EKDfq67NZV5VsIeedvzQjCv5YK8R/4bw7Cl+/P7920+kJkBEq/hWWaPem45cQ"
    "YDybTfdSmf5CizckwHaAH9ATZldu7i560/ELwC+6RXdU6KzezAAAAABJRU5ErkJggg==")
""" Pressed close button image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_inactive_center = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAbCAYAAAC9WOV0AAAABHNCSVQICAgIfAhkiAAAAElJ"
    "REFUCJlVyiEOgDAUBNHp3qmX5iYkyMpqBAaFILRdDGn4qybZB98yy3ZZrRu1PpABAQiDSLN+"
    "h4NLEU8CBAfoPHZUywr3M/wCTz8c3/qQrUcAAAAASUVORK5CYII=")
""" Center inactive tab image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_inactive_left = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAbCAYAAACjkdXHAAAABHNCSVQICAgIfAhkiAAAAf5J"
    "REFUOI2llE1rE1EUhp8bZwyhaZomk5DaD40hSWPQVkTd6KIIEUWlLqTEhTaLulBQ6sfKjeBC"
    "ECULXQku/Alx7d6/U1EQae45LjJpJ5NOnOKBgYG5z33Px3sG/iPMIc87QAmYBZKHgdOu69a2"
    "3/W2yrVGK5vPLTlxFV3Xrb3+8v1Ntd5oiSpWBmnEidKT972tar3R6ovSt4qoxoIdoFipNlpW"
    "B6AVRYFEHNWn3a8dz/PK1rIHEgN2UpnMseVTK7fUGBME48CFe88+3sh5+SXr1xmMSbABvJXz"
    "l9siYAVGWJ0Mu/OVZr5Q8CpWfFWzD2Imj2qu/fhtG4wRVUIZg0bDBsgtn15dt6qIKKBDQZ81"
    "kWmnzly6OZ+ZzhSt7jfK6CBjFMwEk5TWOy82AVQGhzVUb5RJEkC2fLK6JgIiPhioeZJJUhev"
    "3j2RTqdzooqge2ojCxwxqrnrG4/uq4Ida3HgAjMOJ4CZSq1+RVBUzCgQinDDstfa282jyeTU"
    "rhUGF4CJgMPKhbXbmw9VFfG7fBA4LCao7AAzi8cXz1kF0dENMqH38KgWnnd7nSMJxxE5wI4+"
    "MHyCaeeAYvPshQ0RJby3wVSDHxxgAVh99elb9/evndmfP3boW2FsqGNhMMCdBy8/fJ5KZ6at"
    "qL+3Q1dEzFkNGMX82ZWh18e0/vVT/wuFmdYVv/ruKgAAAABJRU5ErkJggg==")
""" Left inactive tab image for the Chrome tab art. """

#----------------------------------------------------------------------
tab_inactive_right = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAbCAYAAACjkdXHAAAABHNCSVQICAgIfAhkiAAAAhBJ"
    "REFUOI2llM9rE1EQxz8zb1dSTKNuYtW01kQDRoKFWi9FEEq1IooUUWoPokWCtVqkR69KsSBU"
    "8OJRPOhBxZNe/At6FBER/HFUPEq1IGn3ecgm2ZjdJODCHPY9vvP9fufNDPzHZ4DDQBrYBKwB"
    "ftfoJys/Kw9ef/1y8/6rh67rHgKS3WLl6cqqtcCGD58+vn+zdPXorUql8g5Y7wTWdd+y4Vus"
    "teQK+yfKi8/KwM5umBXAAgioCIP54gTQBzgdwTbsQZR0JpOfXXw+0w27hn9EBGMcyRcPnulJ"
    "pbKd2JvACKgKnpcePH99+TSwvT3YEphusKsqB4ZHp4FMNWUn5loSEVSFbZ63b8eeUhpwu5Md"
    "JBFRjHHk7LXb08CuNuAaZTgEEaFQHJoEvDjpakOYmnURUFWSvam+0ujJfqAnmlnABhG2jlTZ"
    "j19YuEzMm7dUu34hihrDQG7vGLCViPq0VruuvdquyWSvN3xsKhclvbXaoUQiihFlfLJ8iYiq"
    "O/EtUC2xGGF3vjAObAnI6stCsZbYCLwnEonNY+dulALvHWSH2YN2PXLq4hz/9HpjnmOs18DZ"
    "bP9IIL0+afV5juqzRgLFcV1n9u6LGWAgWnaMBFHBOIbi0MgU1S3jAcjyyw9xqpvzWou1Pj++"
    "f/t8b/7EAvBW5u48agU37abWs99rv1YfL81fkT8V34YxbZ696d4CfwEszZSZx6Z26wAAAABJ"
    "RU5ErkJggg==")
""" Right inactive tab image for the Chrome tab art. """

# For auibook
# -----------

AuiBaseTabCtrlId = 5380
""" Base window identifier for AuiTabCtrl. """

AUI_NB_TOP                 = 1 << 0
""" With this style, tabs are drawn along the top of the notebook. """
AUI_NB_LEFT                = 1 << 1  # not implemented yet
""" With this style, tabs are drawn along the left of the notebook.
Not implemented yet. """
AUI_NB_RIGHT               = 1 << 2  # not implemented yet
""" With this style, tabs are drawn along the right of the notebook.
Not implemented yet. """
AUI_NB_BOTTOM              = 1 << 3
""" With this style, tabs are drawn along the bottom of the notebook. """
AUI_NB_TAB_SPLIT           = 1 << 4
""" Allows the tab control to be split by dragging a tab. """
AUI_NB_TAB_MOVE            = 1 << 5
""" Allows a tab to be moved horizontally by dragging. """
AUI_NB_TAB_EXTERNAL_MOVE   = 1 << 6
""" Allows a tab to be moved to another tab control. """
AUI_NB_TAB_FIXED_WIDTH     = 1 << 7
""" With this style, all tabs have the same width. """
AUI_NB_SCROLL_BUTTONS      = 1 << 8
""" With this style, left and right scroll buttons are displayed. """
AUI_NB_WINDOWLIST_BUTTON   = 1 << 9
""" With this style, a drop-down list of windows is available. """
AUI_NB_CLOSE_BUTTON        = 1 << 10
""" With this style, a close button is available on the tab bar. """
AUI_NB_CLOSE_ON_ACTIVE_TAB = 1 << 11
""" With this style, a close button is available on the active tab. """
AUI_NB_CLOSE_ON_ALL_TABS   = 1 << 12
""" With this style, a close button is available on all tabs. """
AUI_NB_MIDDLE_CLICK_CLOSE  = 1 << 13
""" Allows to close `AuiNotebook` tabs by mouse middle button click. """
AUI_NB_SUB_NOTEBOOK        = 1 << 14
""" This style is used by `AuiManager` to create automatic `AuiNotebooks`. """
AUI_NB_HIDE_ON_SINGLE_TAB  = 1 << 15
""" Hides the tab window if only one tab is present. """
AUI_NB_SMART_TABS          = 1 << 16
""" Use `Smart Tabbing`, like ``Alt`` + ``Tab`` on Windows. """
AUI_NB_USE_IMAGES_DROPDOWN = 1 << 17
""" Uses images on dropdown window list menu instead of check items. """
AUI_NB_CLOSE_ON_TAB_LEFT   = 1 << 18
""" Draws the tab close button on the left instead of on the right
(a la Camino browser). """
AUI_NB_TAB_FLOAT           = 1 << 19
""" Allows the floating of single tabs.
Known limitation: when the notebook is more or less full screen, tabs 
cannot be dragged far enough outside of the notebook to become 
floating pages. """
AUI_NB_DRAW_DND_TAB        = 1 << 20
""" Draws an image representation of a tab while dragging. """
AUI_NB_SASH_DCLICK_UNSPLIT = 1 << 22
""" Unsplit a splitted `AuiNotebook` when double-clicking on a sash. """

AUI_NB_DEFAULT_STYLE = AUI_NB_TOP | AUI_NB_TAB_SPLIT | AUI_NB_TAB_MOVE | \
                       AUI_NB_SCROLL_BUTTONS | AUI_NB_CLOSE_ON_ACTIVE_TAB | \
                       AUI_NB_MIDDLE_CLICK_CLOSE | AUI_NB_DRAW_DND_TAB
""" Default `AuiNotebook` style. """

#----------------------------------------------------------------------
Mondrian = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAHFJ"
    "REFUWIXt1jsKgDAQRdF7xY25cpcWC60kioI6Fm/ahHBCMh+BRmGMnAgEWnvPpzK8dvrFCCCA"
    "coD8og4c5Lr6WB3Q3l1TBwLYPuF3YS1gn1HphgEEEABcKERrGy0E3B0HFJg7C1N/f/kTBBBA"
    "+Vi+AMkgFEvBPD17AAAAAElFTkSuQmCC")
""" Default icon for the Smart Tabbing dialog. """

# -------------------------- #
# - FrameManager Constants - #
# -------------------------- #

# Docking Styles
AUI_DOCK_NONE = 0
""" No docking direction. """
AUI_DOCK_TOP = 1
""" Top docking direction. """
AUI_DOCK_RIGHT = 2
""" Right docking direction. """
AUI_DOCK_BOTTOM = 3
""" Bottom docking direction. """
AUI_DOCK_LEFT = 4
""" Left docking direction. """
AUI_DOCK_CENTER = 5
""" Center docking direction. """
AUI_DOCK_CENTRE = AUI_DOCK_CENTER
""" Centre docking direction. """
AUI_DOCK_NOTEBOOK_PAGE = 6
""" Automatic AuiNotebooks docking style. """

# Floating/Dragging Styles
AUI_MGR_ALLOW_FLOATING           = 1 << 0
""" Allow floating of panes. """
AUI_MGR_ALLOW_ACTIVE_PANE        = 1 << 1
""" If a pane becomes active, "highlight" it in the interface. """
AUI_MGR_TRANSPARENT_DRAG         = 1 << 2
""" If the platform supports it, set transparency on a floating pane
while it is dragged by the user. """
AUI_MGR_TRANSPARENT_HINT         = 1 << 3
""" If the platform supports it, show a transparent hint window when
the user is about to dock a floating pane. """
AUI_MGR_VENETIAN_BLINDS_HINT     = 1 << 4
""" Show a "venetian blind" effect when the user is about to dock a
floating pane. """
AUI_MGR_RECTANGLE_HINT           = 1 << 5
""" Show a rectangle hint effect when the user is about to dock a
floating pane. """
AUI_MGR_HINT_FADE                = 1 << 6
""" If the platform supports it, the hint window will fade in and out. """
AUI_MGR_NO_VENETIAN_BLINDS_FADE  = 1 << 7
""" Disables the "venetian blind" fade in and out. """
AUI_MGR_LIVE_RESIZE              = 1 << 8
""" Live resize when the user drag a sash. """
AUI_MGR_ANIMATE_FRAMES           = 1 << 9
""" Fade-out floating panes when they are closed (all platforms which support
frames transparency) and show a moving rectangle when they are docked
(Windows < Vista and GTK only). """

AUI_MGR_DEFAULT = AUI_MGR_ALLOW_FLOATING | AUI_MGR_TRANSPARENT_HINT | \
                  AUI_MGR_HINT_FADE | AUI_MGR_NO_VENETIAN_BLINDS_FADE
""" Default `AuiManager` style. """

# Panes Customization
AUI_DOCKART_SASH_SIZE = 0
""" Customizes the sash size. """
AUI_DOCKART_CAPTION_SIZE = 1
""" Customizes the caption size. """
AUI_DOCKART_GRIPPER_SIZE = 2
""" Customizes the gripper size. """
AUI_DOCKART_PANE_BORDER_SIZE = 3
""" Customizes the pane border size. """
AUI_DOCKART_PANE_BUTTON_SIZE = 4
""" Customizes the pane button size. """
AUI_DOCKART_BACKGROUND_COLOUR = 5
""" Customizes the background colour. """
AUI_DOCKART_BACKGROUND_GRADIENT_COLOUR = 6
""" Customizes the background gradient colour. """
AUI_DOCKART_SASH_COLOUR = 7
""" Customizes the sash colour. """
AUI_DOCKART_ACTIVE_CAPTION_COLOUR = 8
""" Customizes the active caption colour. """
AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR = 9
""" Customizes the active caption gradient colour. """
AUI_DOCKART_INACTIVE_CAPTION_COLOUR = 10
""" Customizes the inactive caption colour. """
AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR = 11
""" Customizes the inactive gradient caption colour. """
AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR = 12
""" Customizes the active caption text colour. """
AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR = 13
""" Customizes the inactive caption text colour. """
AUI_DOCKART_BORDER_COLOUR = 14
""" Customizes the border colour. """
AUI_DOCKART_GRIPPER_COLOUR = 15
""" Customizes the gripper colour. """
AUI_DOCKART_CAPTION_FONT = 16
""" Customizes the caption font. """
AUI_DOCKART_GRADIENT_TYPE = 17
""" Customizes the gradient type (no gradient, vertical or horizontal). """
AUI_DOCKART_DRAW_SASH_GRIP = 18
""" Draw a sash grip on the sash. """

# Caption Gradient Type
AUI_GRADIENT_NONE = 0
""" No gradient on the captions. """
AUI_GRADIENT_VERTICAL = 1
""" Vertical gradient on the captions. """
AUI_GRADIENT_HORIZONTAL = 2
""" Horizontal gradient on the captions. """

# Pane Button State
AUI_BUTTON_STATE_NORMAL = 0
""" Normal button state. """
AUI_BUTTON_STATE_HOVER = 1 << 1
""" Hovered button state. """
AUI_BUTTON_STATE_PRESSED = 1 << 2
""" Pressed button state. """
AUI_BUTTON_STATE_DISABLED = 1 << 3
""" Disabled button state. """
AUI_BUTTON_STATE_HIDDEN   = 1 << 4
""" Hidden button state. """
AUI_BUTTON_STATE_CHECKED  = 1 << 5
""" Checked button state. """

# Pane minimize mode
AUI_MINIMIZE_POS_SMART    = 0x01
""" Minimizes the pane on the closest tool bar. """
AUI_MINIMIZE_POS_TOP      = 0x02
""" Minimizes the pane on the top tool bar. """
AUI_MINIMIZE_POS_LEFT     = 0x03
""" Minimizes the pane on its left tool bar. """
AUI_MINIMIZE_POS_RIGHT    = 0x04
""" Minimizes the pane on its right tool bar. """
AUI_MINIMIZE_POS_BOTTOM   = 0x05
""" Minimizes the pane on its bottom tool bar. """
AUI_MINIMIZE_POS_MASK     = 0x07
""" Mask to filter the position flags. """
AUI_MINIMIZE_CAPT_HIDE    = 0
""" Hides the caption of the minimized pane. """
AUI_MINIMIZE_CAPT_SMART   = 0x08
""" Displays the caption in the best rotation (horz or clockwise). """
AUI_MINIMIZE_CAPT_HORZ    = 0x10
""" Displays the caption horizontally. """
AUI_MINIMIZE_CAPT_MASK    = 0x18
""" Mask to filter the caption flags. """

# Button kind
AUI_BUTTON_CLOSE = 101
""" Shows a close button on the pane. """
AUI_BUTTON_MAXIMIZE_RESTORE = 102
""" Shows a maximize/restore button on the pane. """
AUI_BUTTON_MINIMIZE = 103
""" Shows a minimize button on the pane. """
AUI_BUTTON_PIN = 104
""" Shows a pin button on the pane. """
AUI_BUTTON_OPTIONS = 105
""" Shows an option button on the pane (not implemented). """
AUI_BUTTON_WINDOWLIST = 106
""" Shows a window list button on the pane (for AuiNotebook). """
AUI_BUTTON_LEFT = 107
""" Shows a left button on the pane (for AuiNotebook). """
AUI_BUTTON_RIGHT = 108
""" Shows a right button on the pane (for AuiNotebook). """
AUI_BUTTON_UP = 109
""" Shows an up button on the pane (not implemented). """
AUI_BUTTON_DOWN = 110
""" Shows a down button on the pane (not implemented). """
AUI_BUTTON_CUSTOM1 = 201
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM2 = 202
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM3 = 203
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM4 = 204
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM5 = 205
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM6 = 206
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM7 = 207
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM8 = 208
""" Shows a custom button on the pane. """
AUI_BUTTON_CUSTOM9 = 209
""" Shows a custom button on the pane. """

# Pane Insert Level
AUI_INSERT_PANE = 0
""" Level for inserting a pane. """
AUI_INSERT_ROW = 1
""" Level for inserting a row. """
AUI_INSERT_DOCK = 2
""" Level for inserting a dock. """

# Action constants
actionNone = 0
""" No current action. """
actionResize = 1
""" Resize action. """
actionClickButton = 2
""" Click on a pane button action. """
actionClickCaption = 3
""" Click on a pane caption action. """
actionDragToolbarPane = 4
""" Drag a floating toolbar action. """
actionDragFloatingPane = 5
""" Drag a floating pane action. """

# Drop/Float constants
auiInsertRowPixels = 10
""" Number of pixels between rows. """
auiNewRowPixels = 40
""" Number of pixels for a new inserted row. """
auiLayerInsertPixels = 40
""" Number of pixels between layers. """
auiLayerInsertOffset = 5
""" Number of offset pixels between layers. """
auiToolBarLayer = 10
""" AUI layer for a toolbar. """

# some built in bitmaps

if wx.Platform == "__WXMAC__":

    close_bits = "\xFF\xFF\xFF\xFF\x0F\xFE\x03\xF8\x01\xF0\x19\xF3\xB8\xE3\xF0" \
                 "\xE1\xE0\xE0\xF0\xE1\xB8\xE3\x19\xF3\x01\xF0\x03\xF8\x0F\xFE\xFF\xFF"
    """ Close button bitmap for a pane on wxMAC. """

elif wx.Platform == "__WXGTK__":

    close_bits = "\xff\xff\xff\xff\x07\xf0\xfb\xef\xdb\xed\x8b\xe8\x1b\xec\x3b\xee" \
                 "\x1b\xec\x8b\xe8\xdb\xed\xfb\xef\x07\xf0\xff\xff\xff\xff\xff\xff"
    """ Close button bitmap for a pane on wxGTK. """

else:

    close_bits = "\xff\xff\xff\xff\xff\xff\xff\xff\xcf\xf3\x9f\xf9\x3f\xfc\x7f\xfe" \
                 "\x3f\xfc\x9f\xf9\xcf\xf3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
    """ Close button bitmap for a pane on wxMSW. """

pin_bits     = '\xff\xff\xff\xff\xff\xff\x1f\xfc\xdf\xfc\xdf\xfc\xdf\xfc\xdf\xfc' \
               '\xdf\xfc\x0f\xf8\x7f\xff\x7f\xff\x7f\xff\xff\xff\xff\xff\xff\xff'
""" Pin button bitmap for a pane. """

max_bits     = '\xff\xff\xff\xff\xff\xff\x07\xf0\xf7\xf7\x07\xf0\xf7\xf7\xf7\xf7' \
               '\xf7\xf7\xf7\xf7\xf7\xf7\x07\xf0\xff\xff\xff\xff\xff\xff\xff\xff'
""" Maximize button bitmap for a pane. """

restore_bits = '\xff\xff\xff\xff\xff\xff\x1f\xf0\x1f\xf0\xdf\xf7\x07\xf4\x07\xf4' \
               '\xf7\xf5\xf7\xf1\xf7\xfd\xf7\xfd\x07\xfc\xff\xff\xff\xff\xff\xff'
""" Restore/maximize button bitmap for a pane. """

minimize_bits = '\xff\xff\xff\xff\xff\xff\x07\xf0\xf7\xf7\x07\xf0\xff\xff\xff\xff' \
                '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
""" Minimize button bitmap for a pane. """

restore_xpm = ["16 15 3 1",
               "       c None",
               ".      c #000000",
               "+      c #FFFFFF",
               "                ",
               "     .......... ",
               "     .++++++++. ",
               "     .......... ",
               "     .++++++++. ",
               " ..........+++. ",
               " .++++++++.+++. ",
               " ..........+++. ",
               " .++++++++..... ",
               " .++++++++.     ",
               " .++++++++.     ",
               " .++++++++.     ",
               " .++++++++.     ",
               " ..........     ",
               "                "]
""" Restore/minimize button bitmap for a pane. """

#----------------------------------------------------------------------

down_focus_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACaUlE"
    "QVRIib2WvWsUQRjGn5mdnWxyTaqz9q+QlLnGToSgWAYDNjbpNCAGDGIvaRPbNJGQyiAEbK+w"
    "sAo2qexyEhbxsvt+jMXc3u3liPfhmWeXnWVm9vc+vO/M7prVzTb+gxyA7Ye/nXPWWmvtXKBb"
    "B9YBcM5lWZam6by4QNcBsNamaeq9d87NmWutdc59+NgGoKIizCwsxMTMFI8oZmZilzomZiFm"
    "FWERaXbv7eyueO+TJEHM79LSkvfeWnv2qftgex2ASGDmkrUkKUspiIuCy5IL4qKQgnghdQVx"
    "ScKsxCKiaH8lIu99NOwAEFGsG4Dv5xeiQYOKBBYVUWJlFhIVVmIlEZGQJKVIYBbWoKqqwQN5"
    "nqdpuri42OMys6rGOG/X78yW0bXWNyLqcyyAEEIIYcYK3aB5Lazb4o5fsPc3ToFaloxBwMle"
    "6+9Pjfd7stda6HR85+dCPC86Y6ETcQEcHz32eZ7meZrnx0ePJnlk0vwenm70r/PkTgWdjjuV"
    "rnPPfvxaa+3NcL3GMaub7XdPtNFoZFn24tmX1/trAOLuM6aaFQwQYExAMPWNaUw1FW+eHj5/"
    "dbfZbDYajY33F7e1L4gUA5uo3fd8AWbQH70bjGqEyxLq3LoMYhKCgakCIWZoLLdkMRE43Iy0"
    "tWi9QOP8xoIFAyBUjF7dgOizb9iMhLmByxIAHbAGKYigUPX3hqog47hSvfCHfYRaDcNg3IzO"
    "7GmydRaGi37zMujrut/9l58nijROQ9yd3ZXLy8urq6vZWFmW9f+Yhrje++XlZR2keDpZa4f+"
    "H/pKkiR+/f9dDsDWgQW6QHcuxKg/ZbVtCjjzINkAAAAASUVORK5CYII=")
""" VS2005 focused docking guide window down bitmap. """

#----------------------------------------------------------------------
down_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACY0lE"
    "QVRIib2WwWrUUBSG/3tzc5s2m0JhXPsU0u1s3Lkpui4W3PgAuhAFi2/QbesTVEphwCIU3Hbh"
    "wk2LG1fujJQgtMk55x4Xd2aS6VAzM479JyQhufnOz3/uzcQMBgP8BzkAeZ4756y11tqlQIui"
    "cACcc1mWpWm6ZK61Nk1T771zbilcxBxiAs659x/OAAQJIswsLMTEzBR/UczMxC51TMxCzEGE"
    "RaR39WB3b9N7nyTJkLu2tua9t9ZefLx69GYbgIgyc82hJqlrqYiriuuaK+Kqkop4JXUVcU3C"
    "HIhFJODsCxF57xu/RBT7BuDb958SNGgQUZYgEogDs5AE4UAcSEREk6QWUWbhoCGEENQDZVmm"
    "abq6ujrkMnMIIdZ5t31vsUC3+l+JaMyxAFRVVRds0C1azsS6O273hH24cwq0UjIGipP9/t+f"
    "6vZ7st9fKQpf/FqJ28+iEzoTF8Dx0RNflmlZpmV5fPR4lkdmzffwdGe8XyZ3Luh83Ll0k3vx"
    "4/dWf3+B/Q2OGQwGGxsbeZ5nWfbi2efXB1sA4uozZjRKDaAwRqGmvTCNGQ3F26eHz1/d7/V6"
    "eZ6fn5/f1bogCmhsonU+9AWY5nr0bjCtKS6LtrltGcQQ1MCMCiEm1MmtWUwETh6mjq1qw0Jd"
    "fmPD1ADQEWPYNyD6HBs2U2Vu4bIoEBpWE0EE6ej68NaoSBdXRi/8SR/a6qE29830yKFmm2c6"
    "2fTbp8FYN/0evPw0U6UuTXB39zYvLy+vr68XY2VZNv5imuB679fX10MT8Xyy1k58P4yVJEn8"
    "9/93OQBFURRFsRTcWH8An5lwqISXsWUAAAAASUVORK5CYII=")
""" VS2005 unfocused docking guide window down bitmap. """

#----------------------------------------------------------------------
left_focus_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACVElE"
    "QVRIibWWvW8TQRDF3+7Ors8ShSsaSpo0dEgoFcINVChSBFRUkajpIKKgiPgP0pqGJiAhITqE"
    "FIk2BQUVHT2VK+y7ndmhWN/5Ixcbh8tYWvtO8vvdm5mdPXPv+RmuMgjA670/RGSttdZ2q354"
    "YgkAERVF4b3vHABMCIC11nsfQiCiqwJYa4noxbNvOw/6AJIk62ySJMLMwhI5MnPMnxzMzJHJ"
    "E0dmicxJhEXk+uTO0fFuCME5h1yDxbh5+zEz93q+LGOv50WUmStOVZSqkjJyWXJVcRm5LKWM"
    "3PNURq6iMKfIIpJw9n08Hg8Gg36/3wL4+eu3iHpykcWTS5pElCWJpMiJWaIk4RQ5RRERda4S"
    "UWbhpCmllDQA0+k0pZQFVwF3bzEAZ5N3jgje+0COnPVknbUAdm5cW5/1/eGPxcuL2saoAczC"
    "DQWAV0/fr1c/HxcBFNC8QGEMMu3NuyddAfIjG9QLjKJTB3NIHV050EZuoQI6+93q4P7B6TYA"
    "A2gW1xlC61K0OXi492HZ6EbAnGFqEmBmhlYc7A9HutRq/wgA5plSwDT9tORgfzgCNsmv2QfQ"
    "OvEwps7BooOPpwebxFsB83wazdWdl321BjOGWWejrciZ0+wBMwef76LPnx6trXFrivIfVOsl"
    "P2V7FwH4MhpuCTBLX7mjckU628naTImlrdDdLDJ59OT+XDDU8SwyTX+Y2bC7hIPVA+fty6/b"
    "SmwBODreHY/H0+n0P0WLomjegJYAIYTBYNAcp5cOa20IoQXgnMuvAh0GATg8scAEmHQrneMv"
    "3LAo6X/e0vAAAAAASUVORK5CYII=")
""" VS2005 focused docking guide window left bitmap. """

#----------------------------------------------------------------------
left_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACTklE"
    "QVRIibWWPWsUURSG3/u5u8RiKxtLmzR2gqQSttFKhKBWqQL+BQXL4D9IGxsrBUGEFCIEbC0s"
    "rOzshYHt3Jl7PizuzsduJhs3Ts7C3Z2BfZ95zzn33DGnp6e4zvAAdnZ2vPfWWmvtsOpFUXgA"
    "3vvxeBxCuC6AtTaEEGP03g8LQE5RTo73/sXzr7sPJwCExTorLMxExMSJEhGl/MlBRJTIB0+J"
    "iBORMBMz3/xz7+h4L8bonFsCunH77lMiGo1CWabRKDArEVUkVeKq4jJRWVJVUZmoLLlMNAq+"
    "TFQlJpJEzCz49n0+n0+n08lk0gP4+es3swbvEnHwTlSYlViYJZEQcWJhkkSSmJnVuYpZiZhE"
    "RUREI7BYLESkTVE37t8hAM5KcM57hBCid97Z4K2zFsDurRubk74/+9G9vKhtjBrAdG4oALw6"
    "eLdZ/XxcBFBA8wKFMci012+fDQXIj2xQLzCKQR20kDqGcqCNXKcCuvzd6+DB4dk2AANoFtcl"
    "QutS9Dl49Pj9qtFLAS3D1CTALA2tOdifnehKq/0jAGgzpYBp+mnFwf7sBLhMfsM+gNaJhzF1"
    "DroOPpwdXibeC2jzaTRXty37eg2WDLPJRl+RM6fZA6YFn++iTx+fbKxxb4ryH1TrJT9lfxcB"
    "+Hwy2xJgVr5yR+WKDLaTtZkSK1thuFlk8ujJ/dkxNPAsMk1/mOWwu4KD9QPnzcsv20psATg6"
    "3pvP54vF4j9Fx+Nx8wa0AogxTqfT5ji9clhrY4w9AOdcfhUYMDyAoiiKohhWt4m/9Qss43IB"
    "CBMAAAAASUVORK5CYII=")
""" VS2005 unfocused docking guide window left bitmap. """

#----------------------------------------------------------------------
right_focus_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACWElE"
    "QVRIibWWv2/TQBTHv3e+uyRbJwZWFv4AJNSRLjChSkhlYqrEzFZVDAwVC3PXsrAUISTExlKJ"
    "tQMSWzcmFqaqQqT2+8VwtuMkbiBp+mzF0pPz/dzX7z373IMXp7jJCABebf8JIXjvvffrVd8/"
    "9gFACGE4HMYY1w4AxgGA9z7GmFIKIdwUwHsfQth7/vXuoxEAFfWFV1ERZhYWYmJmykcOZmbi"
    "EAMTsxCzirCI3BrfPzjcTCkVRYFcg27cubfDzINBLEsaDKKIMXPFWpFUlZTEZclVxSVxWUpJ"
    "PIihJK5ImJVYRBSn387Pzzc2NkajUQ/g7McvEYuhIJYYCjUVMRYVUWJlFhIVVmIlERErikrE"
    "mIXVVFXVEnB5eamqWXAW8Gb39uKHevbzNwARZVFirUSIlFkqEVUD8Pb71P1Lt83LZ+8BAA7O"
    "AYABMAPcFfcvDXj97ikA5wxmHVVrf64LyA7Mau1so770uVjRQa1lzaKtSc2ZWAR4uHsyn2xq"
    "YBnjbFp4zsRCBw6Ptz/M5GoHgLla15AfUV8F/gEwA/Bk66jPgXNwMNhkyf199F816DIaB5bx"
    "yB2aO2qFLsp/+Xiy22YmczA1Cq4hLQlwsK56xwHgumLWln0pgPv8aWcmNdVF7TKujkWAL0db"
    "88nagXWb0xYgVn4XWf0CymdzWQNgapJzWC7HCnPQF5M5aBhXzthqgMkcoF57Zxx6YvaDMzO3"
    "148pwMHhJhFdXFwQ0XVEh8NhuwOaAqSUUkoxxvaLulp471NKPYC80ci7gXVFALB/7IExMF6j"
    "bht/AXIQRaTUgkiHAAAAAElFTkSuQmCC")
""" VS2005 focused docking guide window right bitmap. """

#----------------------------------------------------------------------
right_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACVElE"
    "QVRIibWWv2sUQRTHvzM7M3dHmlQWtjb+AYKkTaOVCEKsrAL+CxaWwcY6bWysRAQRUtgEbC0E"
    "u3RWNsJCCILZfb8sZvdu925zej/yveMWHnvvM9837+2OOz09xU0qANjZ2QkheO+999vNXpZl"
    "ABBCGI/HMcabAnjvY4wppRDCdgHIJcrFCSG8eP7l7sMJABX1hVdREWYWFmJiZsqfLGZm4hAD"
    "E7MQs4qwiNz6c//oeC+lVBRFA+jqzr0DZh6NYlXRaBRFjJlr1pqkrqUiriqua66Iq0oq4lEM"
    "FXFNwqzEIqL4+u3i4mJ3d3cymQwAzn/8ErEYCmKJoVBTEWNRESVWZiFRYSVWEhGxoqhFjFlY"
    "TVVVLQFXV1eqOitRV68Pby+v6fnP3wBElEWJtRYhUmapRVQNwJvvvftXbpuXz94BABycAwAD"
    "YAa4a+5fGfDq7VMAzhnMOllt+rMpIDswa3JnG81lyMWaDppc1i7a2tCCiWWAB4dni8F2Dyxj"
    "nPUTL5hY6sDh0eP3c7HGAWCuyWvIJRragX8AzAA82T8ZcuAcHAw2W/JwH/3XHnQZrQPLeOQO"
    "zR21Rhflv3w4O5xGZnPQGwXXklYEOFg3e8cB4LrJbLrtKwHcp48Hc6FeF02Xcb2WAT6f7C8G"
    "GwfWbU5bglj7WWTNAyh/28sWAL1JzrK8HWvMwZBmc9Ayrp2x9QCzOUCz9s44DGj+hTM3t5ur"
    "Bzg63iOiy8tLItok6Xg8np6AeoCUUkopxjh9o64n731KaQCQDxr5NLAtBQBlWZZlucWkXf0F"
    "imtJnvbT2psAAAAASUVORK5CYII=")
""" VS2005 unfocused docking guide window right bitmap. """

#----------------------------------------------------------------------
tab_focus_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAIAAADZ8fBYAAAAA3NCSVQICAjb4U/gAAAC10lE"
    "QVRIidWWT0gUcRTH387+ZveXZgzsbmvSsmqEfzBJSYz+gUsHCYJgISPytCQKFhJdpIN0qIUO"
    "ezIUaU/roQ5eEzp46ZT/DhG4haCXdSUPK+Wuzvze+02HgdFmFqMtD76Bx8yb3/v8vr/3Zn4z"
    "np6ReTgCYwAwdqfEGFMURVGU/wIdfaswAGCMcc5VVf1fXIBdBgCKoqiq+nxkobn3BABIkgBA"
    "hIiEJFAgorAOyxARBTKVoUAkgSiJkIhO73a/nLjGOd/nWkrPXbqLiH6/CgBEJiIaKA1BhkG6"
    "QF1Hw0BdoK6TLtCvMl2gIQhRCiQiCfPLm5ubtbW1YNXXtuzadyJTZV4AkKYkMpEkkRQoEUmQ"
    "JJQCpSAiMr1eg8hEJJSmlFJK0wdQLBYR0cl9laj7l6LGY5/tc2ejsrmdgeGJbG5nYHgym9uJ"
    "x9KHeGuMNd7B8fSMzCfvyerq6rHHn2bmEgPDE09G+/9WaSqZmRofisfSiadnotHoozclp94K"
    "oGWznNxn/e8q4LqznNwXmb4KuO6s4643lZyugOvOcj8PDyrgurOOe30r05tKZv7ALavXmszt"
    "rXZZL7EjhTmuU8lpRxNSyemZuUEAmJlLOPzU+CAAuKFluO7OWpF4LO1OPsTcejOOTcRepqXR"
    "tngs7Y6U4bbcqNrIF6bGh6yt0prAgm7kC6E2fSNfWF9b2d7e1jStvqGlbMSmeRsuP7zZZvp8"
    "PvCoW1s/a2qq7vddD57y3b7VZfmNfGFxadUQBgqztbWps7Pdy04uLq0WSyVJnoMRgUY45NM0"
    "bXZZ7OvtaA8vLOdeT85mP+4eXN35K/6W5nBjxFz5tv7+w8LWF3+oTW+IBpsavStf1+xIfTTY"
    "cNbknDPGfqsD5/xCa6AuDFe791xtEJyHIhHedTGw17tnj49EeFdH8GAkEAhwzgF+7HMZY5qm"
    "cc6tD6rDGGOMMUS075aN2Ho9R/R/9gsXZ7dKHM+ODQAAAABJRU5ErkJggg==")
""" VS2005 focused docking guide window center bitmap. """

#----------------------------------------------------------------------
tab_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAIAAADZ8fBYAAAAA3NCSVQICAjb4U/gAAAC1klE"
    "QVRIidWVTWgTQRTHJ5vZZEyMLKSx1RbSImJbioeiCKIechLBU8CCtadAaaGIFC/iQTxowENO"
    "hUohp/Tiocdce/Gk/TiIpTm0JCnmA+OaFJs2u/PerIcp27IbKsZ66Ft47P5n3m/evLc768lm"
    "s+Q/GCWEBINBSqmiKIqinApU13VKCKGUMsZUVT1lrqIoqqq+frYyeP8cIUSgIIQgAgACcuAA"
    "wOUlDQCAA1UpcADkAAIREPHiwa2383cYY0TWwa7AlRuPAMDvVwkhiBYAmCBMjqaJBgfDANME"
    "g4NhoMHBr1KDg8kRQHBAREE+r1er1Z6enkOubbn8d0RLpV5CiLAEogUoEAUHAYAcBYLgIDgi"
    "ouX1mogWAIKwhBBCWD5Cms0mADi57xKX/6Ws8dgX+97ZqFxpb3JmPlfam5x5nyvtxWPpE7yc"
    "I+c7OJ5sNhsOh4PB4Kunn5aWE5Mz87MvJv4201QyszA3HY+lE88vRaPRYrHozLcDaNsoJ/fl"
    "xIcOuO4oJ/dNZqwDrjvqrOebSi52wHVHud+HJx1w3VFnvb6d5ZtKZv7AbZuvXMztZbvkR+wI"
    "oY7nVHLR0YRUcnFpeYoQsrSccPiFuSlCiBvahuvurFTisbQ7+ARz55txHCL2NmWOtsVjabfS"
    "hjt0L1Cu1BfmpuVRKReQ0HKlHhkxypV6Ib/ZaDQ0TesfGGqr2DTv+Ph4IBDw+XzEo9Zqv0Kh"
    "wOOxu10XfA8f3JS+XKmvrm2Z3ARuDQ9fGx297qXnV9e2mvv7Aj3HFQ5md8Snadru7u7Rua6q"
    "6sp6aTNXzX08OL67q7f9Q4PdTP1ZKCn5Qq321R8ZMQaiXf19VuGbJ1/8IZX+aNdAnxWJRHp7"
    "e7e3t4+4oVCo0Wjout5qtdx9YIwxxlqtlj3aVgmHw5qmbWxsHNWXUqppGmNM/lCd/aWUUgoA"
    "9mhbhTFGKT3sm67ruq7v7Oy4cR3bb5uW079be13FAAAAAElFTkSuQmCC")
""" VS2005 unfocused docking guide window center bitmap. """

#----------------------------------------------------------------------
up_focus_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACTUlE"
    "QVRIic2WP28TMRjGH/85c1miqEF8CnbUgSFdukVRmZGQ+gW6Vgwd+hW60Yq1gMQMQzpHGZAg"
    "C6JS+QIMmUju/L5+Ge6ulzoRTcMh5TmdZfv8/vT4Pcu26h2N8R9kAZwMfltrtdZa60agx5fa"
    "ArDWpmmaJElTXGBmAWitkyRxzllrG+Zqra21bz+OAQQOzETExJ48EfniKURE5MkmljwRe6LA"
    "TMz8ZPbs9GzXOWeMQZHfW33/NOufvALALESUU8g95zlnnrKM8pwyT1nGmadHic085Z6Jgidm"
    "Dhh/mU6nnU6n1WrFXAA/fv7iIEECsxAH5uApELHnwBQ8Bc/MLMbkzELEFCSEEII4YD6fhxAK"
    "Tsx9/tQDEIgqOzRggAQQQEEBguIFgKoNqDdfvy1yYq41emG4QKkSpDQAiNQfFQClpBoZcaK2"
    "s0awEHzXVVyri1gxN7FaFuILu6qwtAyokqWWwEvcxNTTKsIK95Cqs4JJzV02vMJvHS/1cFFQ"
    "UGV+K3tSzWlZq/5bOWGllIio0mzpX+pZSJXdVRmOuabcItRC+ZfKcn+pFRvN65fvNihj9Y7G"
    "o9FoMplcX18f9M5lUx30zofD4WQyubm56R2Nm9oYY20B98XeRfPcAro+ei1uf/DBt9u+3c7b"
    "7f7gfTPc/cOr7HE36+5k3Z28u5N1u/uHV/dG3X+gfb7YW8dgpC1YD1vBjfP7oEW6Lvf0bHc6"
    "nc7n881YaZre3pjucJ1znU7n9qx+qLTWzrkVXGNMcav4d1kAx5camAGzRoiF/gCKPmudbgYP"
    "HQAAAABJRU5ErkJggg==")
""" VS2005 focused docking guide window up bitmap. """

#----------------------------------------------------------------------
up_single = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACTklE"
    "QVRIic2WP4vUQBjGn/mTMUtgWS6yvb29XGGzzXXHwdWCcGBzH8BCweK+wnWyWKtot6DNge0V"
    "gjYnNn4BA9vdJvO+81ok2ewmi7d3RtgnZEgm8/545skwiZrNZvgPsgCSJLHWaq211r1Asyyz"
    "AKy1cRxHUdQzV2sdRZFzzlrbCxdlDmUC1to3Hy8BBA7MRMTEnjwR+fIoRUTkyUaWPBF7osBM"
    "zDy+fnR2vu+cM8ZU3KV+fLo+fPUUALMQUUGh8FwUnHvKcyoKyj3lOeee7kU291R4JgqemDng"
    "8ut8Ph+NRoPBoM0F8PPXbw4SJDALcWAOngIRew5MwVPwzMxiTMEsRExBQgghiAMWi0UIoclh"
    "VY8fegACUVWHBgwQAQIoKEBQngBQ3wPq9bfv7XzX7o1eGS5QqgIpDQAizUMFQCmpR3bf26qc"
    "NYKV4nVX7aumaavNjayWlfrSriotdQF1WKoD7nAj00yrLCvdQ+rOGiYNt2t4g9+mXprhoqCg"
    "qnxre1LPqatN762asFJKRFRltvIvzSykTndTwm2uqbYItdL+5aLbX2nDRvPiyds7tC2p2WyW"
    "pmmSJHEcP3/25cPFSXfQNjqeTE9fPhiPx0mSXF1d9bMxdrUD3OPJtH9uCd0evRX38Oi9Hw79"
    "cFgMh4dH7/rhHpxc5PfTPN3L070i3cvT9ODk4saqmz9on6eTbQy2tAPrYSe47XxvtUi35Z6d"
    "78/n88VicTdWHMfLP6Y1rnNuNBotv9W3ldbaObeBa4wp/yr+XRZAlmVZlvWCW+oP2FUt8NYb"
    "g5wAAAAASUVORK5CYII=")
""" VS2005 unfocused docking guide window up bitmap. """

#----------------------------------------------------------------------
down = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACFUlE"
    "QVRIidWVPWvbUBSG3+tv8KKpnYtH/4DuJtCti2nntBm7depQWih0zT9w/AtSQsDQ0JIfkKFD"
    "wRC61Iu3uBgRiKXz1eFalizb8QfxkFdCurofz3l1zhVyg8EAe1BhH9BHyC3NWkTU/XYFQEVF"
    "mFlYiImZyR9ezMzEpXKJiVmIWUVYRJ7cPT/uHizhFgqF6+93Lz8fAhAxZo5ZY5I4log4ijiO"
    "OSKOIomIq+VSRByTMCuxiCiufo3H4yAI8txisQjgz98bUVNTEWNRESVWZiFRYSVWEhGxYjEW"
    "MWZhNVVVtQoQhuESrtfXw6e7JbTd+k1E6dv3+/3dQPeo3+8/3n22Si+OLgFLn52D4aLTun/V"
    "er8XnVZ1NKqM/lX9eTNaC92IC+D87HUlDMthWA7D87NXmyzZNL+nl0ez60Nyt4Jux91Kee71"
    "8Lbd6uxwzXFcr9drNpv+4f2bn59O2gDMAMC5ZJY5wOCcwZxlV7tkKr68PX338Vmj0cBev7f8"
    "d0GkSG0i0576Alza7707LGqBy2JZblYOPgnm4JJA8Blay41ZnAfO3xbumWjTQOv8+oKZA2AJ"
    "Y1o3wPucGXYLYVZwWQzQlJWmwIMs6Z8OJUHWcUU1aWZ9WKaGlo67xZlTbbbPbL7oq7fBTHm/"
    "Jx9+bBRpnea4x92D4XA4mUx2Y9VqteVcAEEQ1Ov13bhZ5fP7IFB4v/v41f8HFQ1ap0nfm7YA"
    "AAAASUVORK5CYII=")
""" VS2005 unfocused docking guide window down bitmap. """

#----------------------------------------------------------------------
down_focus = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACaUlE"
    "QVRIib2WvWsUQRjGn5mdnWxyTaqz9q+QlLnGToSgWAYDNjbpNCAGDGIvaRPbNJGQyiAEbK+w"
    "sAo2qexyEhbxsvt+jMXc3u3liPfhmWeXnWVm9vc+vO/M7prVzTb+gxyA7Ye/nXPWWmvtXKBb"
    "B9YBcM5lWZam6by4QNcBsNamaeq9d87NmWutdc59+NgGoKIizCwsxMTMFI8oZmZilzomZiFm"
    "FWERaXbv7eyueO+TJEHM79LSkvfeWnv2qftgex2ASGDmkrUkKUspiIuCy5IL4qKQgnghdQVx"
    "ScKsxCKiaH8lIu99NOwAEFGsG4Dv5xeiQYOKBBYVUWJlFhIVVmIlEZGQJKVIYBbWoKqqwQN5"
    "nqdpuri42OMys6rGOG/X78yW0bXWNyLqcyyAEEIIYcYK3aB5Lazb4o5fsPc3ToFaloxBwMle"
    "6+9Pjfd7stda6HR85+dCPC86Y6ETcQEcHz32eZ7meZrnx0ePJnlk0vwenm70r/PkTgWdjjuV"
    "rnPPfvxaa+3NcL3GMaub7XdPtNFoZFn24tmX1/trAOLuM6aaFQwQYExAMPWNaUw1FW+eHj5/"
    "dbfZbDYajY33F7e1L4gUA5uo3fd8AWbQH70bjGqEyxLq3LoMYhKCgakCIWZoLLdkMRE43Iy0"
    "tWi9QOP8xoIFAyBUjF7dgOizb9iMhLmByxIAHbAGKYigUPX3hqog47hSvfCHfYRaDcNg3IzO"
    "7GmydRaGi37zMujrut/9l58nijROQ9yd3ZXLy8urq6vZWFmW9f+Yhrje++XlZR2keDpZa4f+"
    "H/pKkiR+/f9dDsDWgQW6QHcuxKg/ZbVtCjjzINkAAAAASUVORK5CYII=")
""" VS2005 focused docking guide window down bitmap. """

#----------------------------------------------------------------------
left = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACMElE"
    "QVRIib2WPYsTURSG3zv3ThKJRSqblDYLwU6wFMKCViIEtbKQ/QdWgrXt/oO4hZWCIEIKUfYH"
    "WFgIATuraewHM3PPh8XNZCaTSWI2oydwMx/kfeY959wzMbPZDC3FaDTavOi23Wgron8n/Z8A"
    "rnry/NmXk/vXAAhLZCNhYSYiJvbkiciHTwgiIk8uduSJ2BMJMzHzjd93zi9OmwEAbt5+TETd"
    "bpxlvtuNmZWIcpLcc55z5inLKM8p85RlnHnqxi7zlHsmEk/MLPj6LUmS4XDYDPjx8xezxs56"
    "4thZUWFWYmEWT0LEnoVJPIlnZlZrc2YlYhIVERHtAIvFYquDu7cIgI0kttY5xHHccdbZKHaR"
    "jSIAJ8Pru5M+GX+vnm4rslEDmMoFBYCXT9/uVt+MbQAFNCxQGINAe/XmSVuA8MgGxQKjaNVB"
    "CSmiLQe6kqtUQJfHjQ7unV0eAjCABnFdIrQoRZODBw/frRvdCygZpiABZmmo5mAynupaq/0l"
    "ACgzpYBZ9dOag8l4CuyT37EPoEXiYUyRg6qD95dn+8QbAWU+jYbqlmWv12DJMLtsNBU5cFZ7"
    "wJTgzS76+OHRzho3pij8QLVYwlM2dxGAT9PxgQCz9hU6KlSktZ2sqymxthXam0UmjJ7QnxVD"
    "Lc8is+oPsxx2V3BQf+G8fvH5UIkDAOcXp0mSVF94V4ter5emab/frwMADAaDcOOYSNO00+mE"
    "4zrgePWaiAMwn8+PF932//MPv0Uk8OspzrYAAAAASUVORK5CYII=")
""" VS2005 unfocused docking guide window left bitmap. """

#----------------------------------------------------------------------
left_focus = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACVElE"
    "QVRIibWWvW8TQRDF3+7Ors8ShSsaSpo0dEgoFcINVChSBFRUkajpIKKgiPgP0pqGJiAhITqE"
    "FIk2BQUVHT2VK+y7ndmhWN/5Ixcbh8tYWvtO8vvdm5mdPXPv+RmuMgjA670/RGSttdZ2q354"
    "YgkAERVF4b3vHABMCIC11nsfQiCiqwJYa4noxbNvOw/6AJIk62ySJMLMwhI5MnPMnxzMzJHJ"
    "E0dmicxJhEXk+uTO0fFuCME5h1yDxbh5+zEz93q+LGOv50WUmStOVZSqkjJyWXJVcRm5LKWM"
    "3PNURq6iMKfIIpJw9n08Hg8Gg36/3wL4+eu3iHpykcWTS5pElCWJpMiJWaIk4RQ5RRERda4S"
    "UWbhpCmllDQA0+k0pZQFVwF3bzEAZ5N3jgje+0COnPVknbUAdm5cW5/1/eGPxcuL2saoAczC"
    "DQWAV0/fr1c/HxcBFNC8QGEMMu3NuyddAfIjG9QLjKJTB3NIHV050EZuoQI6+93q4P7B6TYA"
    "A2gW1xlC61K0OXi492HZ6EbAnGFqEmBmhlYc7A9HutRq/wgA5plSwDT9tORgfzgCNsmv2QfQ"
    "OvEwps7BooOPpwebxFsB83wazdWdl321BjOGWWejrciZ0+wBMwef76LPnx6trXFrivIfVOsl"
    "P2V7FwH4MhpuCTBLX7mjckU628naTImlrdDdLDJ59OT+XDDU8SwyTX+Y2bC7hIPVA+fty6/b"
    "SmwBODreHY/H0+n0P0WLomjegJYAIYTBYNAcp5cOa20IoQXgnMuvAh0GATg8scAEmHQrneMv"
    "3LAo6X/e0vAAAAAASUVORK5CYII=")
""" VS2005 focused docking guide window left bitmap. """

#----------------------------------------------------------------------
right = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACMklE"
    "QVRIibWWvY7TUBCFz83vojSuKNiShgdAol8hQYWQkJaKAuUNtqWmoeANFgoqhJAQHRLaB6BA"
    "orC0HWnSUEURK2LPmRmKayeO4wTysydWbI+c+e7xzDgOo9EIK0rTdDW4m0Ij4FBK07R1fdmj"
    "rh3QqZ6cPf965+ENAKbWardMTZWkUoVCUuIniiSFnW6HQqqQpkpVvfnn3uu395sBAG7fPSXZ"
    "73ezTPr9rqqTzGm5aJ5rJswy5jkzYZZpJux3O5kwFyVNqKqGb9/H4/Hx8XEz4PLnL1XvdtpC"
    "7Xba5qbqVFM1oZEqakoTmqiqerudqzqpNDczM+8Bs9lsrYNXw1ub7+nl+DcAVaOa0HJVESM1"
    "VzVzAG9+LF2/dZFfPHsPAAgIAQAcgDsQ1ly/NeDlu6cAQnC4V7L6/GtfQHTgXuSONopdk4sd"
    "HRS5vFy0l6EVE5sAD4YXq8GyBh4xwZcTr5jY6CDg0eMPtVjhAPBQ5HXEW9RUgX8A3AE8OTlv"
    "chACAhy+WHJzH/1XDaqM0oFHPGKHxo7aoYviTz5eDOeRxRwsjUIoSVsCAryaveIACNVkPi/7"
    "VoDw+dNpLbTURfNlrNcmwJfzk9Vg4cCrzekbEDs/i7x4AMWt3B0AsDTJUR7LscMcNGkxByVj"
    "7YztBljMAYq1V8ahQfU/nNrc7q/6e9FkMplOpyKyT9Kjo6MkSQaDQZqmdQdJkiRJsk92AFdX"
    "V71eLx7XAQfRYDCYH68FHOr19C8Ad0k9S0aHzwAAAABJRU5ErkJggg==")
""" VS2005 unfocused docking guide window right bitmap. """

#----------------------------------------------------------------------
right_focus = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAdCAIAAABE/PnQAAAAA3NCSVQICAjb4U/gAAACWElE"
    "QVRIibWWv2/TQBTHv3e+uyRbJwZWFv4AJNSRLjChSkhlYqrEzFZVDAwVC3PXsrAUISTExlKJ"
    "tQMSWzcmFqaqQqT2+8VwtuMkbiBp+mzF0pPz/dzX7z373IMXp7jJCABebf8JIXjvvffrVd8/"
    "9gFACGE4HMYY1w4AxgGA9z7GmFIKIdwUwHsfQth7/vXuoxEAFfWFV1ERZhYWYmJmykcOZmbi"
    "EAMTsxCzirCI3BrfPzjcTCkVRYFcg27cubfDzINBLEsaDKKIMXPFWpFUlZTEZclVxSVxWUpJ"
    "PIihJK5ImJVYRBSn387Pzzc2NkajUQ/g7McvEYuhIJYYCjUVMRYVUWJlFhIVVmIlERErikrE"
    "mIXVVFXVEnB5eamqWXAW8Gb39uKHevbzNwARZVFirUSIlFkqEVUD8Pb71P1Lt83LZ+8BAA7O"
    "AYABMAPcFfcvDXj97ikA5wxmHVVrf64LyA7Mau1so770uVjRQa1lzaKtSc2ZWAR4uHsyn2xq"
    "YBnjbFp4zsRCBw6Ptz/M5GoHgLla15AfUV8F/gEwA/Bk66jPgXNwMNhkyf199F816DIaB5bx"
    "yB2aO2qFLsp/+Xiy22YmczA1Cq4hLQlwsK56xwHgumLWln0pgPv8aWcmNdVF7TKujkWAL0db"
    "88nagXWb0xYgVn4XWf0CymdzWQNgapJzWC7HCnPQF5M5aBhXzthqgMkcoF57Zxx6YvaDMzO3"
    "148pwMHhJhFdXFwQ0XVEh8NhuwOaAqSUUkoxxvaLulp471NKPYC80ci7gXVFALB/7IExMF6j"
    "bht/AXIQRaTUgkiHAAAAAElFTkSuQmCC")
""" VS2005 focused docking guide window right bitmap. """

#----------------------------------------------------------------------
tab = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAIAAADZ8fBYAAAAA3NCSVQICAjb4U/gAAACq0lE"
    "QVRIidWWTWgTQRTHJ+3ETEugERrtF6QhFhKsIlgQRITm5LkBvdiDhBZKc5DiRXryoAEPPRUi"
    "pTnVi4cee5NePAitFtFoVxSyheYDa02KCd3deW/Gw2Cy7MZaIz307TK7/Gfeb9587Nvx6LpO"
    "TsA6TgJ6glyqHgcHB4/ub0ZvdRFCBApCCCIAICAHDgBcXcoAADhQLwUOgBxAIAIinju89iRz"
    "gzHW5Pb09BBCImO3AcDn8xJCECUAWCAsjpaFJgfTBMsCk4NposnB56UmB4sjgOCAiIJsbJXL"
    "5b6+PsYYtQev5b8hSi/tJIQIKRAloEAUHAQAchQIgoPgiIiys9NClAAIQgohhJBnCKnX6wDQ"
    "jFfZ0+TA/8xpIv6+8e5cN61Qm05ltEJtOvVMK9QS8ewRpWqj2js4nsb+nbv3cnU9OZ3KzD2c"
    "/NdIF9IrS4sziXg2+aA/FAr5/X5nvG1AW3o5ufOTL9rgur2c3Mcrd9rgur1Oe7wL6edtcN1e"
    "7v1wtw2u2+u0z2978S6kV/7CbRmv6sxdquVSH7HTR/9tE+PLUsqp2cz27k/7PTWbkcezifHl"
    "tbW1XC6n6zp1dONeWaUk4tnjTwtx5F81KEcSaQxzdT1p1xPxrFtpwY3d7C6WKkuLMypVqg4U"
    "tFiqBEfNYqmi57er1WogEBgOx1oqDVoz/77e2Onu6hq7emGg/6w9imKp8ubt149a/mI0rGqV"
    "8u7DlyuXRuzKp8/5yzG/yr9NrmEYm1uFba2svTq0c0eu+2LR88z7Qy905PW9vZwvOGqGQ73D"
    "Q1Lf9eR3vitlONQbHpLBYHBwcJAx5rGfd6rV6v7+vmEY7nVgjDHGDMNo1LZUIpGIc34ppYFA"
    "gDGmfqgOo5RSSgGgUdtSUSUANLmqWp0q/mTK82hFcX4Bm24GMv+uL+EAAAAASUVORK5CYII=")
""" VS2005 unfocused docking guide window center bitmap. """

#----------------------------------------------------------------------
tab_focus = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAIAAADZ8fBYAAAAA3NCSVQICAjb4U/gAAAC10lE"
    "QVRIidWWT0gUcRTH387+ZveXZgzsbmvSsmqEfzBJSYz+gUsHCYJgISPytCQKFhJdpIN0qIUO"
    "ezIUaU/roQ5eEzp46ZT/DhG4haCXdSUPK+Wuzvze+02HgdFmFqMtD76Bx8yb3/v8vr/3Zn4z"
    "np6ReTgCYwAwdqfEGFMURVGU/wIdfaswAGCMcc5VVf1fXIBdBgCKoqiq+nxkobn3BABIkgBA"
    "hIiEJFAgorAOyxARBTKVoUAkgSiJkIhO73a/nLjGOd/nWkrPXbqLiH6/CgBEJiIaKA1BhkG6"
    "QF1Hw0BdoK6TLtCvMl2gIQhRCiQiCfPLm5ubtbW1YNXXtuzadyJTZV4AkKYkMpEkkRQoEUmQ"
    "JJQCpSAiMr1eg8hEJJSmlFJK0wdQLBYR0cl9laj7l6LGY5/tc2ejsrmdgeGJbG5nYHgym9uJ"
    "x9KHeGuMNd7B8fSMzCfvyerq6rHHn2bmEgPDE09G+/9WaSqZmRofisfSiadnotHoozclp94K"
    "oGWznNxn/e8q4LqznNwXmb4KuO6s4643lZyugOvOcj8PDyrgurOOe30r05tKZv7ALavXmszt"
    "rXZZL7EjhTmuU8lpRxNSyemZuUEAmJlLOPzU+CAAuKFluO7OWpF4LO1OPsTcejOOTcRepqXR"
    "tngs7Y6U4bbcqNrIF6bGh6yt0prAgm7kC6E2fSNfWF9b2d7e1jStvqGlbMSmeRsuP7zZZvp8"
    "PvCoW1s/a2qq7vddD57y3b7VZfmNfGFxadUQBgqztbWps7Pdy04uLq0WSyVJnoMRgUY45NM0"
    "bXZZ7OvtaA8vLOdeT85mP+4eXN35K/6W5nBjxFz5tv7+w8LWF3+oTW+IBpsavStf1+xIfTTY"
    "cNbknDPGfqsD5/xCa6AuDFe791xtEJyHIhHedTGw17tnj49EeFdH8GAkEAhwzgF+7HMZY5qm"
    "cc6tD6rDGGOMMUS075aN2Ho9R/R/9gsXZ7dKHM+ODQAAAABJRU5ErkJggg==")
""" VS2005 focused docking guide window center bitmap. """

#----------------------------------------------------------------------
up = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACHUlE"
    "QVRIidWWP4vUQBjGn8mfcyGQYiM2W8mWsRcLm22uWw6uFpQt7WwVLPwKVsp+gFMsAwqynY2F"
    "oLAgNu4HsEiz3E7mfee1yN9Lcueu7oo+IcPMZN4fz7yZzEQlSYIDyAMQx/F+ocvl0tkvsdKh"
    "uF6z8eLsAwDLlpmImNiQISKTX7mIiAx5vkeGiA2RZSZmvnF++9nzO0EQ9HC/vj2fPr0PgFmI"
    "KCObGc4y1oa0piwjbUhr1oau+Z42lBkmsoaY2eLjpzRN+7kAvn3/wVasWGYhtszWkCViw5bJ"
    "GrKGmVlcN2MWIiYr1lpr5QjYbDb9eQBw95YBIBBVdDiAC/iAAAoKEOQ3AJRtQL38/OXS/ALw"
    "XKcxXKBUAVIOAIjUDxUApaQcecV7A3DkuYJG8EVX7VpdtNXm+p4jjfjcrsotdQFlslQH3OH6"
    "bj2tPCx3Dyk7S5jU3K7hHr91vNTDRUFBFfkt7Uk5p6763lsxYaWUiKjCbOFf6llImd2+DLe5"
    "ruM0UlA5uazS7S/Usz88vnf2G2VLKkmSap989OD9m8WsO2gbnU7mD5/cHI/H+C/3yR24p5P5"
    "/rk5dHv0VtzpyWsThiYMszCcnrzaD/d4ttDXIx0NdTTMoqGOouPZ4pdR7e+iq3fzyTYGWzrY"
    "etj7zwOAOI7/yjmPHRfpFVKr1apqrNfrNE2bx+pOGgwGo9Eor1/wGwRB9QPwh/oH9oed9BPW"
    "YyQlBOJt4AAAAABJRU5ErkJggg==")
""" VS2005 unfocused docking guide window up bitmap. """
#----------------------------------------------------------------------
up_focus = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAgCAIAAABhFeQrAAAAA3NCSVQICAjb4U/gAAACTUlE"
    "QVRIic2WP28TMRjGH/85c1miqEF8CnbUgSFdukVRmZGQ+gW6Vgwd+hW60Yq1gMQMQzpHGZAg"
    "C6JS+QIMmUju/L5+Ge6ulzoRTcMh5TmdZfv8/vT4Pcu26h2N8R9kAZwMfltrtdZa60agx5fa"
    "ArDWpmmaJElTXGBmAWitkyRxzllrG+Zqra21bz+OAQQOzETExJ48EfniKURE5MkmljwRe6LA"
    "TMz8ZPbs9GzXOWeMQZHfW33/NOufvALALESUU8g95zlnnrKM8pwyT1nGmadHic085Z6Jgidm"
    "Dhh/mU6nnU6n1WrFXAA/fv7iIEECsxAH5uApELHnwBQ8Bc/MLMbkzELEFCSEEII4YD6fhxAK"
    "Tsx9/tQDEIgqOzRggAQQQEEBguIFgKoNqDdfvy1yYq41emG4QKkSpDQAiNQfFQClpBoZcaK2"
    "s0awEHzXVVyri1gxN7FaFuILu6qwtAyokqWWwEvcxNTTKsIK95Cqs4JJzV02vMJvHS/1cFFQ"
    "UGV+K3tSzWlZq/5bOWGllIio0mzpX+pZSJXdVRmOuabcItRC+ZfKcn+pFRvN65fvNihj9Y7G"
    "o9FoMplcX18f9M5lUx30zofD4WQyubm56R2Nm9oYY20B98XeRfPcAro+ei1uf/DBt9u+3c7b"
    "7f7gfTPc/cOr7HE36+5k3Z28u5N1u/uHV/dG3X+gfb7YW8dgpC1YD1vBjfP7oEW6Lvf0bHc6"
    "nc7n881YaZre3pjucJ1znU7n9qx+qLTWzrkVXGNMcav4d1kAx5camAGzRoiF/gCKPmudbgYP"
    "HQAAAABJRU5ErkJggg==")
""" VS2005 focused docking guide window up bitmap. """

# ------------------------ #
# - AuiToolBar Constants - #
# ------------------------ #

ITEM_CONTROL = wx.ITEM_MAX
""" The item in the AuiToolBar is a control. """
ITEM_LABEL = ITEM_CONTROL + 1
""" The item in the AuiToolBar is a text label. """
ITEM_SPACER = ITEM_CONTROL + 2
""" The item in the AuiToolBar is a spacer. """
ITEM_SEPARATOR = wx.ITEM_SEPARATOR
""" The item in the AuiToolBar is a separator. """
ITEM_CHECK = wx.ITEM_CHECK
""" The item in the AuiToolBar is a toolbar check item. """
ITEM_NORMAL = wx.ITEM_NORMAL
""" The item in the AuiToolBar is a standard toolbar item. """
ITEM_RADIO = wx.ITEM_RADIO
""" The item in the AuiToolBar is a toolbar radio item. """
ID_RESTORE_FRAME = wx.ID_HIGHEST + 10000
""" Identifier for restoring a minimized pane. """

BUTTON_DROPDOWN_WIDTH = 10
""" Width of the drop-down button in AuiToolBar. """

DISABLED_TEXT_GREY_HUE = 153.0
""" Hue text colour for the disabled text in AuiToolBar. """
DISABLED_TEXT_COLOR = wx.Colour(DISABLED_TEXT_GREY_HUE,
                                DISABLED_TEXT_GREY_HUE,
                                DISABLED_TEXT_GREY_HUE)
""" Text colour for the disabled text in AuiToolBar. """

AUI_TB_TEXT             = 1 << 0
""" Shows the text in the toolbar buttons; by default only icons are shown. """
AUI_TB_NO_TOOLTIPS      = 1 << 1
""" Don't show tooltips on `AuiToolBar` items. """
AUI_TB_NO_AUTORESIZE    = 1 << 2
""" Do not auto-resize the `AuiToolBar`. """
AUI_TB_GRIPPER          = 1 << 3
""" Shows a gripper on the `AuiToolBar`. """
AUI_TB_OVERFLOW         = 1 << 4
""" The `AuiToolBar` can contain overflow items. """
AUI_TB_VERTICAL         = 1 << 5
""" The `AuiToolBar` is vertical. """
AUI_TB_HORZ_LAYOUT      = 1 << 6
""" Shows the text and the icons alongside, not vertically stacked.
This style must be used with ``AUI_TB_TEXT``. """
AUI_TB_PLAIN_BACKGROUND = 1 << 7
""" Don't draw a gradient background on the toolbar. """
AUI_TB_CLOCKWISE        = 1 << 8
AUI_TB_COUNTERCLOCKWISE = 1 << 9

AUI_TB_HORZ_TEXT        = AUI_TB_HORZ_LAYOUT | AUI_TB_TEXT
""" Combination of ``AUI_TB_HORZ_LAYOUT`` and ``AUI_TB_TEXT``. """
AUI_TB_VERT_TEXT        = AUI_TB_VERTICAL | AUI_TB_CLOCKWISE | AUI_TB_TEXT

AUI_TB_DEFAULT_STYLE    = 0
""" `AuiToolBar` default style. """

# AuiToolBar settings
AUI_TBART_SEPARATOR_SIZE = 0
""" Separator size in AuiToolBar. """
AUI_TBART_GRIPPER_SIZE = 1
""" Gripper size in AuiToolBar. """
AUI_TBART_OVERFLOW_SIZE = 2
""" Overflow button size in AuiToolBar. """

# AuiToolBar text orientation
AUI_TBTOOL_TEXT_LEFT = 0     # unused/unimplemented
""" Text in AuiToolBar items is aligned left. """
AUI_TBTOOL_TEXT_RIGHT = 1
""" Text in AuiToolBar items is aligned right. """
AUI_TBTOOL_TEXT_TOP = 2      # unused/unimplemented
""" Text in AuiToolBar items is aligned top. """
AUI_TBTOOL_TEXT_BOTTOM = 3
""" Text in AuiToolBar items is aligned bottom. """

# AuiToolBar tool orientation
AUI_TBTOOL_HORIZONTAL = 0             # standard
AUI_TBTOOL_VERT_CLOCKWISE = 1         # rotation of 90 on the right
AUI_TBTOOL_VERT_COUNTERCLOCKWISE = 2  # rotation of 90 on the left


# --------------------- #
# - AuiMDI* Constants - #
# --------------------- #

wxWINDOWCLOSE = 4001
""" Identifier for the AuiMDI "close window" menu. """
wxWINDOWCLOSEALL = 4002
""" Identifier for the AuiMDI "close all windows" menu. """
wxWINDOWNEXT = 4003
""" Identifier for the AuiMDI "next window" menu. """
wxWINDOWPREV = 4004
""" Identifier for the AuiMDI "previous window" menu. """

# ----------------------------- #
# - AuiDockingGuide Constants - #
# ----------------------------- #

colourTargetBorder = wx.Colour(180, 180, 180)
colourTargetShade = wx.Colour(206, 206, 206)
colourTargetBackground = wx.Colour(224, 224, 224)
colourIconBorder = wx.Colour(82, 65, 156)
colourIconBackground = wx.Colour(255, 255, 255)
colourIconDockingPart1 = wx.Colour(215, 228, 243)
colourIconDockingPart2 = wx.Colour(180, 201, 225)
colourIconShadow = wx.Colour(198, 198, 198)
colourIconArrow = wx.Colour(77, 79, 170)
colourHintBackground = wx.Colour(0, 64, 255)
guideSizeX, guideSizeY = 29, 32

# ------------------------------- #
# - AuiSwitcherDialog Constants - #
# ------------------------------- #

SWITCHER_TEXT_MARGIN_X = 4
SWITCHER_TEXT_MARGIN_Y = 1
