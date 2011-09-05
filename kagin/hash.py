import os
import logging
import hashlib
import shutil
import urlparse

from kagin.link_css import replace_css_links
from kagin.utils import url_path

class HashFile(object):
    """This object hashes content files and output files with hash file name,
    and generate a file map
    
    """
    
    def __init__(
        self, 
        input_dir, 
        output_dir, 
        hash_type=hashlib.md5, 
        exclude_files=None, 
        logger=None
    ):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        #: path to input directory
        self.input_dir = input_dir
        #: path to output directory
        self.output_dir = output_dir
        #: type of hash function to run, MD5 as default value
        self.hash_type = hash_type
        #: list of filename patterns to ignore
        self.exclude_files = exclude_files
        
    def compute_hash(self, filename):
        """Compute hash value of a file
        
        """
        import mmap
        hash = self.hash_type()
        if not os.path.getsize(filename):
            return hash.hexdigest()
        chunk_size = 4096
        with open(filename, 'rb') as file:
            map = mmap.mmap(file.fileno(), 0, 
                            access=mmap.ACCESS_READ)
            while True:
                chunk = map.read(chunk_size)
                if not chunk:
                    break
                hash.update(chunk)
        return hash.hexdigest()
    
    def run_hashing(self):
        """Run hashing process
        
        """
        file_map = {}
        for root, _, filenames in os.walk(self.input_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                # TODO: exclude files here
                
                # compute hash value of file here
                hash = self.compute_hash(file_path)
                _, ext = os.path.splitext(file_path)
                output_name = os.path.join(self.output_dir, hash + ext)
                
                # copy file
                shutil.copy(file_path, output_name)
                # make relative path
                input_path = url_path(file_path, self.input_dir)
                output_path = url_path(output_name, self.output_dir)
                file_map[input_path] = output_path
                self.logger.info('Output %s as %s', input_path, output_path)
        return file_map
        
    def run_linking(self, file_map, route_url):
        """Run linking process
        
        """
        for root, _, filenames in os.walk(self.input_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                _, ext = os.path.splitext(file_path)
                if ext.lower() != '.css':
                    continue
                
                # directory path of CSS file
                css_dir = os.path.dirname(file_path)
                if css_dir:
                    css_dir = css_dir + '/'
                input_url = url_path(file_path, self.input_dir)
                
                def map_func(url):
                    parsed = urlparse.urlparse(url)
                    # we don't want to map absolute URLs
                    if parsed.scheme:
                        return
                    if parsed.path.startswith('/'):
                        return
                    
                    # get CSS path in file system
                    css_path = os.path.join(css_dir, url)
                    css_path = os.path.normpath(css_path)
                    css_url = url_path(css_path, self.input_dir)
                    new_url = file_map.get(css_url)
                    if new_url is None:
                        return
                    return route_url(new_url)
                
                # output filename
                output_filename = file_map.get(input_url)
                output_filename = os.path.join(self.output_dir, output_filename)
                with open(output_filename, 'rt') as file:
                    css_content = file.read()
                output = replace_css_links(css_content, map_func, self.logger)
                with open(output_filename, 'wt') as file:
                    file.write(output)
                
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    h = HashFile('..\\input', '..\\output')
    file_map = h.run_hashing()
    h.run_linking(file_map, 'http://cdn.s3.now.in')