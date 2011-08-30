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
            
    def run(self):
        """Run file hashing, generate filename map and return
        
        """
        file_map = {}
        for _, _, filenames in os.walk(self.input_dir):
            for filename in filenames:
                # TODO: exclude files here
                hash = self.compute_hash(filename)
                _, ext = os.path.splitext(filename)
                output_filename = os.path.join(self.output_dir, hash + ext)
                shutil.copy(filename, output_filename)
                file_map[filename] = output_filename
        return file_map
                
if __name__ == '__main__':
    h = HashFile('.', '.')
    print h.run()