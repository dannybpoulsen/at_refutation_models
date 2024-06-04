import os
import subprocess




libdir = os.path.join (os.path.dirname(os.path.abspath(__file__)))

def getlib (directory = libdir):
    build_dir = os.path.join (directory,"build")
    os.makedirs (build_dir,exist_ok = True)
    subprocess.run (["cmake",f"{libdir}"],cwd=build_dir) 
    subprocess.run (["make"],cwd=build_dir) 
    return os.path.join (build_dir,"liblogger.so")

    
