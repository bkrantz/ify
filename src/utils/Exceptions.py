
class BaseIfyException(Exception):
	def __init__(self, message=None):
		self.message = message

	def __str__(self):
		return self.message

class IOException(BasePretifyException):
	pass

class FileNotFoundException(IOException):
	pass

class FileImportException(IOException):
	pass

class InvalidContentException(BaseIfyException):
	pass