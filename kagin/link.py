import os
import logging

class LinkFile(object):
    """This object replace link in resource files with a file map
    
    """
    
    def __init__(self, file_dir, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
            #: path to file directory to link
            self.file_dir = file_dir
            
    def run(self, file_map):
        """Replace URL links in resource files with URL in file_map
        
        """
        