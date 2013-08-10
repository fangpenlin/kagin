import re
import logging
import urlparse


def replace_css_links(content, map_func, logger=None):
    """Replace CSS URL links
    
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    url_pattern = '(?P<url>[a-zA-Z0-9\-\./_\?=#&]+)'
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

        endswith_q = False
        striped_url = url
        ori_result = urlparse.urlparse(url)
        if ori_result.query or ori_result.fragment:
            new_result = urlparse.ParseResult(
                scheme=ori_result.scheme, 
                netloc=ori_result.netloc, 
                path=ori_result.path, 
                params=ori_result.params, 
                query='', 
                fragment='' 
            )
            striped_url = new_result.geturl()
            logger.info('Strip url to %s', striped_url)

        if striped_url.endswith('?'):
            striped_url = striped_url[:-1]
            endswith_q = True

        # for path?#xxx special case
        if '?' in url and '#' in url and url.index('?') < url.index('#'):
            endswith_q = True

        new_url = map_func(striped_url)
        if new_url is None:
            logger.info('Cannot find %r', striped_url)
            result.append(content[previous:start])
            result.append(url)
            previous = end
            continue
        else:
            if ori_result.query or endswith_q:
                new_url = new_url + '?' + ori_result.query
            if ori_result.fragment:
                new_url = new_url + '#' + ori_result.fragment
        logger.info('Replace %s with %s', url, new_url)
        result.append(content[previous:start])
        result.append(new_url)
        previous = end
    result.append(content[previous:])
    return ''.join(result)
