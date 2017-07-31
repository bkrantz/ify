import common
import re
from decimal import *
from Fly import Fly
import os

def help():
	output("This is the help menu")

def version():
	output("Pretifly v%s" % (current_version,))

def process(**kwargs):
	if 'actions' not in kwargs:
		common.error("No action specified")
	elif kwargs['actions'] in ["-h", "-v"]:
		if kwargs['actions'] == "-h":
			help()
		elif kwargs['actions'] == "-v":
			version()
	elif kwargs['actions'] in ["-m", "-p"]:
		module = None
		format = None
		if ((not 'format' in kwargs or kwargs['format'] == None) and
			(not 'input_file' in kwargs or kwargs['input_file'] == None)):
			common.error("Unable to determine data format")
		elif ((not 'format' in kwargs or kwargs['format'] == None) and
			('formats' in kwargs and not kwargs['formats'] == None)):

			extension = common.getFileExtension(kwargs['input_file'])
			format = None
			if extension:
				for cur_format in kwargs['formats']:
					if kwargs['formats'][cur_format]['extension'] == extension:
						format = cur_format
			if not format:
				common.error("Unable to determine format from filename")
		elif 'format' in kwargs and kwargs['format'] == None:
			format = kwargs['format']
		else:
			common.error("Unable to determine data format")

		if not 'formats' in kwargs:
			common.error("addon formats are not provided")
		else:
			try:
				fly = kwargs['formats'][format]['module'].getInstance(kwargs['input_file'], kwargs['actions'], kwargs['tab'])
			except Exception as e:
				print e
				common.error("Unable to create format object instance")

			fly.process()

			if not 'output_file' in kwargs or kwargs['output_file'] == None:
				common.output(str(fly))
			else:
				if "gzip" in kwargs and kwargs['gzip']:
					kwargs['output_file'] = common.toGZipFile(filename=kwargs['output_file'], message=str(fly))
					fly._content_size = os.path.getsize(kwargs['output_file'])
				else:
					common.toFile(filename=kwargs['output_file'], message=str(fly))

			if 'verbose' in kwargs and kwargs['verbose']:
				common.output("Initial Size : %s bytes" % (fly._initial_size,))
				common.output("Total Input Size : %s bytes" % (fly._total_input_size,))
				common.output("New Size: %s bytes" % (fly._content_size,))
				percent = Decimal(fly._total_input_size - fly._content_size) / Decimal(fly._total_input_size) * 100
				common.output("Savings: %2.2f%%" % (percent,))
	else:
		common.error("Unknown action")