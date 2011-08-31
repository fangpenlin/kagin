import unittest

class TestHashFile(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def make_one(self, *args, **kwargs):
        from kargin.hash import HashFile
        return HashFile(*args, **kwargs)
    
    def test_url_path(self):
        from kagin.utils import url_path
        
        def assert_url_path(path, base, output):
            self.assertEqual(url_path(path, base), output) 
            
        assert_url_path('/base/testfile', '/base', 'testfile')
        assert_url_path('/base/dir/', '/base', 'dir/')
        assert_url_path('/base/a/myfile', '/base', 'a/myfile')
        assert_url_path('/base/a/../myfile', '/base', 'myfile')
        assert_url_path('/base/a/b/../myfile', '/base', 'a/myfile')
        assert_url_path('c:\\base\\myfile.txt', 'c:\\base', 'myfile.txt')
        assert_url_path('c:\\base\\dir\\', 'c:\\base', 'dir/')
        assert_url_path('c:\\base\\a\\myfile.txt', 'c:\\base', 'a/myfile.txt')
        assert_url_path('c:\\base\\a\\..\\myfile.txt', 
                        'c:\\base', 'myfile.txt')
        assert_url_path('c:\\base\\a\\b\\..\\myfile.txt', 
                        'c:\\base', 'a/myfile.txt')
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHashFile))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')
    