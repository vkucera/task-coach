import converter, changes, sys

if sys.argv[1] == 'text':
    converter = converter.ReleaseToTextConverter()
elif sys.argv[1] == 'html':
    converter = converter.ReleaseToHTMLConverter()
else:
    raise ValueError, 'Unknown target format (%s)'%sys.argv[1]

for release in changes.releases:
    print converter.convert(release)

