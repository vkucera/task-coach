import converter, changes 

textConverter = converter.ReleaseToTextConverter()
for release in changes.releases:
    print textConverter.convert(release)

