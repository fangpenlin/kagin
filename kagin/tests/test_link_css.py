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

    def test_query(self):
        from kagin.link_css import replace_css_links
        file_map = {
            'icon.png': 'new-icon.png'
        }
        
        def map_func(path):
            return file_map.get(path)
        
        def test_replace(input, expected):
            result = replace_css_links(input, map_func)
            self.assertEqual(result, expected)

        test_replace(
            """html { background-image: url("icon.png?a=123&b=456"); }""",
            """html { background-image: url("new-icon.png?a=123&b=456"); }""",
        )

        test_replace(
            """html { background-image: url("icon.png?"); }""",
            """html { background-image: url("new-icon.png?"); }""",
        )

        test_replace(
            """html { background-image: url("icon.png?1"); }""",
            """html { background-image: url("new-icon.png?1"); }""",
        )

        test_replace(
            """html { background-image: url("icon.png?#1"); }""",
            """html { background-image: url("new-icon.png?#1"); }""",
        )

    def test_replace_fonts(self):
        from kagin.link_css import replace_css_links
        file_map = {
            'fontawesome-webfont.eot': 'hashed.eot',
            'fontawesome-webfont.woff': 'hashed.woff',
            'fontawesome-webfont.ttf': 'hashed.ttf',
        }
        
        def map_func(path):
            return file_map.get(path)

        css = """
        @font-face {
          font-family: 'FontAwesome';
          src: url('fontawesome-webfont.eot?v=3.0.1');
          src: url('fontawesome-webfont.eot?#iefix&v=3.0.1') format('embedded-opentype'),
            url('fontawesome-webfont.woff?v=3.0.1') format('woff'),
            url('fontawesome-webfont.ttf?v=3.0.1') format('truetype');
          font-weight: normal;
          font-style: normal;
        }"""

        result = replace_css_links(css, map_func)

        expected = """
        @font-face {
          font-family: 'FontAwesome';
          src: url('hashed.eot?v=3.0.1');
          src: url('hashed.eot?#iefix&v=3.0.1') format('embedded-opentype'),
            url('hashed.woff?v=3.0.1') format('woff'),
            url('hashed.ttf?v=3.0.1') format('truetype');
          font-weight: normal;
          font-style: normal;
        }"""
        self.assertMultiLineEqual(result, expected)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLinkFile))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')