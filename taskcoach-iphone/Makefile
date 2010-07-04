
all: help

help:
	@echo 'Targets:'
	@echo '  - messages: Generate messages.pot'
	@echo '  - stringfiles: Generate Localizable.strings and Root.strings from PO files'
	@echo '  - settings: Generate Root.strings files for settings bundle'
	@echo '  - translated: Generate NIB files for all languages'
	@echo
	@echo 'Typical use:'
	@echo '<Linux> $ make messages'
	@echo '(commit new messages.pot, wait for translators, download PO files)'
	@echo '<Linux> $ make stringfiles'
	@echo '<Linux> $ make settings'
	@echo '(commit)'
	@echo '<MacOS> $ make translated'
	@echo '(Check NIB files in Interface Builder, commit)'

messages:
	find Classes -name "*.m" | xargs xgettext -o i18n.in/main.pot
	msgcat -o i18n.in/settings.pot --stringtable-input Settings.strings
	msgcat -o i18n.in/messages.pot i18n.in/main.pot i18n.in/settings.pot

stringfiles:
	msgcat -o en.lproj/Localizable.strings --stringtable-output i18n.in/messages.pot
	for lang in fr nl ru de th cs; do \
		msgcat -o $$lang.lproj/Localizable.strings --stringtable-output i18n.in/$$lang.po; \
	done

settings:
	# Settings bundle
	msgcat --stringtable-input -o Settings.po Settings.strings
	for lang in fr nl ru de th cs; do \
		msgmerge -N -o - i18n.in/$$lang.po Settings.po | egrep -v "^#" | \
			msgcat --stringtable-output -o Settings.bundle/$$lang.lproj/Root.strings -; \
	done

translated:
	# This generates NIB files for all languages. They must then be edited with
	# Interface Builder to ensure widget sizes are OK.
	for lang in fr nl ru de th cs; do \
		for name in DatePickerView MainWindow TaskView TaskDetailsRecurrencePeriodPicker TaskDetailsControlleriPad; do \
			ibtool --strings-file $$lang.lproj/$$name.strings \
				--write $$lang.lproj/$$name.xib en.lproj/$$name.xib; \
		done; \
		ibtool --strings-file Resources-iPad/$$lang.lproj/MainWindow-iPad.strings \
			--write Resources-iPad/$$lang.lproj/MainWindow-iPad.xib Resources-iPad/en.lproj/MainWindow-iPad.xib; \
	done

xibstrings:
	# Extract translatable strings from XIB files.
	for lang in en fr nl ru de th cs; do \
		for name in DatePickerView MainWindow TaskView TaskDetailsRecurrencePeriodPicker TaskDetailsControlleriPad; do \
			ibtool --generate-strings-file $$lang.lproj/$$name.strings en.lproj/$$name.xib; \
		done; \
		ibtool --generate-strings-file Resources-iPad/$$lang.lproj/MainWindow-iPad.strings Resources-iPad/$$lang.lproj/MainWindow-iPad.xib; \
	done
