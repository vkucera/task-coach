
all: translations

translations:
	for name in DatePickerView MainWindow StringChoice SyncView; do \
		ibtool --generate-stringsfile fr.lproj/$$name.strings en.lproj/$$name.xib; cp en.lproj/$$name.xib fr.lproj/$$name.xib; \
	done
	genstrings -o fr.lproj Classes/*.m Classes/Config/*.m Classes/Database/*.m Classes/Domain/*.m \
		Classes/Network/*.m Classes/Synchronization/*.m Classes/Utils/*.m

translated:
	for name in DatePickerView MainWindow StringChoice SyncView; do \
		ibtool --strings-file fr.lproj/$$name.strings --write fr.lproj/$$name.xib en.lproj/$$name.xib; \
	done
