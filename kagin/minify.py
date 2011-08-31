import os
import logging
import subprocess
import urlparse

from kagin.link_css import replace_css_links

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
    
class Builder(object):
    """Builder builds CSS or JS file groups into minified files
    
    """
    def __init__(self, input_dir, output_dir, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.input_dir = input_dir
        self.output_dir = output_dir
        
    def _get_yui_compressor(self):
        """Get path of yui compressor
        
        """
        import kagin
        pkg_dir = os.path.dirname(kagin.__file__)
        path = os.path.join(pkg_dir, 'yuicompressor-2.4.2.jar')
        return path
    
    def link_css(self, content, old_path, new_path):
        """Replace URL links in CSS content and return result
        
        """
        # put both path in output dir
        old_path = os.path.join(self.output_dir, old_path)
        new_path = os.path.join(self.output_dir, new_path)
        old_dir = os.path.dirname(old_path)
        new_dir = os.path.dirname(new_path)
        rel_dir = os.path.relpath(old_dir, new_dir)
        #rel_dir = url_path(rel_dir, old_dir)
        rel_dir = rel_dir.replace('\\', '/')
        if rel_dir:
            rel_dir = rel_dir + '/'
        
        def map_func(url):
            parsed = urlparse.urlparse(url)
            # we don't want to map absolute URLs
            if parsed.scheme:
                return
            if parsed.path.startswith('/'):
                return
            return urlparse.urljoin(rel_dir, url)
        
        output = replace_css_links(content, map_func, self.logger)
        return output
        
    def minify(self, input_files, output_path, link_css=True):
        minified = []
        yui_path = self._get_yui_compressor()
        for filename in input_files:
            self.logger.info('Minifying %s ...', filename)
            output = subprocess.check_output(['java', '-jar', 
                                              yui_path, filename])
            _, ext = os.path.splitext(filename)
            if link_css and ext.lower() == '.css':
                old_path = os.path.relpath(filename, self.input_dir)
                new_path = os.path.relpath(output_path, self.output_dir)
                output = self.link_css(output, old_path, new_path)
            minified.append(output)
            
        file_content = '\n'.join(minified)
        with open(output_path, 'wt') as file:
            file.write(file_content)
        
    def build(self, file_config, ext):
        for name, filenames in file_config.groups.iteritems():
            output_filename = os.path.join(self.output_dir, name + ext)
            input_files = [os.path.join(file_config.input_dir, name) 
                           for name in filenames]
            self.minify(input_files, output_filename)