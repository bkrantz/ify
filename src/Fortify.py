#improve

class Fortify(IfyExtractor):
	'''
		key = regex
		value = replacement
	'''
	_substititions = {}

	def __init__(self, configs, *args, **kwargs):
		self.configs = configs
		super(Fortify, self).__init__(*args, **kwargs)

	def _process(self, data):
		self._process_substitutions(content=data)

	def _process_substitutions(self, content):
		for key,value in self._substititions.iteritems():
			re.sub(key, value, content)