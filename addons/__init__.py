import os, sys
from . import *
data = {}

dir_path = os.path.dirname(os.path.realpath(__file__))
sub_files = os.listdir(dir_path)
for dir in sub_files:
	if os.path.isdir("%s/%s" % (dir_path, dir,)):
		__import__("addons.%s" % dir)
		module = sys.modules["addons."+dir]
		if dir == "CSS":
			data[dir] = module.data if module and getattr(module, "data", None) else {}


#print data

#import os, sys
#dir_path = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(dir_path + '/..')
#print sys.path
#from src.utils.Imports import *
#import_Ify()

#print data