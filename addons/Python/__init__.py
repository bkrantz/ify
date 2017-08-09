import os
from load_resources import load_resources

#from python_flags import *

path = os.path.dirname(__file__)

data = load_resources(os.path.join(path, 'data'), extensions=['json'])
