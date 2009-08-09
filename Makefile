
all: stringfiles

stringfiles:
	for name in DatePickerView MainWindow StringChoice SyncView TaskView; do \
		ibtool --generate-stringsfile en.lproj/$$name.strings en.lproj/$$name.xib; \
	done
	genstrings -o en.lproj Classes/*.m Classes/Config/*.m Classes/Database/*.m Classes/Domain/*.m \
		Classes/Network/*.m Classes/Synchronization/*.m Classes/Utils/*.m

translated:
	for name in DatePickerView MainWindow StringChoice SyncView TaskView; do \
		ibtool --strings-file fr.lproj/$$name.strings --write fr.lproj/$$name.xib en.lproj/$$name.xib; \
	done
