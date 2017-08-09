from src import *
import re
import abc
import os

class IfyProcessor:

	def __init__(self, configs={}, *args, **kwargs):
		self._name = os.path.dirname(os.path.realpath(__file__))
		self._configs = configs[self._name]

	def process(self, content):
		self._preHook()
		content = self._process(content=content)
		self._postHook()
		return content

	def _process(self, content):
		raise NotImplementedError

	def _preHook(self):
		pass

	def _postHook(self):
		pass

class IfyReplaceMixin:

	def _replacePattern(self, pattern, replacement, content):
		if callable(replacement):
			match = re.search(pattern, content)
			if match:
				return re.sub(pattern, replacement(match=content[match.start():match.end()]), content, 1)   
		else:
			return re.sub(pattern, replacement, content, 1)
		return content

class IfySubstituteMixin(IfyReplaceMixin):

	_substitutions = {}

	def __init__(self, *args, **kwargs):
		self._registerSubstitutions()

	def _process_substitution(self, pattern, replacement, content):
		prev = None
		while not prev == content:
			prev = content
			content = self._replacePattern(pattern=pattern, replacement=replacement, content=content)
		return content

	def _cycle_substitutions(self, content):
		prev = None
		while not prev == content:
			prev = content
			for pattern, replacement in self._substitutions.iteritems():
				content = self._process_substitution(content=content)
		return content

	def _registerSubstitutions(self):
		pass

class IfyPatternMixin:

	def _findFirstPattern(self, content, patterns):
		try:
			return self._findFirstPatternDict(content=content, patterns=patterns)
		except AttributeError:
			pass
		try:
			return self._findFirstPatternList(content=content, patterns=patterns)
		except Exception:
			pass
		return content

	def _findFirstPatternDict(self, content, patterns):
		patterns_found, first_position, first_pattern = {}, len(content), None
		for pattern, value in patterns.iteritems():
			match = re.search(pattern, content)
			if match:
				patterns_found[pattern] = value
				start = match.start()
				if start < first_position and start >= 0:
					first_position = start
					first_pattern = pattern
		return first_pattern, patterns_found

	def _findFirstPatternList(self, content, patterns):
		patterns_found, first_position, first_pattern = [], len(content), None
		for pattern in patterns:
			match = re.search(pattern, content)
			if match:
				patterns_found.append(pattern)
				start = match.start()
				if start < first_position and start >= 0:
					first_position = start
					first_pattern = pattern
		return first_pattern, patterns_found


class IfyExtractorMixin(IfyReplaceMixin, IfyPatternMixin):

	_extracted = {}
	_patterns = {}

	def _registerPattern(self, pattern, replacement=''):
		self._patterns[pattern] = replacement

	def _restoreExtractedContent(self, content):
		if not self._extracted:
			return content
		for key, value in self._extracted.iteritems():
			self._restoreHook(key=key, value=value, content=content)
			content = content.replace(key, value)
		self._extracted = {}
		return content

	#first come first serve
	def _fcfsReplace(self, content):
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

	def _extract(self, content):
		self._registerExtracts()
		return self._fcfsReplace(content=content)

	def _extractCallback(self, match, placeholderTemplate="({})"):
		count = len(self._extracted)
		placeholder = placeholderTemplate.format(str(len(self._extracted)))
		self._extracted[placeholder] = match
		return placeholder

	def _registerExtracts(self):
		raise NotImplementedError

	def _restoreHook(self, key, value, content):
		pass

class Ify(IfyProcessor, IfyExtractorMixin):

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

	def __init__(self, fortify=False, minify=False, notify=False, pretify=False, validify=False, *args, **kwargs):
		super(Ify, self).__init__(*args, **kwargs)
		self._fortify = globals()[self._fortifyClass](configs=self.configs) if fortify else None
		self._minify = globals()[self._minifyClass](configs=self.configs, comment_regex=self._comment_placeholder_template_regex) if minify else None 
		self._pretify = globals()[self._notifyClass](configs=self.configs) if pretify else None 
		self._notify = globals()[self._pretifyClass](configs=self.configs) if notify else None 
		self._validify = globals()[self._validifyClass](configs=self.configs) if validify else None
		self._registerExtracts()

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
	def _process(self, content):
		if self._validify and not self._validify.isValid(content):
			raise InvalidContentException

		content = self._extract(content=content)

		content = self._minify.process(content) if self._minify else content
		content = self._fortify.process(content) if self._fortify else content
		content = self._notify.process(content) if self._notify else content
		content = self._pretify.process(content) if self._pretify else content

		return self._restoreExtractedContent(content)

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

	def _restoreHook(self, key, value, content):
		if self._notify:
			self._notify.updateFlags(key=key, value=value, content=content)