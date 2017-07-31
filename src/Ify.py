class Ify:
	#static
	extension_regex = ".*"
	_fortify_class = ""
	_minify_class = ""
	_notify_class = ""
	_pretify_class = ""
	_validify_class = ""

	#extract
	_string_regexes = []
	_comment_regexes = []
	_additional_regexes = []
	_extract_comments = True
	_placeholder_template = "#({})#"
	_placeholder_template_regex = r"#\(\d+\)#"

	'''
		key = placeholder value
		value = extracted value
	'''
	_extracted = {}

	def __init__(self, data=None, fortify=False, minify=False, notify=False, pretify=False, validify=False, *args, **kwargs):
		self.data = data
		self.configs = {}
		self.fortify = self._fortify_class(configs=self.configs) if fortify else None
		self.minify = self._fortify(configs=self.configs) if minify else None 
		self.pretify = self._fortify(configs=self.configs) if pretify else None 
		self.notify = self._fortify(configs=self.configs) if notify else None 
		self._validify = self._fortify(configs=self.configs) if validify else None 

	'''
		Sequence of Events
			Validify
			Text Extractions
			Minify
			Fortify
			Notify
			Pretify
			Text Return
	'''
	def execute(self):
		self._pre_hook()
		self.data = self._extract(data)

		self._post_hook()
		pass

	def _pre_hook(self):
		pass

	def _post_hook(self):
		pass

	def _extract(self,):
		pass

	def _get_extract_patterns(self):
		pass

	def _return_extracts(self):
		pass


