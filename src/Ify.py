
class IfyExtractor:

	self._extracted = {}
	self._patterns = {}

	def _registerPattern(self, pattern, replacement=''):
        self._patterns[pattern] = replacement

    def _replacePattern(self, pattern, replacement, content):
    	try:
    		return re.sub(pattern, replacement, content, 1)
    		#TODO Identify what error is thrown when sub is called to be replace with callable
    	except Exception:
            match = re.search(pattern, content)
            if match:
                return re.sub(pattern, replacement(content[match.start():match.end()]), content, 1)            
        return content

    def _restoreExtractedData(self, content):
        if not self._extracted:
            return content
        for key, value in self._extracted.iteritems():
            content = content.replace(key, value)
        self._extracted = {}
        return content

	def _replace(self, content):
		processed = ""
		pattern, patterns = self._findFirstPattern(content, self._patterns)
		while pattern:
			match = re.search(pattern, content)
			start, end = match.start(), match.end()
			match = content[start:end]
            replacement = self._replacePattern(pattern, patterns[pattern], content)
            content = content[end:]
            processed = "%s%s" % (processed, replacement[:len(replacement)-len(content)])
			pattern, patterns = self._findFirstPattern(content, patterns)
		return "%s%s" % (processed, content)

	def _findFirstPattern(self, content):
		patterns_found, first_position, first_pattern = {}, len(content), None
		for pattern, replacement in self._patterns.iteritems():
			match = re.search(pattern, content)
			if match:
				patterns_found[pattern] = replacement
				start = match.start()
				if start < first_position and start >= 0:
					first_position = start
					first_pattern = pattern
		return first_pattern, patterns_found

	def _extract(self,):
		self._registerExtracts()
		return self._replace()

	#can I default to self value?
	def process(self, data=self.data):
		self._preHook()
		self.data = self._process(data=data)
		self._postHook()

	def _extractCallback(self, match, placeholderTemplate="({})"):
		count = len(self._extracted)
        placeholder = placeholderTemplate.format(str(len(self._extracted)))
        self._extracted[placeholder] = match
        return placeholder

	def _registerExtracts(self):
		pass

	def _preHook(self):
		pass

	def _postHook(self):
		pass

class Ify(IfyExtractor):
	#static
	extension_regex = ".*"
	_fortify_class = Fortify
	_minify_class = Minify
	_notify_class = Notify
	_pretify_class = Pretify
	_validify_class = Validify

	#extract regexes
	_string_regexes = []
	_comment_regexes = []
	_additional_regexes = []

	#extract templates
	_strings_placeholder_template = "\"({})\""
	_strings_placeholder_template_regex = r"\"\(\d+\)\""
	_comments_placeholder_template = "#({})#"
	_comments_placeholder_template_regex = r"#\(\d+\)#"
	_additionals_placeholder_template = "\'({})\'"
	_additionals_placeholder_template_regex = r"\'\(\d+\)\'"

	def __init__(self, data=None, fortify=False, minify=False, notify=False, pretify=False, validify=False, *args, **kwargs):
		self.data = data
		self.configs = {}
		self._fortify = self._fortify_class(configs=self.configs) if fortify else None
		self._minify = self._minify_class(configs=self.configs, _comment_regex=self._comment_placeholder_template_regex) if minify else None 
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
	def _process(self, data):
		if self._validify and not self._validify.isValid(data):
			raise InvalidContentException

		data = self._extract(data)

		data = self._minify.process(data) if self._minify else data
		data = self._fortify.process(data) if self._fortify else data
		data = self._notify.process(data) if self._notify else data
		data = self._pretify.process(data) if self._pretify else data

		data = self._restoreExtractedData(data)

	def _registerExtracts(self):
		for regex in self._string_regexes:
			self._registerPattern(regex, self._extractStringsCallback)
		for regex in self._comment_regexes:
			self._registerPattern(regex, self._extractCommentsCallback)
		for regex in self._additional_regexes:
			self._registerPattern(regex, self._extractAdditionalsCallback)

	def _extractCommentsCallback(self, match):
		self._extractCallback(match=match, placeholderTemplate=self._commentsPlaceholderTemplate)

	def _extractAdditionalsCallback(self, match):
		self._extractCallback(match=match, placeholderTemplate=self._additionalsPlaceholderTemplate)

	def _extractStringsCallback(self, match):
        self._extractCallback(match=match, placeholderTemplate=self._stringsPlaceholderTemplate)