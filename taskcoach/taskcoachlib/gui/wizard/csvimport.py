'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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


import wx, os, csv, tempfile
from taskcoachlib.i18n import _
from taskcoachlib.thirdparty import chardet

import wx.wizard as wiz
import wx.grid as gridlib


class CSVDialect(csv.Dialect):
    def __init__(self, delimiter=',', quotechar='"', doublequote=True, escapechar=''):
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.quoting = csv.QUOTE_MINIMAL
        self.lineterminator = '\r\n'
        self.doublequote = doublequote
        self.escapechar = escapechar

        csv.Dialect.__init__(self)


class CSVImportOptionsPage(wiz.WizardPageSimple):
    def __init__(self, filename, *args, **kwargs):
        super(CSVImportOptionsPage, self).__init__(*args, **kwargs)

        self.delimiter = wx.Choice(self, wx.ID_ANY)
        self.delimiter.Append(_('Comma'))
        self.delimiter.Append(_('Tab'))
        self.delimiter.Append(_('Space'))
        self.delimiter.SetSelection(0)

        self.quoteChar = wx.Choice(self, wx.ID_ANY)
        self.quoteChar.Append(_('Simple quote'))
        self.quoteChar.Append(_('Double quote'))
        self.quoteChar.SetSelection(1)

        self.quotePanel = wx.Panel(self, wx.ID_ANY)
        self.doubleQuote = wx.RadioButton(self.quotePanel, wx.ID_ANY, _('Double it'))
        self.doubleQuote.SetValue(True)
        self.escapeQuote = wx.RadioButton(self.quotePanel, wx.ID_ANY, _('Escape with'))
        self.escapeChar = wx.TextCtrl(self.quotePanel, wx.ID_ANY, '\\', size=(50, -1))
        self.escapeChar.Enable(False)
        self.escapeChar.SetMaxLength(1)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.doubleQuote, 1, wx.ALL, 3)
        hsizer.Add(self.escapeQuote, 1, wx.ALL, 3)
        hsizer.Add(self.escapeChar, 1, wx.ALL, 3)
        self.quotePanel.SetSizer(hsizer)

        self.hasHeaders = wx.CheckBox(self, wx.ID_ANY, _('First line describes fields'))
        self.hasHeaders.SetValue(True)

        self.grid = gridlib.Grid(self, wx.ID_ANY)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelSize(0)
        self.grid.CreateGrid(0, 0)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        gridSizer = wx.FlexGridSizer(0, 2)

        gridSizer.Add(wx.StaticText(self, wx.ID_ANY, _('Delimiter')), 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 3)
        gridSizer.Add(self.delimiter, 0, wx.ALL, 3)

        gridSizer.Add(wx.StaticText(self, wx.ID_ANY, _('Quote character')), 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 3)
        gridSizer.Add(self.quoteChar, 0, wx.ALL, 3)

        gridSizer.Add(wx.StaticText(self, wx.ID_ANY, _('Escape quote')), 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 3)
        gridSizer.Add(self.quotePanel, 0, wx.ALL, 3)

        gridSizer.Add(self.hasHeaders, 0, wx.ALL, 3)
        gridSizer.Add((0, 0))

        gridSizer.AddGrowableCol(1)
        vsizer.Add(gridSizer, 0, wx.EXPAND|wx.ALL, 3)

        vsizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 3)

        self.SetSizer(vsizer)

        self.headers = None

        self.filename = filename
        self.encoding = chardet.detect(file(filename, 'rb').read())['encoding']
        self.OnOptionChanged(None)

        wx.EVT_CHOICE(self.delimiter, wx.ID_ANY, self.OnOptionChanged)
        wx.EVT_CHOICE(self.quoteChar, wx.ID_ANY, self.OnOptionChanged)
        wx.EVT_CHECKBOX(self.hasHeaders, wx.ID_ANY, self.OnOptionChanged)
        wx.EVT_RADIOBUTTON(self.doubleQuote, wx.ID_ANY, self.OnOptionChanged)
        wx.EVT_RADIOBUTTON(self.escapeQuote, wx.ID_ANY, self.OnOptionChanged)
        wx.EVT_TEXT(self.escapeChar, wx.ID_ANY, self.OnOptionChanged)

    def OnOptionChanged(self, event):
        self.escapeChar.Enable(self.escapeQuote.GetValue())

        if self.filename is None:
            self.grid.SetRowLabelSize(0)
            self.grid.SetColLabelSize(0)
            if self.grid.GetNumberCols():
                self.grid.DeleteRows(0, self.grid.GetNumberRows())
                self.grid.DeleteCols(0, self.grid.GetNumberCols())
        else:
            if self.doubleQuote.GetValue():
                doublequote = True
                escapechar = ''
            else:
                doublequote = False
                escapechar = self.escapeChar.GetValue().encode('UTF-8')
            self.dialect = CSVDialect(delimiter={0: ',', 1: '\t', 2: ' '}[self.delimiter.GetSelection()],
                                      quotechar={0: "'", 1: '"'}[self.quoteChar.GetSelection()],
                                      doublequote=doublequote, escapechar=escapechar)

            fp = tempfile.TemporaryFile()
            try:
                fp.write(file(self.filename, 'rb').read().decode(self.encoding).encode('UTF-8'))
                fp.seek(0)

                reader = csv.reader(fp, dialect=self.dialect)

                if self.hasHeaders.GetValue():
                    self.headers = [header.decode('UTF-8') for header in reader.next()]
                else:
                    # In some cases, empty fields are omitted if they're at the end...
                    hsize = 0
                    for line in reader:
                        hsize = max(hsize, len(line))
                    self.headers = [_('Field #%d') % idx for idx in xrange(hsize)]
                    fp.seek(0)
                    reader = csv.reader(fp, dialect=self.dialect)

                if self.grid.GetNumberCols():
                    self.grid.DeleteRows(0, self.grid.GetNumberRows())
                    self.grid.DeleteCols(0, self.grid.GetNumberCols())
                self.grid.InsertCols(0, len(self.headers))

                self.grid.SetColLabelSize(20)
                for idx, header in enumerate(self.headers):
                    self.grid.SetColLabelValue(idx, header)

                lineno = 0
                for line in reader:
                    self.grid.InsertRows(lineno, 1)
                    for idx, value in enumerate(line):
                        self.grid.SetCellValue(lineno, idx, value.decode('UTF-8'))
                    lineno += 1
            finally:
                fp.close()

    def GetOptions(self):
        return dict(dialect=self.dialect,
                    hasHeaders=self.hasHeaders.GetValue(),
                    filename=self.filename,
                    encoding=self.encoding,
                    fields=self.headers)

    def CanGoNext(self):
        if self.filename is not None:
            self.GetNext().SetOptions(self.GetOptions())
            return True, None
        return False, _('Please select a file.')


class CSVImportMappingPage(wiz.WizardPageSimple):
    def __init__(self, *args, **kwargs):
        super(CSVImportMappingPage, self).__init__(*args, **kwargs)

        # (field name, multiple values allowed)

        self.fields = [
            (_('None'), True),
            (_('ID'), False),
            (_('Subject'), False),
            (_('Description'), True),
            (_('Category'), True),
            (_('Priority'), False),
            (_('Start date'), False),
            (_('Due date'), False),
            (_('Completion date'), False),
            (_('Budget'), False),
            (_('Fixed fee'), False),
            (_('Hourly fee'), False),
            ]
        self.choices = []
        self.interior = wx.ScrolledWindow(self)
        self.interior.EnableScrolling(False, True)
        self.interior.SetScrollRate(10, 10)

        sizer = wx.BoxSizer()
        sizer.Add(self.interior, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def SetOptions(self, options):
        self.options = options

        for child in self.interior.GetChildren():
            self.interior.RemoveChild(child)
        self.choices = []

        gsz = wx.FlexGridSizer(0, 2)

        for fieldName in options['fields']:
            gsz.Add(wx.StaticText(self.interior, wx.ID_ANY, fieldName))

            choice = wx.Choice(self.interior, wx.ID_ANY)
            for tcFieldName, _ in self.fields:
                choice.Append(tcFieldName)
            choice.SetSelection(0)
            self.choices.append(choice)

            gsz.Add(choice)

        self.interior.SetSizer(gsz)

    def CanGoNext(self):
        wrongFields = []
        countNotNone = 0

        for idx, (fieldName, canMultiple) in enumerate(self.fields):
            count = 0
            for choice in self.choices:
                if choice.GetSelection() == idx:
                    count += 1
                if choice.GetSelection() != 0:
                    countNotNone += 1
            if count > 1 and not canMultiple:
                wrongFields.append(fieldName)

        if countNotNone == 0:
            return False, _('No field mapping.')

        if len(wrongFields) == 1:
            return False, _('The "%s" field cannot be selected several times.') % wrongFields[0]

        if len(wrongFields):
            return False, _('The fields %s cannot be selected several times.') % ', '.join(['"%s"' % fieldName for fieldName in wrongFields])

        return True, None

    def GetOptions(self):
        options = dict(self.options)
        options['mappings'] = [self.fields[choice.GetSelection()][0] for choice in self.choices]
        return options


class CSVImportWizard(wiz.Wizard):
    def __init__(self, filename, *args, **kwargs):
        kwargs['style'] = wx.RESIZE_BORDER
        super(CSVImportWizard, self).__init__(*args, **kwargs)

        self.optionsPage = CSVImportOptionsPage(filename, self)
        self.mappingPage = CSVImportMappingPage(self)
        self.optionsPage.SetNext(self.mappingPage)
        self.mappingPage.SetPrev(self.optionsPage)

        self.SetPageSize((600, -1)) # I know this is obsolete but it's the only one that works...

        wiz.EVT_WIZARD_PAGE_CHANGING(self, wx.ID_ANY, self.OnPageChanging)
        wiz.EVT_WIZARD_PAGE_CHANGED(self, wx.ID_ANY, self.OnPageChanged)

    def OnPageChanging(self, event):
        if event.GetDirection():
            can, msg = event.GetPage().CanGoNext()
            if not can:
                wx.MessageBox(msg, _('Information'), wx.OK)
                event.Veto()

    def OnPageChanged(self, event):
        if event.GetPage() == self.optionsPage:
            pass # XXXTODO

    def RunWizard(self):
        return super(CSVImportWizard, self).RunWizard(self.optionsPage)

    def GetOptions(self):
        return self.mappingPage.GetOptions()
