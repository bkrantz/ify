from src import *
import re
import abc
import os

class IfyExtractor:

	_extracted = {}
	_patterns = {}

	def __init__(self, *args, **kwargs):
		self._name = os.path.dirname(os.path.realpath(__file__))

	def _registerPattern(self, pattern, replacement=''):
		self._patterns[pattern] = replacement

	def _replacePattern(self, pattern, replacement, content):
		if callable(replacement):
			match = re.search(pattern, content)
			if match:
				return re.sub(pattern, replacement(content[match.start():match.end()]), content, 1)   
		else:
			return re.sub(pattern, replacement, content, 1)
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

	def _findFirstPattern(self, content, patterns):
		patterns_found, first_position, first_pattern = {}, len(content), None
		for pattern, replacement in patterns.iteritems():
			match = re.search(pattern, content)
			if match:
				patterns_found[pattern] = replacement
				start = match.start()
				if start < first_position and start >= 0:
					first_position = start
					first_pattern = pattern
		return first_pattern, patterns_found

	def _extract(self, content):
		self._registerExtracts()
		return self._replace(content=content)

	def process(self, data=None):
		data = self.data if not data else data
		self._preHook()
		self.data = self._process(data=data)
		self._postHook()

	def _extractCallback(self, match, placeholderTemplate="({})"):
		count = len(self._extracted)
		placeholder = placeholderTemplate.format(str(len(self._extracted)))
		self._extracted[placeholder] = match
		return placeholder

	def _process(self, data):
		raise NotImplementedError

	def _registerExtracts(self):
		raise NotImplementedError

	def _preHook(self):
		pass

	def _postHook(self):
		pass

class Ify(IfyExtractor):
	#static
	extensions = []
	_fortifyClass = "Fortify"
	_minifyClass = "Minify"
	_notifyClass = "Notify"
	_pretifyClass = "Pretify"
	_validifyClass = "Validify"

	#extract regexes
	_stringRegexes = [
		r"([\"\'])[\x00-\x7F]*?(?<!\\)(\\\\)*\1"
	]
	_commentRegexes = []
	_additionalRegexes = []

	#extract templates
	_stringsPlaceholderTemplate = "\"({})\""
	_stringsPlaceholderTemplateRegex = r"\"\(\d+\)\""
	_commentsPlaceholderTemplate = "#({})#"
	_commentsPlaceholderTemplateRegex = r"#\(\d+\)#"
	_additionalsPlaceholderTemplate = "\'({})\'"
	_additionalsPlaceholderTemplateRegex = r"\'\(\d+\)\'"

	def __init__(self, data=None, configs={}, fortify=False, minify=False, notify=False, pretify=False, validify=False, *args, **kwargs):
		self.data = data
		self.configs = configs[self.name]
		self._fortify = globals()[self._fortifyClass](configs=self.configs) if fortify else None
		self._minify = globals()[self._minifyClass](configs=self.configs, _comment_regex=self._comment_placeholder_template_regex) if minify else None 
		self._pretify = globals()[self._notifyClass](configs=self.configs) if pretify else None 
		self._notify = globals()[self._pretifyClass](configs=self.configs) if notify else None 
		self._validify = globals()[self._validifyClass](configs=self.configs) if validify else None

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

		data = self._extract(content=data)

		data = self._minify.process(data) if self._minify else data
		data = self._fortify.process(data) if self._fortify else data
		data = self._notify.process(data) if self._notify else data
		data = self._pretify.process(data) if self._pretify else data

		data = self._restoreExtractedData(data)

	def _registerExtracts(self):
		for regex in self._stringRegexes:
			self._registerPattern(regex, self._extractStringsCallback)
		for regex in self._commentRegexes:
			self._registerPattern(regex, self._extractCommentsCallback)
		for regex in self._additionalRegexes:
			self._registerPattern(regex, self._extractAdditionalsCallback)

	def _extractCommentsCallback(self, match):
		return self._extractCallback(match=match, placeholderTemplate=self._commentsPlaceholderTemplate)

	def _extractAdditionalsCallback(self, match):
		return self._extractCallback(match=match, placeholderTemplate=self._additionalsPlaceholderTemplate)

	def _extractStringsCallback(self, match):
		return self._extractCallback(match=match, placeholderTemplate=self._stringsPlaceholderTemplate)