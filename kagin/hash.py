import os
import logging
import hashlib
import shutil

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
        if self.logger is not None:
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
    
    def unify_path(self, path):
        """Ensure the path to be unix-style path
        
        """
        path = path.replace('\\', '/')
        if path.startswith('/'):
            path = path[1:]
        return path
            
    def run(self):
        """Run file hashing, generate filename map and return
        
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
                input_path = os.path.relpath(file_path, self.input_dir)
                input_path = self.unify_path(input_path)
                output_path = os.path.relpath(output_name, self.output_dir)
                output_path = self.unify_path(output_path)
                file_map[input_path] = output_path
        return file_map
                
if __name__ == '__main__':
    h = HashFile('.', '.')
    print h.run()