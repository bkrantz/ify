#!/usr/bin/python

#imports
import sys, os, re
from more import *

try:

	class flagged(object):
		def __init__(self, relative_path, line_number, char_number, match, yellow=False, red=False, *args, **kwargs):
			self.relative_path = relative_path
			self.line_number = line_number
			self.char_number = char_number
			self.match = match
			self.red = red
			self.yellow = yellow

		def tostring(self):
			return "%s:%d:%d:\"%s\"" % (self.relative_path, self.line_number, self.char_number, self.match, )

	class file_examiner():

		#regex as key, target group as value
		red_flag_regexes = {
			r"[\t\vf ]*(except[\t\vf ]*[\:])": 1,
			r"[^\n]*for[\t\vf ]+[^\s]+[\t\vf ]+in[\t\vf ]+([^\s]*\.(keys|values)\(\))": 1,
			r"[^\n]*for[\t\vf ]+[^\s]+,[\t\vf ]*[^\s]+[\t\vf ]+in[\t\vf ]+([^\s]*\.items\(\))": 1,
			r"(?<!with)[\t\vf ]+(open\()": 1,
			r"[\s](dict.fromkeys\()", 1
		}

		#regex as key, target group as value
		yellow_flag_regexes = {
			"(open\()": 1,
			"(\.(items|keys|values|popitem)\(\))": 1
		}

		comments = [
			r"(\"|\')\1\1(.|\s)*?\1\1\1",
			r"#[^\n]*"
		]

		strings = [
			r"([\"\'])[\x00-\x7F]*?(?<!\\)(\\\\)*\1"
		]

		def __init__(self, root_path, relative_path, *args, **kwargs):
			self.extracted = {}
			self.root_path = root_path
			self.relative_path = relative_path
			self.flagged = []
			self.content = read_file(root_path)
			self.process()

		def process(self):
			extract_regexes = []
			extract_regexes.extend(self.comments)
			extract_regexes.extend(self.strings)
			content = self.extract(self.content, extract_regexes)
			content = self.identify_flags(content, file_examiner.red_flag_regexes)
			content = self.identify_flags(content, file_examiner.yellow_flag_regexes)
			content = self.repopulate(content)
			
		def identify_flags(self, content, regex_dict):
			processed_content = ""
			regex, regexes = self.find_first_regex(content, list(regex_dict.keys()))
			while regex:
				match = re.search(regex, content)
				start, end = match.start(), match.end()
				processed_content += content[:start]
				group, content = content[start:end], content[end:]
				line_number = processed_content.count("\n")+1
				char_number = len(processed_content) - processed_content.rfind("\n")
				processed_content += group
				group = match.group(regex_dict[regex])
				if not self.flag_exists(line_number):
					yellow, red = False, False
					if regex in file_examiner.red_flag_regexes:
						red = True
					elif regex in file_examiner.yellow_flag_regexes:
						yellow = True
					self.flagged.append(flagged(self.relative_path, line_number, char_number, group, yellow=yellow, red=red))
				regex, regexes = self.find_first_regex(content, regexes)
			return processed_content + content

		def repopulate(self, content):
			processed_content = ""
			regex = r"#\([\d]+\)#"
			match = re.search(regex, content)
			while match:
				start, end = match.start(), match.end()
				replacement = self.extracted.pop(content[start:end])
				temp = processed_content + content[:end]
				processed_content += content[:start]
				lines_b4 = temp.count("\n")+1
				chars_b4 = len(temp) - temp.rfind("\n")
				for flag in self.flagged:
					if lines_b4 < flag.line_number or (lines_b4 == flag.line_number and chars_b4 < flag.char_number):
						flag.line_number += replacement.count("\n")
						if lines_b4 == flag.line_number:
							pre_after = len(processed_content) - processed_content.rfind("\n")
							post_after = len(replacement) - replacement.rfind("\n")
							flag.char_number = flag.char_number - pre_after + post_after
				content = replacement + content[end:]
				match = re.search(regex, content)
			return processed_content + content

		def flag_exists(self, line_number):
			for flag in self.flagged:
				if flag.line_number == line_number:
					return True
			return False

		def get_flags(self, ):
			red = []
			yellow = []
			for flag in self.flagged:
				if flag.red:
					red.append(flag.tostring())
				if flag.yellow:
					yellow.append(flag.tostring())
			return yellow, red

		def extract(self, content, regex_list):
			processed_content = ""
			regex, regexes = self.find_first_regex(content, regex_list)
			while regex:
				match = re.search(regex, content)
				sub = "#({})#".format(str(len(self.extracted)))
				start, end = match.start(), match.end()
				self.extracted[sub] = content[start:end]
				processed_content += content[:start] + sub
				content = content[end:]
				regex, regexes = self.find_first_regex(content, regexes)
			return processed_content + content

		def find_first_regex(self, content, regexes):
			found = []
			first_position, first_regex = len(content), None
			for regex in regexes:
				match = re.search(regex, content)
				if match:
					found.append(regex)
					start = match.start()
					if start < first_position and start >= 0:
						first_position = start
						first_regex = regex
			return first_regex, found

	def crawl_files(root_path):
		red = []
		yellow = []
		cnt = 0
		for root, dirs, files in os.walk(root_path):
			if not re.match(".*\/$", root):
				root += "/"
			relative_root = root[len(root_path)+1:]
			for file in files:
				full_path = "%s%s" % (root, file, )
				relative_path = "%s%s" % (relative_root, file, )
				name, ext = os.path.splitext(full_path)
				if ext == ".py":
					#print "Examining '%s'" % relative_path
					flagger = file_examiner(full_path, relative_path)
					new_yellow, new_red = flagger.get_flags()
					red.extend(new_red)
					yellow.extend(new_yellow)
		return yellow, red

	red = []
	yellow = []
	deny = False
	if len(sys.argv) > 1:
		if os.path.isdir(sys.argv[1]):
			yellow, red = crawl_files(os.path.realpath(sys.argv[1]))
		elif os.path.isfile(sys.argv[1]):
			flagger = file_examiner(sys.argv[1], sys.argv[1])
			yellow, red = flagger.get_flags()
	else:
		raise Exception

	if yellow:
		print "\n#########################################################"
		print "# Yellow Flags Detected: These may be areas of interest #"
		print "#########################################################\n"

		for flag in yellow:
			print flag
	if red:
		print "\n#################################################################"
		print "# Red Flags Detected: Please address these issues and try again #"
		print "#################################################################\n"
		for flag in red:
			print flag
		deny = True

	if deny:
		raise UnaddressedFlagException

except Exception as e:
	sys.exit(1)