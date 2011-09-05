import urlparse

from boto.s3.connection import S3Connection
from boto.s3.key import Key

class S3Storage(object):
    """Amazon s3 storage
    
    """
    
    def __init__(self, url_prefix, bucket_name, access_key, secret_key):
        # TODO: add location support here
        self.url_prefix = url_prefix
        self.access_key= access_key
        self.secret_key= secret_key
        self.bucket_name= bucket_name
        self.conn = S3Connection(self.access_key, self.secret_key)
        self.bucket = self.conn.create_bucket(self.bucket_name)
        
    def route_url(self, name):
        """Get URL of object in storage by name
        
        """
        return urlparse.urljoin(self.url_prefix, name)
        
    def exist(self, name):
        """Check does a file exist on the storage
        
        """
        return self.bucket.get_key(name) is not None
    
    def get_names(self):
        """Get a list of existing name of files
        
        """
        return [key.name for key in self.bucket.get_all_keys()]
        
    def upload(self, name, data, reduced_redundancy=True):
        """Upload data
        
        """
        key = Key(self.bucket, name)
        key.set_contents_from_string(data, 
                                     reduced_redundancy=reduced_redundancy)
        
    def upload_file(self, name, filename, reduced_redundancy=True):
        """Upload data from file
        
        """
        key = Key(self.bucket, name)
        key.set_contents_from_filename(filename, 
                                       reduced_redundancy=reduced_redundancy)
    def remove(self, name):
        """Remove file
        
        """
        key = Key(self.bucket, name)
        key.delete()