from src import IfyProcessor, IfySubstituteMixin

class Minify(IfyProcessor, IfySubstituteMixin):
	
	def __init__(self, comment_regex=None, *args, **kwargs):
		super(Minify, self).__init__(*args, **kwargs)
		if comment_regex:
			self._substitutions[comment_regex] = ''

	def _process(self, content):
		return self._cycle_substitutions(content=content)

	def _removeWhitespaceCallback(self, match):
		return re.sub(r"\s+", "", match)
