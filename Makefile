
all: stringfiles

messages:
	find Classes -name "*.m" | xargs xgettext -o i18n.in/messages.pot

stringfiles:
	msgcat -o en.lproj/Localizable.strings --stringtable-output i18n.in/messages.pot

translated:
	# This generates NIB files for all languages. They must then be edited with
	# Interface Builder to ensure widget sizes are OK.
	for name in DatePickerView MainWindow StringChoice SyncView TaskView; do \
		ibtool --strings-file fr.lproj/$$name.strings --write fr.lproj/$$name.xib en.lproj/$$name.xib; \
	done
