import os

def url_path(path, base):
    """Ensure the path to be URL-style path
    
    """
    relpath = os.path.relpath(path, base)
    relpath = relpath.replace('\\', '/')
    if path.endswith('/') or path.endswith('\\'):
        return relpath + '/'
    return relpath