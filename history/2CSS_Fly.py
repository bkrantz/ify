import sys
import os
import simplejson as json
import shlex
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/../../src' % (cur_dir,))
from Fly import Fly
from CSS_Minify import CSSMinify
from Minify import Minify
import common

format = "css"
extension = "css"
className = "CSSFly"

def getInstance(input_file, actions, tab):
	return CSSFly(input_file, actions, tab)

class CSSFly(Fly):

	def isValid(self,):
		try:
			return True
		except Exception as e:
			return False

	def _minify(self,):
	    self._initial_size = os.path.getsize(self._input_file)
	    minifier = CSSMinify(self._input_file)
	    self._minified_content = minifier.minify(self._input_file)
	    self._total_input_size = Minify._total_input_size
	    self._content_size = minifier._minified_size

	def _pretify(self,):
		tab_cnt = 0
		processed = ""
		content = self._minified_content

		while len(content):
			open_bracket = common.regexpos(content, "{")
			close_bracket = common.regexpos(content, "}")
			end_line = common.regexpos(content, ";")

			shortest = open_bracket
			if ((close_bracket >= 0 and close_bracket < shortest) or shortest < 0):
				shortest = close_bracket
			if ((end_line >= 0 and end_line < shortest) or shortest < 0):
				shortest = end_line

			if shortest >= 0:
				if open_bracket == shortest:
					processed += "\n%s%s" % (self._tab * tab_cnt, content[:shortest+1], )
					tab_cnt += 1
				elif close_bracket == shortest:
					if close_bracket != 0:
						processed += "\n%s%s" % (self._tab * tab_cnt, content[:shortest], )
					tab_cnt -= 1
					processed += "\n%s%s" % (self._tab * tab_cnt, content[shortest:shortest+1], )
				elif end_line == shortest:
					processed += "\n%s%s" % (self._tab * tab_cnt, content[:shortest+1], )
				content = content[shortest+1:]
			else:
				processed += "\n%s" % (content, )
				content = ""

		self._pretty_content = processed
		self._content_size = len(self._pretty_content)

