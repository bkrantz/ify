import os
import sys
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/../../src' % (cur_dir,))
from Fly import Fly
import simplejson as json

format = "html"
extension = "html"
className = "HTMLFly"

def getInstance(raw_content, actions, tab):
	return HTMLFly(raw_content, actions, tab)

class HTMLFly(Fly):
	pass