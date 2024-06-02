import os
import sys

class Locator:
    def __init__(self,root):
        self._root = os.path.abspath(root)
        
        
    def sublocator(self,subdir):
        path = os.path.join (self._root,subdir)
        os.makedirs(path,exist_ok = True)
        return Locator (path)

    def makeFile (self,filename):
        return open (os.path.join (self._root,filename),'w')

    def makeFilePath (self,filename):
        return os.path.join (self._root,filename)


class Progresser:
    def __enter__(self):
        sys.stdout.write ("\n")
        return self
    
    def __exit__ (self, exc_type, exc_value, exc_traceback):
        sys.stdout.write ("\n")
        
    def message (self,string):
        sys.stdout.write ("\r\u001b[0J{0}".format(string))

