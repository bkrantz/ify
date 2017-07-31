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

print data