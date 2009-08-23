
all: stringfiles

messages:
	find Classes -name "*.m" | xargs xgettext -o i18n.in/messages.pot

stringfiles:
	msgcat -o en.lproj/Localizable.strings --stringtable-output i18n.in/messages.pot
	for lang in fr; do \
		msgcat -o $$lang.lproj/Localizable.strings --stringtable-output i18n.in/$$lang.po; \
	done

translated:
	# This generates NIB files for all languages. They must then be edited with
	# Interface Builder to ensure widget sizes are OK.
	for name in DatePickerView MainWindow StringChoice SyncView TaskView; do \
		ibtool --strings-file fr.lproj/$$name.strings --write fr.lproj/$$name.xib en.lproj/$$name.xib; \
	done
