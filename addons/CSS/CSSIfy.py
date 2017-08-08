from src import Ify

class CSSIfy(Ify):

	extensions = [
		"css"
	]

	_commentRegexes = [
		r'(\s*\/\*(.|\s)*?\*\/\s*)'
	]