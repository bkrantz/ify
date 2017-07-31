

import re
import sys
import os
import json
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/../src' % (cur_dir,))
from common import *
from Converter import *

lista = ['a', 'b', 'c', 'd']
listb = ['a', 'c', 'e', 'f']
print array_diff(lista, listb)
'''
print str(hex(int("230")))

my_dir = cur_dir + "/../addons/CSS/data/color_table"

colors = json.loads(common.file_get_contents(my_dir))
print colors['BLACK']
print len(colors)
#print colors
#print json.dumps(colors, indent=4)

#'''