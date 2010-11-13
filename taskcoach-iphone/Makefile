
# LANGS=fr nl ru de th cs
LANGS=fr nl de

all: help

help:
	@echo 'Targets:'
	@echo '  - messages: Generate messages.pot'
	@echo '  - stringfiles: Generate Localizable.strings and Root.strings from PO files'
	@echo '  - translated: Generate NIB files for all languages'
	@echo
	@echo 'Typical use:'
	@echo '<Linux> $ make messages'
	@echo '(commit new messages.pot, wait for translators, download PO files)'
	@echo '<Linux> $ make stringfiles'
	@echo '(commit)'
	@echo '<MacOS> $ make translated'
	@echo '(Check NIB files in Interface Builder, commit)'

messages:
	find Classes -name "*.m" | xargs xgettext -o i18n.in/messages.pot

stringfiles:
	msgcat -o en.lproj/Localizable.strings --stringtable-output i18n.in/messages.pot
	for lang in $(LANGS); do \
		msgcat -o $$lang.lproj/Localizable.strings --stringtable-output i18n.in/$$lang.po; \
	done

translated:
	# This generates NIB files for all languages. They must then be edited with
	# Interface Builder to ensure widget sizes are OK.
	for lang in $(LANGS); do \
		for name in DatePickerView MainWindow TaskView TaskDetailsRecurrencePeriodPicker TaskDetailsControlleriPad; do \
			ibtool --strings-file $$lang.lproj/$$name.strings \
				--write $$lang.lproj/$$name.xib en.lproj/$$name.xib; \
		done; \
		ibtool --strings-file Resources-iPad/$$lang.lproj/MainWindow-iPad.strings \
			--write Resources-iPad/$$lang.lproj/MainWindow-iPad.xib Resources-iPad/en.lproj/MainWindow-iPad.xib; \
	done

xibstrings:
	# Extract translatable strings from XIB files.
	for lang in en $(LANGS); do \
		for name in DatePickerView MainWindow TaskView TaskDetailsRecurrencePeriodPicker TaskDetailsControlleriPad; do \
			ibtool --generate-strings-file $$lang.lproj/$$name.strings en.lproj/$$name.xib; \
		done; \
		ibtool --generate-strings-file Resources-iPad/$$lang.lproj/MainWindow-iPad.strings Resources-iPad/$$lang.lproj/MainWindow-iPad.xib; \
	done
