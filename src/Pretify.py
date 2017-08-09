#add spacing

class Pretify(IfyProcessor, IfyPatternMixin):

	_spaces_per_tab = 4

	_indent_regexes = []
	_reverese_indent_regexes = []

	_current_indent_number = 0
	
	def 