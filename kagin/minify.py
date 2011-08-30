import os
import logging
import subprocess

class FileConfig(object):
    """Group of files to be minified and compacted together
    
    """
    def __init__(self, input_dir, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
            
        #: input files directory
        self.input_dir = input_dir
        #: group of files
        self.groups = {}
        #: map from filename to group name
        self.filename_map = {}
        
    def add_group(self, name, filenames):
        """Add file group
        
        """
        assert name not in self.groups 
        self.groups[name] = filenames
        for filename in filenames:
            self.filename_map[filename] = name
        
    def include_files(self, filenames):
        """Return name of groups which include files in filenames
        
        """
        groups = set()
        for filename in filenames:
            group_name = self.filename_map[filename]
            groups.add(group_name)
        return groups
    
class Compressor(object):
    
    def __init__(self, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
    
    def _get_yui_compressor(self):
        """Get path of yui compressor
        
        """
        import kagin
        pkg_dir = os.path.dirname(kagin.__file__)
        path = os.path.join(pkg_dir, 'yuicompressor-2.4.2.jar')
        return path
        
    def minify(self, input_files, output_path):
        minified = []
        yui_path = self._get_yui_compressor()
        for filename in input_files:
            self.logger.info('Minifying %s ...', filename)
            output = subprocess.check_output(['java', '-jar', 
                                              yui_path, filename])
            minified.append(output)
        minified = '\n'.join(minified)
        with open(output_path, 'wt') as file:
            file.write(minified)
    
class Builder(object):
    """Builder builds CSS or JS file groups into minified files
    
    """
    def __init__(self, output_dir, ext):
        self.output_dir = output_dir
        self.ext = ext
        
    def build(self, file_config):
        compressor = Compressor()
        for name, filenames in file_config.groups.iteritems():
            output_filename = os.path.join(self.output_dir, name + self.ext)
            input_files = [os.path.join(file_config.input_dir, name) 
                           for name in filenames]
            compressor.minify(input_files, output_filename)