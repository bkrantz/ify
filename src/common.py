import sys
import re
import urllib2
import gzip

def array_diff(list1, list2):
    return [item for item in list1 if item not in list2] + [item for item in list2 if item not in list1]

def getFile(filename,):
	with open(filename, "r") as target:
	   content = target.read()
	return content

def log(message):
	output(message)

def info(message):
    log("%s%s" % ("INFO: ", message, ))

def warn(message):
    log("%s%s" % ("WARN: ", message, ))

def error(message):
	log("%s%s" % ("ERROR: ", message, ))
	sys.exit()

def output(message):
	print message

# modes = w, a, r, r+
def toFile(filename, message, mode="w"):
	with open(filename, mode) as target:
	   target.write(message)

# modes = w, a, r, r+
def toGZipFile(filename, message, mode="wb"):
    regex1 = ".*\.$"
    regex2 = ".*\.gz$"
    if re.match(regex1, filename):
        filename += "gz"
    elif not re.match(regex2, filename):
        filename += ".gz"
    target = gzip.open(filename, mode)
    target.write(message)
    target.close()
    return filename

def regexpos(source, sub_regex, test=False):
	pos = re.search(sub_regex, source)
	return pos.start(0) if re.findall(sub_regex, source) and pos else -1

def ltrim(the_str, char_regex="\s"):
    leading_whitespace_regex = "^(%s*)" % (char_regex, )
    return re.sub(leading_whitespace_regex, "", the_str)

def rtrim(the_str, char_regex="\s"):
    trailing_whitespace_regex = "(%s*)$" % (char_regex, )
    return re.sub(trailing_whitespace_regex, "", the_str)

def trim(the_str, char_regex="\s"):
    return rtrim(ltrim(the_str, char_regex), char_regex)

def isset(variable):
    try:
        variable
        return True
    except:
       return False

def mb_substr(s,start,length=None,encoding="UTF-8") :
    u_s = s.decode(encoding)
    return (u_s[start:(start+length)] if length else u_s[start:]).encode(encoding)

def file_get_contents(filename, use_include_path = 0, context = None, offset = -1, maxlen = -1):
    if (filename.find('://') > 0):
        ret = urllib2.urlopen(filename).read()
        if (offset > 0):
            ret = ret[offset:]
        if (maxlen > 0):
            ret = ret[:maxlen]
        return ret
    else:
        fp = open(filename,'rb')
        try:
            if (offset > 0):
                fp.seek(offset)
            ret = fp.read(maxlen)
            return ret
        finally:
            fp.close( )

def file_get_contents_as_line_array(filename):
    content = file_get_contents(filename)
    lines = []
    line_regex = r"([^\n]*)\n"
    matches = re.findall(line_regex, content)
    if matches:
        for match in matches:
            if match[0]:
                lines.append(matches[0])

    return lines

def getFileExtension(path, ):
    extension_regex = "([.]*[\.](?P<extension>[^.]*))$"
    matches = re.findall(extension_regex, path)
    return matches[0][1] if matches else None

