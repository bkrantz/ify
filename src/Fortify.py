#improve
from src import IfyProcessor, IfySubstituteMixin

class Fortify(IfyProcessor, IfySubstituteMixin):

	def _process(self, content):
		return self._cycle_substitutions(content=content)