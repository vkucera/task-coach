'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
from distutils.core import Command
from distutils.file_util import copy_file


class bdist_winpenpack(Command, object):
    
    description = 'create a winPenPack X-Software package'
    
    user_options = [
        ('bdist-base=', None, 
         'base directory for creating built distributions [build]'),
        ('dist-dir=', 'd', 'directory to put final deb files in [dist]')]
    
    def initialize_options(self):
        self.bdist_base = 'build'
        self.dist_dir = 'dist'
    
    def finalize_options(self):
        mandatoryOptions = []
        for option, description in mandatoryOptions:
            if not getattr(self, option):
                raise errors.DistutilsOptionError, \
                    'you must provide %s (--%s)'%(description, option)

    def run(self):
        self.base = os.path.join(self.bdist_base, 'X-TaskCoach')
        self.create_winpenpack_paths()
        self.copy_launcher()
        self.copy_documents()
        
    def create_winpenpack_paths(self):
        for pathComponents in [('Bin', 'TaskCoach'), 
                               ('Documents', 'TaskCoach'),
                               ('English_users',), 
                               ('ReadMe',), 
                               ('User', 'TaskCoach')]:
            path = os.path.join(self.base, *pathComponents)
            if not os.path.exists(path):
                os.makedirs(path)
                    
    def copy_launcher(self):
        launcher = os.path.join('build.in', 'winpenpack', 'X-TaskCoach.%s')
        for ext in ('exe', 'ini'):
            copy_file(launcher%ext, self.base)
        
    def copy_documents(self):
        example = os.path.join('build.in', 'winpenpack', 'Documents', 'TaskCoach', 'example.tsk')
        copy_file(example, os.path.join(self.base, 'Documents', 'TaskCoach'))
