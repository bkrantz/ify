from src import Minify
from addons.CSS import configs

class CSSMinify(Minify):

	_colors = json.loads(configs["color_table"}])
	_rgb = json.loads(configs["rgb_color_table"])
	_weights = {
		'normal':400,
		'bold':700
	}

	def __init__(self, *args, **kwargs):
		super(CSSMinify, self).__init__(*args, **kwargs)
		self._registerColorSubstitutions()
		self._registerZeroSubstitutions()
		self._registerStripSubstitutions()
		self._registerNoneSubstitutions()
		self._registerShrinkSubstitutions()
		self._registerFontWeightSubstitutions()

	def _process(self, content):
		content = super(CSSMinify, self)._process(content=content)
		return self._normalizeSelectors(content=content)

	'''
		Substitution Registration
	'''
	def _registerColorSubstitutions(self):
		_before_regex = r'(?<=[: ])'
		_after_regex = r'(?=[; }!])'
		_sub_rgb_regex = r"(rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\))"
		_sub_rgba_regex = r"(rgba\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*(0|1|\.[0-9]*)\s*\))"

		_color_regex1 = r'(?i)%s(#([0-9a-z])\2([0-9a-z])\3([0-9a-z])\4)%s' % (_before_regex, _after_regex, )
		_color_regex2 = r'(?i)%s%s%s' % (_before_regex, "(%s)" % ("|".join(str(key) for key in _colors), ), _after_regex, )
		_color_regex3 = r"%s%s%s" % (_before_regex, _sub_rgb_regex, _after_regex, )
		_color_regex4 = r"%s%s%s" % (_before_regex, _sub_rgba_regex, _after_regex, )

		self._substitutions[_color_regex1] = r'#\2\3\4'
		self._substitutions[_color_regex2] = self._colorCallback
		self._substitutions[_color_regex3] = self._rgbCallback
		self._substitutions[_color_regex4] = self._rgbaCallback

	def _registerFontWeightSubstitutions(self):
		weights_regex = "(%s)" % (("|".join(str(key) for key in weights)), )
		full_weights_regex = r'(font-weight\s*:\s*)%s((?=[;}]))' % (weights_regex, )

	def _registerZeroSubstitutions(self):
		before_regex = r'(?<=[:(, ])'
		after_regex = r'(?=[ ,);}!])'
		units_regex = r'(em|ex|%|px|cm|mm|in|pt|pc|ch|rem|vh|vw|vmin|vmax|vm|s|deg|)'
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
		self._substitutions[regex_1] = r'0'
		self._substitutions[regex_2] = r'0'
		self._substitutions[regex_3] = r'\1\2'
		self._substitutions[regex_4] = r'\1\2'
		self._substitutions[regex_5] = r'\1\2\3'
		self._substitutions[regex_6] = r'0'
		self._substitutions[regex_7] = r'(\1\2)'
		self._substitutions[regex_8] = r'(\1)'
		self._substitutions[regex_9] = r'(-\1)'
		self._substitutions[regex_10] = r'flex:\1\0%\2'
		self._substitutions[regex_11] = r'flex-basis:0%\1'

	def _registerStripSubstitutions(self):
		self._substitutions[r'(^|\}|;)[^\{\};]+\{\s*\}'] = r'\1'

		self._substitutions[r'^\s*'] = r''
		self._substitutions[r'\s*$'] = r''
		self._substitutions[r'\s+'] = r' '
		self._substitutions[r'\s*([*$~^|]?\+=|[{};,>~]|!important\b)\s*'] = r'\1'
		self._substitutions[r'([\[(:])\s+'] = r'\1'
		self._substitutions[r'\s+([\]\)])'] = r'\1'
		self._substitutions[r'\s+(:)(?![^\}]*\{)'] = r'\1'
		self._substitutions[r'\s*([+-])\s*(?=[^}]*{)'] = r'\1'
		self._substitutions[r';}'] = r'}'
		self._substitutions[r'\s{1}'] = r' '
		self._substitutions[r'([^\s])\s*$'] = r'\1'
		self._substitutions[r'^\s*([^\s])'] = r'\1'

		self._substitutions[r"(\s*\;\s*)+"] = r';'

	def _registerNoneSubstitutions(self:):
		before_regex = r'(?<=[:(, ])'
		after_regex = r'(?=[ ,);}!])'
		regex = r"(?i)none"
		self._substitutions["%s%s%s" % (before_regex, regex, after_regex, )] = r"0"

	def _registerShrinkSubstitutions(self):
		before_regex = r'(?<=[:(, ])'
		after_regex = r'(?=[ ,);}!])'
		regex = r'(url\(\s*(?P<quotes>["\'])?(?P<path>.+?)(?(quotes)(?P=quotes))\s*\))'
		full_regex = r"%s%s%s" % (before_regex, regex, after_regex, )

		self._substitutions[full_regex] = self._removeWhitespaceCallback
		self._substitutions[r"(?<=-ms-filter:)(\s*([\"\'])progid:DXImageTransform.Microsoft.Alpha\(Opacity=([0-9]+)\)\2)(?=[ ,);}!])"] = r'"alpha(opacity=\3)"'
		self._substitutions[r"(?<=filter:)(\s*progid:\s*DXImageTransform.Microsoft.Alpha\(Opacity=([0-9]+)\))(?=[ ,);}!])"] = r"alpha(opacity=\2)"

	'''
		Callbacks
	'''
	def _colorCallback(self, match):
		return self._colors[match.upper()].lower()

	def _rgbCallback(self, match):
		match = re.sub(r"\s+", "", match)
		match = re.sub(r"rgb\((.*)\)", r"\1", match)
		return self._rgb[match].lower()

	def _rgbaCallback(self, match):
		compressed = re.sub(r"\s+", "", match)
		nums = re.sub("rgba\((.*)\)", r"\1", compressed)
		nums = nums.split(",")
		opacity = nums[3]
		if opacity == "0":
			return "rgba(0,0,0,0)"
		elif opacity == "1":
			return "rgb(%s)" % ",".join(nums[:2])
		return compressed

	def _fontWeightCallback(self, match):
		for key, value in self._weights.iteritems():
			match = re.sub(key, value, match)
		return match

	'''
		Other
	'''

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

	#TODO unused?
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