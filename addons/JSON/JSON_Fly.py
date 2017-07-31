import os
import sys
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/../../src' % (cur_dir,))
from Fly import Fly
import simplejson as json

format = "json"
extension = "json"
className = "JsonFly"

def getInstance(raw_content, actions, tab):
	return JsonFly(raw_content, actions, tab)

class JsonFly(Fly):

	def isValid(self,):
		try:
			self._raw_content = json.loads(self._raw_content)
			return True
		except Exception as e:
			return False

	def _simplify(self,):
		self._simple_content = json.dumps(self._raw_content)

	def _pretify(self,):
		self._pretty_content = json.dumps(self._raw_content, indent=self._tab)

	def _compress(self,):
		self._compressed_content = self._simple_content