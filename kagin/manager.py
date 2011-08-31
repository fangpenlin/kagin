import os
import logging
import shutil

from kagin.minify import FileConfig, Builder
from kagin.hash import HashFile

class KarginManager(object):
    def __init__(self, config, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger  = logging.getLogger(__name__)
        self.file_map = None
        #: configuration of Kargin manager
        self.config = config
        self.init()
        
    def init(self):
        self.input_dir = self.config['input_dir']
        self.output_dir = self.config['output_dir']
        self.url_prefix = self.config['storage']['url_prefix']
        
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
        self.hash_file.run_linking(self.file_map, self.url_prefix)
        
    def build(self):
        """Perform processes
        
        """
        import json
        
        self.do_minify()
        self.copy_files(self.input_dir, self.hash_input_dir)
        self.copy_files(self.minify_dir, self.hash_input_dir)
        self.do_hash()
        
        with open(self.config['file_map'], 'wt') as file:
            json.dump(self.file_map, file)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cfg = dict(
        input_dir='public',
        output_dir='output',
        file_map='file_map.json',
        js_groups=[
            dict(name='testjs', files=[
                'javascripts/chat.js',
                'javascripts/jquery.js'
            ])
        ],
        css_groups=[
            dict(name='testcss', files=[
                'css/candy.css',
                'css/radio.css'
            ])                    
        ],
        storage=dict(
            url_prefix='http://cdn.s3.now.in'
        )
    )
    m = KarginManager(cfg)
    m.build()