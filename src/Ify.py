class Ify:
	#static
	extension_regex = ".*"
	_fortify_class = "Fortify"
	_minify_class = "Minify"
	_notify_class = "Notify"
	_pretify_class = "Pretify"
	_validify_class = "Validify"

	#extract
	_string_regexes = []
	_comment_regexes = []
	_additional_regexes = []
	_extracted_strings = {}
	_extracted_comments = {}
	_extracted_additionals = {}

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
		self._fortify = self._fortify_class(configs=self.configs) if fortify else None
		self._minify = self._minify_class(configs=self.configs) if minify else None 
		self._pretify = self._notify_class(configs=self.configs) if pretify else None 
		self._notify = self._pretify_class(configs=self.configs) if notify else None 
		self._validify = self._validify_class(configs=self.configs) if validify else None

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
	def process(self):
		self._pre_hook()

		if self._validify and not self._validify.is_valid(self.data):
			raise InvalidContentException

		self.data = self._extract(self.data)

		self.data = self._minify.process(self.data) if self._minify else self.data
		self.data = self._fortify.process(self.data) if self._fortify else self.data
		self.data = self._notify.process(self.data) if self._notify else self.data
		self.data = self._pretify.process(self.data) if self._pretify else self.data

		self.data = self._return_extracts(self.data)

		self._post_hook()

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


