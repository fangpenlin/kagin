import re
import logging

def replace_css_links(content, map_func, logger=None):
    """Replace CSS URL links
    
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    url_pattern = '(?P<url>[a-zA-Z0-9\-\./_]+)'
    pattern = re.compile(
        r"""url\s*\(\s*['"]?""" + url_pattern + r"""['"]?\s*\)""", 
        flags=re.I | re.M
    )
    # result of all replaced lines
    result = []
    # start of previous match
    previous = 0
    for match in pattern.finditer(content): 
        start = match.start(1)
        end = match.end(1)
        url = match.group(1)
        
        new_url = map_func(url)
        if new_url is None:
            result.append(content[previous:start])
            result.append(url)
            previous = end
            continue
        logger.info('Replace %s with %s', url, new_url)
        result.append(content[previous:start])
        result.append(new_url)
        previous = end
    result.append(content[previous:])
    return ''.join(result)