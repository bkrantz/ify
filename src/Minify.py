from src import IfyExtractor

class Minify(IfyExtractor):
	
	def __init__(self, configs, *args, **kwargs):
		super(Minify, self).__init__(*args, **kwargs)
		self.configs = configs

	def _process(self, data):
		pass
