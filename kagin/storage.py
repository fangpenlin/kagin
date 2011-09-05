import urlparse
import logging

from boto.s3.connection import S3Connection
from boto.s3.key import Key

class S3Storage(object):
    """Amazon s3 storage
    
    """
    
    def __init__(
        self, 
        http_url_prefix, 
        https_url_prefix,
        bucket_name, 
        access_key, 
        secret_key, 
        default_headers=None,
        logger=None
    ):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        # TODO: add location support here
        self.http_url_prefix = http_url_prefix
        self.https_url_prefix = https_url_prefix
        self.access_key= access_key
        self.secret_key= secret_key
        self.bucket_name= bucket_name
        self.default_headers = default_headers
        
    @property
    def conn(self):
        if hasattr(self, '_conn'):
            return self._conn
        self._conn = S3Connection(self.access_key, self.secret_key)
        return self._conn
    
    @property
    def bucket(self):
        if hasattr(self, '_bucket'):
            return self._bucket
        self._bucket = self.conn.create_bucket(self.bucket_name)
        return self._bucket
        
    def route_url(self, name, https=False):
        """Get URL of object in storage by name
        
        """
        url_prefix = self.http_url_prefix
        if https:
            url_prefix = self.https_url_prefix
        return urlparse.urljoin(url_prefix, name)
        
    def exist(self, name):
        """Check does a file exist on the storage
        
        """
        return self.bucket.get_key(name) is not None
    
    def get_names(self):
        """Get a list of existing name of files
        
        """
        return [key.name for key in self.bucket.get_all_keys()]
    
    def _upload_args(
        self, 
        content_type=None,
        cache_control=None,
        expires=None, 
        reduced_redundancy=True
    ):
        import datetime
        import email
        import time
        
        headers = self.default_headers or {}
        headers = headers.copy()
        if expires:
            due = (datetime.datetime.now() + expires).timetuple()
            headers['Expires'] = \
                '%s GMT' % email.Utils.formatdate(time.mktime(due))
        if content_type:
            headers['Content-Type'] = content_type
        if cache_control:
            headers['Cache-Control'] = cache_control
        return dict(headers=headers, reduced_redundancy=reduced_redundancy)
        
    def upload(self, name, data, **kwargs):
        """Upload data
        
        """
        key = Key(self.bucket, name)
        args = self._upload_args(**kwargs)
        key.set_contents_from_string(data, **args)
        
    def upload_file(self, name, filename, **kwargs
                    ):
        """Upload data from file
        
        """
        key = Key(self.bucket, name)
        args = self._upload_args(**kwargs)
        key.set_contents_from_filename(filename, **args)
        
    def remove(self, name):
        """Remove file
        
        """
        key = Key(self.bucket, name)
        key.delete()