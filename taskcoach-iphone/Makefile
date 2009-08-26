
all: stringfiles

messages:
	find Classes -name "*.m" | xargs xgettext -o i18n.in/main.pot
	msgcat -o i18n.in/settings.pot --stringtable-input Settings.bundle/en.lproj/Root.strings
	msgcat -o i18n.in/messages.pot i18n.in/main.pot i18n.in/settings.pot

stringfiles:
	msgcat -o en.lproj/Localizable.strings --stringtable-output i18n.in/messages.pot
	for lang in fr nl; do \
		msgcat -o $$lang.lproj/Localizable.strings --stringtable-output i18n.in/$$lang.po; \
	done

translated:
	# This generates NIB files for all languages. They must then be edited with
	# Interface Builder to ensure widget sizes are OK.
	for lang in fr nl; do \
		for name in DatePickerView MainWindow StringChoice SyncView TaskView; do \
			ibtool --strings-file $$lang.lproj/$$name.strings \
				--write $$lang.lproj/$$name.xib en.lproj/$$name.xib; \
		done; \
	done

