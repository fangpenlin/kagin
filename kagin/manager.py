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
            self.logger  = logging.getLogger(__name__)
        self.file_map = None
        #: configuration of Kargin manager
        self.config = config
        self.init()
        
    def init(self):
        self.read_file_map()
        
        self.input_dir = self.config['input_dir']
        self.output_dir = self.config['output_dir']
        
        s_cfg = self.config['storage']
        self.storage = S3Storage(
            url_prefix=s_cfg['url_prefix'],
            bucket_name=s_cfg['bucket_name'],
            access_key=s_cfg['access_key'],
            secret_key=s_cfg['secret_key']
        )
        
        # read file map
        self.file_map
        
        self.minify_dir = os.path.join(self.output_dir, 'minify')
        self.hash_input_dir = os.path.join(self.output_dir, 'hash_input')
        self.hash_output_dir = os.path.join(self.output_dir, 'hash_output')
        self.prepare_dir(self.minify_dir)
        self.prepare_dir(self.hash_input_dir)
        self.prepare_dir(self.hash_output_dir)
        
        # init JS groups
        self.js_config = FileConfig(self.input_dir)
        for group in self.config['js_groups']:
            name = group['name']
            files = group['files']
            self.js_config.add_group(name, files)
            
        # init CSS groups
        self.css_config = FileConfig(self.input_dir)
        for group in self.config['css_groups']:
            name = group['name']
            files = group['files']
            self.css_config.add_group(name, files)
            
        self.hash_file = HashFile(self.hash_input_dir, self.hash_output_dir)
        
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
        builder.build(self.js_config, '.minify.js')
        builder.build(self.css_config, '.minify.css')
        
    def do_hash(self):
        self.file_map = self.hash_file.run_hashing()
        self.hash_file.run_linking(self.file_map, self.route_hashed_url)
        
    def route_hashed_url(self, name):
        """Generate URL for hashed filename in storage
        
        """
        return self.storage.route_url(name)
    
    def route_rel_url(self, path):
        """Generate URL for relative URL in storage  
        
        """
        hashed = self.file_map.get(path)
        if not hashed:
            return
        return self.route_hashed_url(hashed)
    
    def build(self):
        """Perform processes
        
        """
        self.do_minify()
        self.copy_files(self.input_dir, self.hash_input_dir)
        self.copy_files(self.minify_dir, self.hash_input_dir)
        self.do_hash()
        
        with open(self.config['file_map'], 'wt') as file:
            json.dump(self.file_map, file)
            
        self.logger.info('Finish building.')
            
    def upload(self, overwire_css=True):
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
                if filename in names and not force_upload:
                    self.logger.info('%s already exists, skipped', filename)
                    continue
                file_path = os.path.join(root, filename)
                self.logger.info('Uploading %s ...', filename)
                self.storage.upload_file(filename, file_path)
        self.logger.info('Finish uploading.')
