from Exceptions.InvalidContentException import InvalidContentException
import common

class Fly():

	def __init__(self, input_file, actions, tab):
		self._input_file = input_file
		self._minified_content = None
		self._pretty_content = None
		self._actions = actions
		self._tab = tab
		self._initial_size = 0
		self._total_input_size = self._initial_size

	def process(self, ):
		if not self.isValid():
			raise InvalidContentException()

		if self._actions == "-m":
			self._minify()
			self._content = self._minified_content
		elif self._actions == "-p":
			self._minify()
			self._pretify()
			self._content = self._pretty_content

		self._content_size = len(self._content)

	def _isValid(self, ):
		return True

	def _minify(self, ):
		self._minified_content = common.file_get_contents(self._input_file)
		self._initial_size = len(raw_content)
		self._total_input_size = self._initial_size

	def _pretify(self, ):
		self._pretty_content = self._minified_content

	def __str__(self, ):
		return self._content
