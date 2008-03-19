from distutils.command.bdist_rpm import bdist_rpm 


class bdist_rpm_fedora(bdist_rpm):
    user_options = bdist_rpm.user_options + \
        [('spec-file=', None, 'spec file to use'),
         ('desktop-file', None, 'desktop file to use')]

    def initialize_options(self):
        bdist_rpm.initialize_options(self)
        self.spec_file = []
        self.desktop_file = ''

    def _make_spec_file(self):
        ''' We don't want the spec file to be generated, but the rpm build
        process should just use the provided spec file. '''
        return self.spec_file
        
    def copy_file(self, source, dest):
        ''' HACK WARNING! bdist_rpm is difficult to override because its
        methods are much too long. We need to copy the desktop file in 
        addition to the icon, so we override copy_file, check whether the 
        icon is being copied, and if so, also copy the desktop file.'''
        bdist_rpm.copy_file(self, source, dest)
        if source == self.icon:
            bdist_rpm.copy_file(self, self.desktop_file, dest)
