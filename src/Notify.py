# point out potential points of interest
from src import IfyProcessor, IfyPatternMixin

class Notify(IfyProcessor, IfyPatternMixin):

	'''
		key = regex
		value = group number
	'''
	_yellow_flag_regexes = {}
	_red_flag_regexes = {}

	'''
		key = line_number
		value = (character_number, match)
	'''
	red_flags = {}
	yellow_flags = {}

	def _process(self, content):
		self.red_flags = self._identify_flags(content=content, regex_dict=self._red_flag_regexes)
		self.yellow_flags = self._identify_flags(content=content, regex_dict=self._yellow_flag_regexes)
		return content

	def _identify_flags(self, content, regex_dict):
		flags = {}
		processed_content = ""
		regex, regexes = self._findFirstPattern(content=content, patterns=regex_dict)
		while regex:
			match = re.search(regex, content)
			group_number = regexes[regex]
			start, end = match.start(group_number), match.end(group_number)
			processed_content += content[:start]
			group, content = content[start:end], content[end:]
			line_number = processed_content.count("\n")+1
			char_number = len(processed_content) - processed_content.rfind("\n")
			processed_content += group
			group = match.group(regex_dict[regex])
			if not self._is_key(dict=flags, key=line_number):
				flags[line_number] = char_number, group
			regex, regexes = self._findFirstPattern(content, regexes)
		return flags

	def _is_key(self, dict, key):
		for actKey in dict.iterKeys():
			if actKey == key:
				return True
		return False

	def updateFlags(self, key, value, content):
		processed_content = ""
		match = re.search(key, content)
		while match:
			start, end = match.start(), match.end()
			temp = processed_content + content[:end]
			processed_content += content[:start]
			lines_b4 = temp.count("\n")+1
			chars_b4 = len(temp) - temp.rfind("\n")
			self.red_flags = self._updateFlagSet(content=processed_content, flagDict=self.red_flags, value=value, linesB4=lines_b4, charsB4=chars_b4)
			self.yellow_flags = self._updateFlagSet(content=processed_content, flagDict=self.yellow_flags, value=value, linesB4=lines_b4, charsB4=chars_b4)
			content = value + content[end:]
			match = re.search(key, content)

	def _updateFlagSet(self, content, flagDict, value, linesB4, charsB4):
		newFlagDict = {}
		for line_number, (character_number, storedMatch) in flagDict.iteritems():
			if linesB4 < line_number or (linesB4 == flag.line_number and charsB4 < flag.char_number):
				line_number += value.count("\n")
				if linesB4 == line_number:
					pre_after = len(content) - content.rfind("\n")
					post_after = len(value) - value.rfind("\n")
					character_number = character_number - pre_after + post_after
			newFlagDict[line_number] = character_number, storedMatch
		return newFlagDict