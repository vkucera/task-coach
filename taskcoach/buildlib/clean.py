import os, os.path, fnmatch
from distutils.command.clean import clean as BaseCleanCommand
from distutils import log


class clean(BaseCleanCommand, object):
    user_options = BaseCleanCommand.user_options + \
        [('really-clean', 'r', 'remove even more files')]
    boolean_options = BaseCleanCommand.boolean_options + ['really-clean']

    def initialize_options(self):
        super(clean, self).initialize_options()
        self.really_clean = False
        self.cleaning_patterns = ['*.pyc']
        self.really_clean_patterns = ['*.bak']
                    
    def finalize_options(self):
        super(clean, self).finalize_options()
        if self.really_clean:
            self.cleaning_patterns.extend(self.really_clean_patterns)
                    
    def run(self):
        super(clean, self).run()
        if not self.verbose:
            log.info("recursively removing '" + "', '".join(self.cleaning_patterns) + "'")
        for root, dirs, files in os.walk('.'):
            for pattern in self.cleaning_patterns:
                for filename in fnmatch.filter(files, pattern):
                    filename = os.path.join(root, filename)
                    try:
                        if not self.dry_run:
                            os.unlink(filename)
                        if self.verbose:
                            log.info("removing '%s'"%filename.strip('.\\'))
                    except:
                        pass
