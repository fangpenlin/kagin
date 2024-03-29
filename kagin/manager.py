import os
import logging
import shutil
import json

from kagin.minify import FileConfig, Builder
from kagin.hash import HashFile
from storage import S3Storage


class KaginManager(object):
    def __init__(self, config, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.file_map = None
        #: configuration of Kargin manager
        self.config = config
        self.init()
        
    def init(self):
        self.read_file_map()
        
        self.input_dir = self.config['input_dir']
        self.output_dir = self.config['output_dir']
        
        s_cfg = self.config['storage']
        self.storage = S3Storage(**s_cfg)
        
        # read file map
        self.file_map
        
        self.minify_dir = os.path.join(self.output_dir, 'minify')
        self.hash_input_dir = os.path.join(self.output_dir, 'hash_input')
        self.hash_output_dir = os.path.join(self.output_dir, 'hash_output')
        self.prepare_dir(self.minify_dir)
        self.prepare_dir(self.hash_input_dir)
        self.prepare_dir(self.hash_output_dir)
        
        self.mini_js_ext = '.mini.js'
        self.mini_css_ext = '.mini.css'
        self.gzip_ext = '.gzip'
        # init JS groups
        self.js_config = FileConfig(self.input_dir)
        for group in self.config['js_groups']:
            name = group['name']
            files = group['files']
            gzip = group.get('gzip', True)
            self.js_config.add_group(name, files, gzip)
            
        # init CSS groups
        self.css_config = FileConfig(self.input_dir)
        for group in self.config['css_groups']:
            name = group['name']
            files = group['files']
            gzip = group.get('gzip', True)
            self.css_config.add_group(name, files, gzip)
            
        self.hash_file = HashFile(
            self.hash_input_dir, 
            self.hash_output_dir,
            hash_version=self.config.get('hash_version', '')
        )
        
    def read_file_map(self):
        self.file_map = {}
        if not os.path.exists(self.config['file_map']):
            return
        with open(self.config['file_map'], 'rt') as file:
            content = file.read()
        self.file_map = json.loads(content)
        
    def prepare_dir(self, path):
        """Remove and make a director
        
        """
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        os.mkdir(path)
        
    def copy_files(self, src, dest):
        """Copy files in src directory to dest directory
        
        """
        self.logger.debug('Copying files from %s to %s ...', src, dest)
        for root, dirs, filenames in os.walk(src):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                rel_dir = os.path.relpath(dir_path, src)
                dest_dir = os.path.join(dest, rel_dir)
                self.logger.debug('Create directory %s ...', dest_dir)
                os.mkdir(dest_dir)
            for filename in filenames:
                file_path = os.path.join(root, filename)
                repl_path = os.path.relpath(file_path, src)
                dest_path = os.path.join(dest, repl_path)
                shutil.copy(file_path, dest_path)
        
    def do_minify(self): 
        builder = Builder(self.input_dir, self.minify_dir)
        builder.build(self.js_config, self.mini_js_ext)
        builder.build(self.css_config, self.mini_css_ext)
        
    def do_hash(self):
        route_func = lambda name: name
        if self.config.get('absolute_hashed_url', False):
            route_func = self.route_hashed_url
        self.file_map = self.hash_file.run_hashing()
        self.hash_file.run_linking(self.file_map, route_func)

    def _gzip_group(self, group_cfg, ext):
        import gzip as gziplib
        for name, group in group_cfg.groups.iteritems():
            gzip = group['gzip']
            if not gzip:
                continue
            filename = name + ext 
            hashed_name = self.file_map[filename]
            self.logger.info(
                'Compressing JS group %s (%s) ...',
                filename, hashed_name
            )
            hashed_path = os.path.join(self.hash_output_dir, hashed_name)
            with open(hashed_path, 'rb') as f:
                content = f.read()
            hashed_name_base, hashed_ext = os.path.splitext(hashed_name)
            gzip_filename = hashed_name_base + self.gzip_ext + hashed_ext
            gzip_path = os.path.join(self.hash_output_dir, gzip_filename)
            with gziplib.open(gzip_path, 'wb') as f:
                f.write(content)
            self.logger.info('Compressed to %s', gzip_filename)
            self.file_map[filename] = gzip_filename

    def do_gzip(self):
        self._gzip_group(self.js_config, self.mini_js_ext)
        self._gzip_group(self.css_config, self.mini_css_ext)
        
    def route_hashed_url(self, name, https=False):
        """Generate URL for hashed filename in storage
        
        """
        return self.storage.route_url(name, https=https)
    
    def route_rel_url(self, path, https=False):
        """Generate URL for relative URL in storage  
        
        """
        hashed = self.file_map.get(path)
        if not hashed:
            return
        return self.route_hashed_url(hashed, https=https)
    
    def route_path(self, path):
        """Generate relative URL
        
        """
        hashed = self.file_map.get(path)
        return hashed
    
    def get_js_group_urls(self, filenames, https=False):
        """Get minfiy group URLs
        
        """
        minified = self.js_config.include_files(filenames)
        minified = [name + self.mini_js_ext for name in minified]

        def get_url(name):
            return self.route_rel_url(name, https=https)
        return map(get_url, minified)
    
    def get_css_group_urls(self, filenames, https=False):
        """Get minfiy group URLs
        
        """
        minified = self.css_config.include_files(filenames)
        minified = [name + self.mini_css_ext for name in minified]

        def get_url(name):
            return self.route_rel_url(name, https=https)
        return map(get_url, minified)
    
    def build(self):
        """Perform processes
        
        """
        self.do_minify()
        self.copy_files(self.input_dir, self.hash_input_dir)
        self.copy_files(self.minify_dir, self.hash_input_dir)
        self.do_hash()
        self.do_gzip()
        
        with open(self.config['file_map'], 'wt') as file:
            json.dump(self.file_map, file)
            
        self.logger.info('Finish building.')
            
    def upload(self, overwire_all=False, overwire_css=True):
        self.logger.info('Getting name list from storage ...')
        names = self.storage.get_names()
        self.logger.info('Got %s file names', len(names))
        self.logger.debug('Names: %r', names)
        
        for root, _, filenames in os.walk(self.hash_output_dir):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                force_upload = False
                if ext.lower() == '.css' and overwire_css:
                    force_upload = True
                if filename in names and not force_upload and not overwire_all:
                    self.logger.info('%s already exists, skipped', filename)
                    continue
                file_path = os.path.join(root, filename)
                self.logger.info('Uploading %s ...', filename)

                # TODO: use a better approach to determine gziped file
                if self.gzip_ext in file_path:
                    self.storage.upload_file(filename, file_path, content_encoding='gzip')
                else:
                    self.storage.upload_file(filename, file_path)
        self.logger.info('Finish uploading.')
