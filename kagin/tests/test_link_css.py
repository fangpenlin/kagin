import unittest

class TestLinkFile(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_replace_css_links(self):
        from kagin.link_css import replace_css_links
        file_map = {
            'test-image01.jpg': 'new-image01.jpg',
            'test-image02.png': 'new-image02.png',
            'test-image03.gif': 'new-image03.gif',
            'foo/bar/test_image04.gif': 'new-image04.gif',
            'icon.png': 'new-icon.png'
        }
        
        def map_func(path):
            return file_map.get(path)
        
        def test_replace(input, expected):
            result = replace_css_links(input, map_func)
            self.assertEqual(result, expected)
            
        test_replace(
            """html { background-image: url(test-image01.jpg); }""",
            """html { background-image: url(new-image01.jpg); }""",
        )
        test_replace(
            """html { background-image: url (test-image01.jpg); }""",
            """html { background-image: url (new-image01.jpg); }""",
        )
        test_replace(
            """html { background-image: url ( test-image01.jpg ); }""",
            """html { background-image: url ( new-image01.jpg ); }""",
        )
        test_replace(
            """html { background-image: url('test-image02.png'); }""",
            """html { background-image: url('new-image02.png'); }""",
        )
        test_replace(
            """html { background-image: url(  'test-image02.png'  ); }""",
            """html { background-image: url(  'new-image02.png'  ); }""",
        )
        test_replace(
            """html { background-image: url("test-image03.gif"); }""",
            """html { background-image: url("new-image03.gif"); }""",
        )
        test_replace(
            """html { background-image: url("foo/bar/test_image04.gif"); }""",
            """html { background-image: url("new-image04.gif"); }""",
        )
        test_replace(
            """html { background-image: url("/icon.png"); }""",
            """html { background-image: url("/icon.png"); }""",
        )
        test_replace(
            """html { background-image: url("http://now.in/icon.png"); }""",
            """html { background-image: url("http://now.in/icon.png"); }""",
        )
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLinkFile))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')