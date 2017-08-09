#add spacing

class IfyComplexPretifyMixin:

	_newLineBeforeRegexes = []
	_newLineAfterRegexes = []
	_spaces_per_tab = 4

	def _insertNewLines(self, content):
		for regex in self._newLineBeforeRegexes:
			match = re.search(regex, content)
			if match:
				start = match.start()
				content = "%s\n%s" % (content[:start], content[start:])
		for regex in self._newLineAfterRegexes:
			match = re.search(regex, content)
			if match:
				end = match.end()
				content = "%s\n%s" % (content[:end], content[:end])
		return content

class IfySimplePretifyMixin(IfyPatternMixin):

	_currentIndentNumber = 0
	_indentRegexes = []
	_newLineRegexes = []
	_revereseIndentRegexes = []

	def _incrementIndent(self):
		self._current_indent_number+=1

	def _decrementIndent(self):
		self._current_indent_number-=1

	def _processIndents(self, content):
		regexes = self._indentRegexes + self._newLineRegexes + self._revereseIndentRegexes

class Pretify(IfyProcessor):

	_indent = "\t"



	def _