Ify = None
Fortify = None
Minify = None
Notify = None

def import_Ify():
	global Ify
	if not Ify:
		Ify = __import__("src.utils.Imports", "Ify")
