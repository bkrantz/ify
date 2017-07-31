from Exceptions.IOException import IOException
import os
import common
import re

class Minify():
    _total_input_size = 0

    def __init__(self, data=None, **kwargs):
        self._data = {}
        self._patterns = {}
        self._extracted = {}
        self._minified_size = 0
        if data:
            cur_data = []
            cur_data.append(data)
            for key in kwargs:
                cur_data.append(kwargs[key])
            self._add(cur_data)

    # data = String[]...
    # commonly size = 1
    def _add(self, data=None):
        if data:
            for cur_data in data:
                if isinstance(cur_data, list):
                    self._add(cur_data)
                else:
                    value = self._load(cur_data)
                    key = value if value == cur_data else len(self._data)
                    value = value.replace("\r\n", "\n")
                    value = value.replace("\r", "\n")
                    self._data[key] = value
        return self

    # path = String
    def minify(self, path=None):
        content = self.execute(path)
        #if not path == None:
        #    self._save(content, path)
        #self._minified_size = len(content)
        return content

    def execute(self, path=None):
        pass

    def _load(self, data):
        if self._canImportFile(data):
            data = common.file_get_contents(data)
            if data[0:3] in ["xef", "xbb", "xbf"]:
                data = data[3:]
        Minify._total_input_size += len(data)
        return data

    def _save(self, content, path):
        handler = self._openFileForWriting(path)
        self._writeToFile(handler, content, path)
        handler.close()

    def _registerPattern(self, pattern, replacement=''):
        #pattern+='S'
        self._patterns[pattern] = replacement

    def _replace(self, content):
        processed = '';
        positions = {}
        for pos, pattern in enumerate(self._patterns):
            positions[pos] = -1
        matches = {}
        while content:
            for pos, pattern in enumerate(self._patterns):
                if positions[pos] >= 0:
                    pass
                else:
                    match = re.findall(pattern, content)
                    if match:
                        matches[pos] = match
                        test = common.regexpos(content, pattern)
                        positions[pos] = test
                    else:
                        matches.pop(pos, None)
                        positions[pos] = len(content)
            if not matches:
                processed += content
                content = None
            else:
                discardLength = len(content)
                firstPattern = ''
                for pos, pattern in enumerate(self._patterns):
                    if positions[pos] < discardLength and positions[pos] >= 0:
                        discardLength = positions[pos]
                        firstPattern = pattern
                        firstPatternPos = pos

                match = matches[firstPatternPos][0]
                match = match[0] if not isinstance(match, str) else match

                replacement = self._replacePattern(firstPattern, self._patterns[firstPattern], content)
                content = content[discardLength:]

                unmatched = content[len(match):]
                processed += replacement[:len(replacement)-len(unmatched)]
                content = unmatched
                for pos in positions:
                    positions[pos] -= discardLength + len(match)
        return processed

    def _replacePattern(self, pattern, replacement, content):
        if callable(replacement):
            match = re.findall(pattern, content)
            if match:
                return re.sub(pattern, replacement(match[0]), content, 1)
        else:
            return re.sub(pattern, replacement, content, 1)

        return content

    def _extractStrings(self, chars='\'"'):
        callback = self._extract_callback
        #pattern = "(([%s])(.*?(?<!\\\\)(\\\\\\\\)*+)\\2)" % (chars, )
        pattern = r"(([%s])(.*?(?<!\\)(\\\\)*)\2)" % (chars, )
        self._registerPattern(pattern, callback)

    def _extract_callback(self, match):
        if not len(match[2]):
            return match[0]
        count = len(self._extracted)
        placeholder = "%s%s%s" % (match[1], str(count), match[1], )
        self._extracted[placeholder] = "%s%s%s" % (match[1], match[2], match[1], )
        return placeholder

    def _restoreExtractedData(self, content):
        if not self._extracted:
            return content
        for key in self._extracted:
            content = content.replace(key, self._extracted[key])
        self._extracted = {}
        return content

    def _canImportFile(self, path):
        len_check = len(path) < 260
        is_file_check = os.path.isfile(path)
        readable_check = True
        try:
            with open(path) as tempFile:
                pass
        except:
            readable_check = False
        return (len_check and is_file_check and readable_check)

    def _openFileForWriting(self, path):
        try:
            handler = open(path, "w")
        except:
            raise IOException("The file '%s' could not be opened for writing. Check if Python has enough permissions." % (path,))
        return handler

    def _writeToFile(self, handler, content, path=''):
        try:
            handler.write(content)
        except:
            raise IOException("The file '%s' could not be opened for writing. Check if Python has enough permissions." % (path,))