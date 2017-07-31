import re
import os
import base64
import sys
import json
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '%s/../../src' % (cur_dir,))
import common
from Minify import Minify
from Converter import Converter
from Exceptions.FileImportException import FileImportException

class CSSMinify(Minify):
	_maxImportSize = 5;

	_importExtensions = {
		'gif':'data:image/gif',
		'png':'data:image/png',
		'jpe':'data:image/jpeg',
		'jpg':'data:image/jpeg',
		'jpeg':'data:image/jpeg',
		'svg':'data:image/svg+xml',
		'woff':'data:application/x-font-woff',
		'tif':'image/tiff',
		'tiff':'image/tiff',
		'xbm':'image/x-xbitmap'
	}

	def setMaxImportSize(self, size):
		self.maxImportSize = size

	def setImportExtensions(self, extensions):
		self.importExtensions = extensions

	def _moveImportsToTop(self, content):
		import_regex = '@import[^;]+;'
		matches = re.findall(import_regex, content)
		for imp in matches:
			content.replace(imp, "")
		content = "".join(matches) + content
		return content

	def _combineImports(self, source, content, parents):
		importRegexes = [
			'(@import\s+url\((?P<quotes>["\']?)(?P<path>.+?)(?P=quotes)\)\s*(?P<media>[^;]*)\s*;)',
			'(@import\s+(?P<quotes>["\'])(?P<path>.+?)(?P=quotes)\s*(?P<media>[^;]*)\s*;?)',
		]

		matches = [];
		for importRegex in importRegexes:
			regexMatches = re.findall(importRegex, content)
			matches = matches + regexMatches

		for match in matches:
			importPath = os.path.dirname(source.rstrip(os.pathsep)) or '.'
			importPath = importPath + '/' + match[2]

			if not self.canImportByPath(match[2]) or not self.canImportFile(importPath):
				pass
			else:
				if importPath in parents:
					raise FileImportException("Failed to import file \"%s\": circular reference detected." % (importPath,));

				minifier = (self.__class__)(importPath)
				importContent = minifier.execute(source, parents);

				if not match[3]:
					importContent = '@media %s{%s}' % (match[3], importContent,)
				search = match[0];
				replace = importContent;
				content = content.replace(search, replace)
		return content

	#++
	def _importFiles(self, source, content):
		url_regex = '(url\((?P<quotes>["\']?)(?P<path>.+?)(?P=quotes)\))'
		matches = re.findall(url_regex, content)
		if self._importExtensions and matches:
			for match in matches:
				extension = common.getFileExtension(match[2])
				if extension and not extension in self._importExtensions:
					pass
				else:
					path = os.path.dirname(source.rstrip(os.pathsep)) or '.'
					path = path + "/" + match[2]
					if self._canImportFile(path) and self._canImportBySize(path):
						importContent = self._load(path)
						importContent = base64.encodestring(importContent)
						search = match[0];
						replace = "url(%s;base64,%s)" % (self._importExtensions[extension], importContent, )
						content = content.replace(search, replace)
		return content

	def execute(self, path=None, parents=[]):
		content = ''
		for source in self._data:
			css = self._data[source]
			self._extractStrings()
			self._stripComments()

			css = self._replace(css)
			css = self._stripWhitespace(css)
			css = self._replaceNone(css)
			css = self._shortenZeroes(css)

			css = self._shortenRGBA(css)
			css = self._shortenRGB(css)
			css = self._shortenHex(css)
			css = self._shortenFontWeights(css)
			css = self._stripEmptyTags(css)
			css = self._stripExtraSemiColons(css)
			css = self._normalizeSelectors(css)
			css = self._restoreExtractedData(css)

			css = self._shrinkEdgeCaseAlpha(css)

			css = self._shrinkURLs(css)
			source2 = '' if isinstance(source, int) else source
			parents = parents + [source2] if source2 else parents

			css = self._combineImports(source2, css, parents)
			css = self._importFiles(source2, css)

			converter = self._getPathConverter(source2, path if path else source2)

			css = self._move(converter, css)

			content = content + css
			self._data[source] = css

		content = self._moveImportsToTop(content)
		return content

	def _move(self, converter, content):

		relativeRegexes = [
			'(url\(\s*(?P<quotes>["\'])?(?P<path>.+?)(?(quotes)(?P=quotes))\s*\))',
			'(@import\s+(?P<quotes>["\'])(?P<path>.+?)(?P=quotes))'
		]
		matches = []
		for relativeRegex in relativeRegexes:
			regexMatches = re.findall(relativeRegex, content)
			matches = matches + regexMatches

		for match in matches:
			import_regex = "(@import)"
			import_match = re.search(import_regex, match[0])
			cur_type = 'import' if import_match else 'url'
			url = match[2]

			if self._canImportByPath(url):
				param_marker_regex = "(\?)"
				param_position = re.search(param_marker_regex, url)
				param_position = param_position.start(1) if param_position else -1
				params = url[param_position:] if param_position >= 0 else ""
				url = url[:param_position] if param_position >= 0 else url
				url = converter.convert(url)
				url = url + params

			search = match[0]
			if cur_type == "url":
				replace = 'url(%s)' % (url, )
			elif cur_type == 'import':
				replace = '@import "%s"' % (url, )

			content.replace(search, replace)
		return content

	def _shortenHex(self, content):
		before_regex = r'(?<=[: ])'
		after_regex = r'(?=[; }!])'

		#shorten hexes where possible
		unnormalized_regex = r'(?i)%s(#([0-9a-z])\2([0-9a-z])\3([0-9a-z])\4)%s' % (before_regex, after_regex, )
		content = re.sub(unnormalized_regex, r'#\2\3\4', content)

		#get static conversions
		colors_file = "%s/data/color_table" % (cur_dir, )
		colors = json.loads(common.file_get_contents(colors_file))

		#minifies color names and color hexes
		colors_keys_regex = "(%s)" % ("|".join(str(key) for key in colors), )
		full_keys_regex = r'(?i)%s%s%s' % (before_regex, colors_keys_regex, after_regex, )
		matches = re.findall(full_keys_regex, content)
		if matches:
			for match in matches:
				content = content.replace(match, colors[match.upper()].lower())

		return content

	def _shortenRGB(self, content):
		before_regex = r'(?<=[: ])'
		after_regex = r'(?=[; }!])'
		full_rgb_regex = r"(rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\))"
		full_regex = "%s%s%s" % (before_regex, full_rgb_regex, after_regex, )
		matches = re.findall(full_regex, content)
		if matches:
			for match in matches:
				first = str(hex(int(match[1])))[2:]
				second = str(hex(int(match[2])))[2:]
				third = str(hex(int(match[3])))[2:]
				new_hex = "#%s%s%s" % (first, second, third, )
				content = content.replace(match[0], new_hex.lower())
		return content

	def _shortenRGBA(self, content):
		before_regex = r'(?<=[: ])'
		after_regex = r'(?=[; }!])'
		full_rgb_regex = r"(rgba\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*(0|1|\.[0-9]*)\s*\))"
		full_regex = "%s%s%s" % (before_regex, full_rgb_regex, after_regex, )
		matches = re.findall(full_regex, content)
		if matches:
			for match in matches:
				if match[4] == "0":
					content = content.replace(match[0], "rgba(0,0,0,0)")
				elif match[4] == "1":
					first = str(hex(int(match[1])))[2:]
					second = str(hex(int(match[2])))[2:]
					third = str(hex(int(match[3])))[2:]
					new_str = "rgb(%s,%s,%s)" % (first, second, third, )
					content = content.replace(match[0], new_str)
		return content

	def _shortenFontWeights(self, content):
		weights = {
			'normal':400,
			'bold':700,
		}

		weights_regex = "(%s)" % (("|".join(str(key) for key in weights)), )
		full_weights_regex = r'(font-weight\s*:\s*)%s((?=[;}]))' % (weights_regex, )
		matches = re.findall(full_weights_regex, content)
		if matches:
			for match in matches:
				search = "%s%s%s" % (match[0], match[1], match[2])
				replace = "%s%s%s" % (match[0], weights[match[1]], match[2])
				content = content.replace(search, replace)
		return content

	def _shortenZeroes(self, content):
		before_regex = r'(?<=[:(, ])'
		after_regex = r'(?=[ ,);}!])'
		units_regex = r'(em|ex|%|px|cm|mm|in|pt|pc|ch|rem|vh|vw|vmin|vmax|vm|s|deg|)'
		#units_regex2 = r'(em|ex|%|px|cm|mm|in|pt|pc|ch|rem|vh|vw|vmin|vmax|vm|s)'

		regex_1 = r"%s(-?0*(\.0+)?)(?<=0)%s%s" % (before_regex, after_regex, units_regex, )
		regex_2 = r"%s\.0+%s?%s" % (before_regex, after_regex, units_regex, )
		regex_3 = r"%s(-?[0-9]+\.[0-9]+)0+%s?%s" % (before_regex, after_regex, units_regex, )
		regex_4 = r"%s(-?[0-9]+)\.0+%s?%s" % (before_regex, after_regex, units_regex, )
		regex_5 = r"%s(-?)0+([0-9]*\.[0-9]+)%s?%s" % (before_regex, after_regex, units_regex, )
		regex_6 = r"%s-?0+%s?%s" % (before_regex, after_regex, units_regex, )
		regex_7 = r'\(([^\(\)]+) [\+\-] 0( [^\(\)]+)?\)'
		regex_8 = r'\(0 \+ ([^\(\)]+)\)'
		regex_9 = r'\(0 \- ([^\(\)]+)\)'
		regex_10 = r'flex:([^ ]+ [^ ]+ )0([;\}])'
		regex_11 = r'flex-basis:0([;\}])'

		previous = ""
		while content != previous:
			previous = content
			content = re.sub(regex_1, r'0', content)
			content = re.sub(regex_2, r'0', content)
			#content = re.sub(regex_2, r'0\1', content)
			content = re.sub(regex_3, r'\1\2', content)
			content = re.sub(regex_4, r'\1\2', content)
			content = re.sub(regex_5, r'\1\2\3', content)
			#content = re.sub(regex_6, r'0\1', content)
			content = re.sub(regex_6, r'0', content)
			content = re.sub(regex_7, r'(\1\2)', content)
			content = re.sub(regex_8, r'(\1)', content)
			content = re.sub(regex_9, r'(-\1)', content)
			content = re.sub(regex_10, r'flex:\1\0%\2', content)
			content = re.sub(regex_11, r'flex-basis:0%\1', content)

		return content

	def _stripEmptyTags(self, content):
		regex = r'(^|\}|;)[^\{\};]+\{\s*\}'
		return re.sub(regex, r'\1', content)

	def _stripComments(self, ):
		comment_regex_1 = r'(\s*\/\*(.|\s)*?\*\/\s*)'
		self._registerPattern(comment_regex_1, '')

	def _stripWhitespace(self, content):
		regex_1 = r'^\s*'
		regex_2 = r'\s*$'
		regex_3 = r'\s+'
		regex_4 = r'\s*([*$~^|]?\+=|[{};,>~]|!important\b)\s*'
		regex_5 = r'([\[(:])\s+'
		regex_6 = r'\s+([\]\)])'
		regex_7 = r'\s+(:)(?![^\}]*\{)'
		regex_8 = r'\s*([+-])\s*(?=[^}]*{)'
		regex_9 = r';}'
		regex_10 = r'\s{1}'

		previous = ""
		while content != previous:
			previous = content
			content = re.sub(regex_1, r'', content)
			content = re.sub(regex_2, r'', content)
			content = re.sub(regex_3, r' ', content)
			content = re.sub(regex_4, r'\1', content)
			content = re.sub(regex_5, r'\1', content)
			content = re.sub(regex_6, r'\1', content)
			content = re.sub(regex_7, r'\1', content)
			content = re.sub(regex_8, r'\1', content)
			content = re.sub(regex_9, r'}', content)
			content = re.sub(regex_10, r' ', content)
		return common.rtrim(common.ltrim(content))

	def _shrinkURLs(self, content):
		before_regex = r'(?<=[:(, ])'
		after_regex = r'(?=[ ,);}!])'
		regex = r'(url\(\s*(?P<quotes>["\'])?(?P<path>.+?)(?(quotes)(?P=quotes))\s*\))'
		full_regex = r"%s%s%s" % (before_regex, regex, after_regex, )
		matches = re.findall(full_regex, content)
		if matches:
			for match in matches:
				search = match[0]
				replace = "url(%s)" % (common.rtrim(common.ltrim(match[2])), )
				content = content.replace(search, replace)
		return content

	def _stripExtraSemiColons(self, content):
		regex = r"(\s*\;\s*)+"
		return re.sub(regex, ";", content)

	def _shrinkEdgeCaseAlpha(self, content):
		regex1 = r"(?<=-ms-filter:)(\s*([\"\'])progid:DXImageTransform.Microsoft.Alpha\(Opacity=([0-9]+)\)\2)(?=[ ,);}!])"
		regex2 = r"(?<=filter:)(\s*progid:\s*DXImageTransform.Microsoft.Alpha\(Opacity=([0-9]+)\))(?=[ ,);}!])"

		content = re.sub(regex1, r'"alpha(opacity=\3)"', content)
		content = re.sub(regex2, r"alpha(opacity=\2)", content)

		return content

	def _getFirstLayerBlocks(self, content, open_char=r"{", close_char=r"}"):
		extracted_blocks = {}
		working_placeholders = []
		temp_content = content
		previous_content = ""
		#extract layers and assemble placeholder blocks
		while previous_content != temp_content:
			previous_content = temp_content
			working_placeholders_regex = r"(%s)+" % (r"[^%s%s]*(%s)[^%s%s]*" % (open_char, close_char, r"|".join(working_placeholders).replace(open_char, "\%s" % (open_char, )).replace(close_char, "\%s" % (close_char, )), open_char, close_char, ), ) if working_placeholders else r"()"
			selector_regex = r"(%s)" % (r"%s[^%s%s]*%s[^%s%s]*%s" % (open_char, open_char, close_char, working_placeholders_regex, open_char, close_char, close_char, ), )
			matches = re.findall(selector_regex, temp_content)
			if matches:
				if working_placeholders:
					match = matches[0]
					toRemove = []
					for placeholder in working_placeholders:
						if placeholder in match[0]:
							toRemove.append(placeholder)
					for to in toRemove:
						working_placeholders.remove(to)
					placeholder = r"%s%s%s" % (open_char, str(len(extracted_blocks)), close_char, )
					working_placeholders.append(placeholder)
					extracted_blocks[placeholder] = match[0]
					temp_content = temp_content.replace(match[0], placeholder, 1)
				else:
					for match in matches:
						placeholder = r"%s%s%s" % (open_char, str(len(extracted_blocks)), close_char, )
						working_placeholders.append(placeholder)
						extracted_blocks[placeholder] = match[0]
						temp_content = temp_content.replace(match[0], placeholder, 1)

		#repopulate extracted blocks
		blocks = []
		placeholder_regex = "(%s)" % (r"|".join(str(key) for key in extracted_blocks).replace("{", "\{").replace("}", "\}"), )
		for selector in working_placeholders:
			prev = ""
			while prev != selector:
				prev = selector
				matches = re.findall(placeholder_regex, selector)
				if matches:
					for match in matches:
						selector = selector.replace(match, extracted_blocks[match], 1)
			blocks.append(selector)

		return blocks

	def _normalizeSelectors(self, content):
		selector_blocks = self._getFirstLayerBlocks(content)
		selectors = []
		full_selectors = []

		for block in selector_blocks:
			placeholder = r"{_1_}"
			content = content.replace(block, placeholder, 1)
			regex = r"[;}]?\s*(([^{}]*){_1_})"
			matches = re.findall(regex, content)
			if matches:
				match = matches[0]
				selector = match[1]
				full_selectors.append("%s%s" % (selector, block, ))
				selectors.append(selector)
				cur_str = "%s%s" % (match[1], placeholder, )
				content = content.replace(cur_str, "", 1)

		for selector in sorted(selectors):
			block = ""
			for full in full_selectors:
				if full.startswith("%s{" % (selector, )):
					if len(block) and block == full:
						full_selectors.remove(full)
					else:
						block = full
						full_selectors.remove(full)

			content += block

		return content

	def _mergeSelectors(self, first, second):
		common.ltrim(first, "{")
		common.rtrim(first, "}")
		common.ltrim(second, "{")
		common.rtrim(second, "}")

		first_statements = first.split(";")
		second_statements = second.split(";")

		first_args = {}
		regex = "([^{}]*)[:]?([{]?.*[}]?)"
		for statement in first_statment:
			matches = re.findall(regex, statement)


	def _replaceNone(self, content):
		before_regex = r'(?<=[:(, ])'
		after_regex = r'(?=[ ,);}!])'
		regex = r"(?i)none"
		full_regex = "%s%s%s" % (before_regex, regex, after_regex, )
		return re.sub(full_regex, "0", content)

	def _canImportBySize(self, path):
		size = os.path.getsize(path)
		return (size and size <= self._maxImportSize * 1024);

	def _canImportByPath(self, path):
		regex = r'^(data:|https?:|\/)'
		return (common.regexpos(path, regex) == 0)

	def _getPathConverter(self, source, target):
		return Converter(source, target)