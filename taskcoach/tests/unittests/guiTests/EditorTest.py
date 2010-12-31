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

import wx
import test
from taskcoachlib import gui, config, persistence
from taskcoachlib.domain import note, base
from unittests import dummy


class EditorUnderTest(gui.dialog.editor.NoteEditor):    
    def __init__(self, *args, **kwargs):
        super(EditorUnderTest, self).__init__(*args, **kwargs)
        self.editorClosed = False
                
    def onClose(self, event):
        self.editorClosed = True
        super(EditorUnderTest, self).onClose(event)


class EditorTestCase(test.wxTestCase):
    def setUp(self):
        super(EditorTestCase, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.items = base.filter.SearchFilter(self.taskFile.notes())
        self.item = note.Note(subject='item')
        self.items.append(self.item)
        self.editor = EditorUnderTest(self.frame, [self.item], 
                                      self.settings, self.items, 
                                      self.taskFile, raiseDialog=False)
        self.appearance = self.editor._interior[-1]

    def testCloseEditorWhenItemIsDeleted(self):
        self.items.remove(self.item)
        self.failUnless(self.editor.editorClosed)
        
    def testDontCloseEditorWhenItemIsFiltered(self):
        self.items.setSearchFilter('abc')
        self.failIf(self.editor.editorClosed)

    def testThatPickingAForegroundColorChangesTheItemForegroundColor(self):
        self.appearance._foregroundColorButton.SetColour(wx.RED)
        self.appearance._foregroundColorSync.onAttributeEdited(dummy.Event())
        self.assertEqual(wx.RED, self.item.foregroundColor())
        
    def testThatChangingTheItemForegroundColorAffectsTheForegroundColorButton(self):
        self.item.setForegroundColor(wx.RED)
        self.assertEqual(wx.RED, self.appearance._foregroundColorButton.GetColour())
        
    def testThatPickingABackgroundColorChangesTheItemBackgroundColor(self):
        self.appearance._backgroundColorButton.SetColour(wx.RED)
        self.appearance._backgroundColorSync.onAttributeEdited(dummy.Event())
        self.assertEqual(wx.RED, self.item.backgroundColor())

    def testThatChangingTheItemBackgroundColorAffectsTheBackgroundColorButton(self):
        self.item.setBackgroundColor(wx.RED)
        self.assertEqual(wx.RED, self.appearance._backgroundColorButton.GetColour())
        
    def testThatPickingAFontChangesTheItemFont(self):
        font = self.appearance._fontButton.GetSelectedFont()
        font.SetPointSize(font.GetPointSize() + 1)
        self.appearance._fontButton.SelectedFont = font
        self.appearance._fontSync.onAttributeEdited(dummy.Event())
        self.assertEqual(font, self.item.font())

    def testThatChangingTheItemFontAffectsTheFontButton(self):
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 1)
        self.item.setFont(font)
        self.assertEqual(font, self.appearance._fontButton.GetSelectedFont())
        
    def testThatPickingAColoredFontChangesTheItemColor(self):
        self.appearance._fontButton.SetSelectedColour(wx.RED)
        self.appearance._fontColorSync.onAttributeEdited(dummy.Event())
        self.assertEqual(wx.RED, self.item.foregroundColor())

    def testThatChangingTheItemColorAffectsTheFontButton(self):
        self.item.setForegroundColor(wx.RED)
        self.assertEqual(wx.RED, self.appearance._fontButton.GetSelectedColour())

    def testThatPickingAColoredFontChangesTheColorButton(self):
        self.appearance._fontButton.SetSelectedColour(wx.RED)
        self.appearance._fontColorSync.onAttributeEdited(dummy.Event())
        self.assertEqual(wx.RED, self.appearance._foregroundColorButton.GetColour())
        
    def testThatPickingAColorChangesTheFontButtonColor(self):
        self.appearance._foregroundColorButton.SetColour(wx.RED)
        self.appearance._foregroundColorSync.onAttributeEdited(dummy.Event())
        self.assertEqual(wx.RED, self.appearance._fontButton.GetSelectedColour())
        
    def testThatPickingAnIconChangesTheItemIcon(self):
        self.appearance._iconEntry.SetSelection(1)
        self.appearance._iconSync.onAttributeEdited(dummy.Event())
        self.failUnless(self.item.icon())
        
    def testThatChangingTheItemIconAffectsTheIconEntry(self):
        imageNames = sorted(gui.artprovider.chooseableItemImages.keys())
        self.item.setIcon(imageNames[10])
        self.assertEqual(10, self.appearance._iconEntry.GetSelection())
