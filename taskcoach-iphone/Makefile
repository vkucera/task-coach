
all: incremental

incremental:
	rm -rf tmp.lproj
	mkdir tmp.lproj
	for name in DatePickerView MainWindow StringChoice SyncView; do \
		ibtool --generate-stringsfile tmp.lproj/$$name.strings en.lproj/$$name.xib; \
		wincent-strings-util --base tmp.lproj/$$name.strings --extract fr.lproj/$$name.strings --output fr.lproj/$$name.new.strings; \
	done
	genstrings -o tmp.lproj Classes/*.m Classes/Config/*.m Classes/Database/*.m Classes/Domain/*.m \
		Classes/Network/*.m Classes/Synchronization/*.m Classes/Utils/*.m
	wincent-strings-util --base tmp.lproj/Localizable.strings --extract fr.lproj/Localizable.strings --output fr.lproj/Localizable.new.strings

translations:
	for name in DatePickerView MainWindow StringChoice SyncView; do \
		ibtool --generate-stringsfile fr.lproj/$$name.strings en.lproj/$$name.xib; cp en.lproj/$$name.xib fr.lproj/$$name.xib; \
	done
	genstrings -o fr.lproj Classes/*.m Classes/Config/*.m Classes/Database/*.m Classes/Domain/*.m \
		Classes/Network/*.m Classes/Synchronization/*.m Classes/Utils/*.m

translated:
	for name in DatePickerView MainWindow StringChoice SyncView; do \
		cp en.lproj/$$name.xib fr.lproj/$$name.xib; \
		ibtool --strings-file fr.lproj/$$name.strings --write fr.lproj/$$name.xib en.lproj/$$name.xib; \
	done
